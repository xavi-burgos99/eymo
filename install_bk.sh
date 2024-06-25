#!/bin/bash

install_eymo() {
	if [ "$EUID" -ne 0 ]; then
		printf "\033[0;33m[WARNING]\033[0m This script must be run as root.\n"
		sudo "$0" "$@"
		exit $?
	fi
	BOOT_PATH="/boot/firmware"
	if [ ! -d $BOOT_PATH ]; then
		BOOT_PATH="/boot"
	fi

	CURRENT_USER=$(logname)

	if [ -d /home/"$CURRENT_USER"/eymo ]; then
    printf "\033[0;31m[ERROR]\033[0m The eymo directory already exists.\n"
    exit 1
  fi

  if [ ! -f /home/"$CURRENT_USER"/eymo.zip ]; then
    printf "\033[0;31m[ERROR]\033[0m The eymo.zip file does not exist.\n"
    exit 1
  fi

	clear
	print "Before starting the installation, you need to set the mDNS hostname. This hostname will be used to access the web server (e.g., http://eymo.local)."
	read -p "Enter the mDNS hostname (default: eymo): " MDNS_HOSTNAME
	MDNS_HOSTNAME=${MDNS_HOSTNAME:-eymo}
	while [ ${#MDNS_HOSTNAME} -gt 63 ] || [[ ! "$MDNS_HOSTNAME" =~ ^[a-zA-Z0-9-]*$ ]]; do
		printf "\033[0;31m[ERROR]\033[0m The mDNS hostname must be alphanumeric and have a maximum length of 63 characters.\n"
		read -p "Enter the mDNS hostname (default: eymo): " MDNS_HOSTNAME
		MDNS_HOSTNAME=${MDNS_HOSTNAME:-eymo}
	done

	clear
	read -p "Do you want to create an access point? [Y/n] " -n 1 -r
	echo
	if [[ $REPLY =~ ^[Yy]$ ]]; then
		read -p "Enter the SSID (default: EYMO): " SSID
		SSID=${SSID:-EYMO}
		while [ ${#SSID} -gt 32 ] || [[ ! "$SSID" =~ ^[a-zA-Z0-9]*$ ]]; do
			printf "\033[0;31m[ERROR]\033[0m The SSID must be alphanumeric and have a maximum length of 32 characters.\n"
			read -p "Enter the SSID (default: EYMO): " SSID
			SSID=${SSID:-EYMO}
		done
		read -p "Enter the password (no password by default): " PASSWORD
		while [ ${#PASSWORD} -lt 8 ] || [ ${#PASSWORD} -gt 63 ] && [ -n "$PASSWORD" ]; do
			printf "\033[0;31m[ERROR]\033[0m The password must have a length between 8 and 63 characters.\n"
			read -p "Enter the password (no password by default): " PASSWORD
		done
		read -p "Do you want to block the access to the Internet? [Y/n] " -n 1 -r
		echo
		if [[ $REPLY =~ ^[Yy]$ ]]; then
			INTERNET_ACCESS=false
		else
			INTERNET_ACCESS=true
		fi
	fi

	clear

	unzip /home/"$CURRENT_USER"/eymo.zip -d /home/"$CURRENT_USER"/eymo

	clear
	printf "The zip file has been extracted successfully.\n"
	read -p "Do you want to remove the eymo.zip file? [Y/n] " -n 1 -r
	echo
	if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -f /home/"$CURRENT_USER"/eymo.zip
  fi

	if [ -f /etc/hostname ]; then
		hostnamectl set-hostname "$MDNS_HOSTNAME"
		sed -i "s/raspberrypi/$MDNS_HOSTNAME/" /etc/hosts
	fi

	apt-get update
	apt-get upgrade -y

	if [ -f /etc/hostapd/hostapd.conf ]; then
		printf "\n\033[0;33m[WARNING]\033[0m The access point is already created.\n"
	else

		if [ -n "$SSID" ]; then

			rfkill unblock wlan
			apt-get install hostapd dnsmasq -y

			echo iptables-persistent iptables-persistent/autosave_v4 boolean true | debconf-set-selections
			echo iptables-persistent iptables-persistent/autosave_v6 boolean true | debconf-set-selections
			apt-get install iptables-persistent -y

			systemctl stop hostapd
			systemctl stop dnsmasq

			echo -e "\ninterface wlan0\nstatic ip_address=192.168.4.10/24\nnohook wpa_supplicant" | tee -a /etc/dhcpcd.conf

			service dhcpcd restart

			echo -e "interface=wlan0\ndhcp-range=192.168.4.11,192.168.4.30,255.255.255.0,24h" | tee /etc/dnsmasq.conf

			echo -e "interface=wlan0\ndriver=nl80211\nhw_mode=g\nchannel=7\nwmm_enabled=0\nmacaddr_acl=0\nauth_algs=1\nignore_broadcast_ssid=0\nssid=$SSID" | tee /etc/hostapd/hostapd.conf
			if [ -n "$PASSWORD" ]; then
				echo -e "wpa=2\nwpa_passphrase=$PASSWORD\nwpa_key_mgmt=WPA-PSK\nwpa_pairwise=TKIP\nrsn_pairwise=CCMP" | tee -a /etc/hostapd/hostapd.conf
			else
				echo -e "ap_isolate=1" | tee -a /etc/hostapd/hostapd.conf
			fi
			echo 'DAEMON_CONF="/etc/hostapd/hostapd.conf"' | tee -a /etc/default/hostapd

			sed -i 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/' /etc/sysctl.conf

			iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
			sh -c "iptables-save > /etc/iptables.ipv4.nat"

			if [ "$INTERNET_ACCESS" = false ]; then
				iptables -I FORWARD -o eth0 -d 0.0.0.0/0 -j DROP
				iptables -I FORWARD -i eth0 -s 192.168.4.0/24 -j ACCEPT
				iptables -I FORWARD -i wlan0 -d 192.168.4.0/24 -j ACCEPT
				
				sh -c "iptables-save > /etc/iptables.ipv4.nat"
			fi

			iptables-save > /etc/iptables.ipv4.nat
			ip6tables-save > /etc/iptables.ipv6.nat

			systemctl unmask hostapd

			systemctl start hostapd
			systemctl start dnsmasq

			echo -e "#!/bin/sh\niptables-restore < /etc/iptables.ipv4.nat\nexit 0" | tee /etc/network/if-pre-up.d/iptables
		fi
	
	fi


	# Install Python3

	if [ -x "$(command -v python3)" ]; then
		printf "\n\033[0;33m[WARNING]\033[0m Python3 is already installed.\n"
	else
		apt-get install python3 python3-pip python3-rpi.gpio python3-opencv python3-virtualenv -y
	fi


	# Create a virtual environment

	if [ -d /home/"$CURRENT_USER"/eymo/venv ]; then
    printf "\n\033[0;33m[WARNING]\033[0m The virtual environment is already created.\n"
  else
    sudo -u eymo virtualenv /home/"$CURRENT_USER"/eymo/venv
  fi

  source /home/"$CURRENT_USER"/eymo/venv/bin/activate
  pip3 install -r /home/"$CURRENT_USER"/eymo/core/requirements.txt


	# Install the eymo access service

	if [ -f /etc/systemd/system/eymo_network.service ]; then
		printf "\n\033[0;33m[WARNING]\033[0m The eymo access service is already installed.\n"
	else
	  echo -e "[Unit]\nDescription=Enable the access point automatically\nAfter=network.target\n\n[Service]\nExecStart=/home/$CURRENT_USER/eymo/venv/bin/python3 /home/$CURRENT_USER/eymo/core/network.py\nWorkingDirectory=/home/$CURRENT_USER/eymo/core/\nStandardOutput=inherit\nStandardError=inherit\nRestart=always\nUser=$CURRENT_USER\n\n[Install]\nWantedBy=multi-user.target" | tee /etc/systemd/system/eymo_network.service
	fi

	systemctl enable eymo_network
	systemctl start eymo_network


	# Install the eymo main service

	if [ -f /etc/systemd/system/eymo.service ]; then
    printf "\n\033[0;33m[WARNING]\033[0m The eymo main service is already installed.\n"
  else
    echo -e "[Unit]\nDescription=Run the EYMO main program\nAfter=network.target\n\n[Service]\nExecStart=/home/$CURRENT_USER/eymo/venv/bin/python3 /home/$CURRENT_USER/eymo/core/main.py\nWorkingDirectory=/home/$CURRENT_USER/eymo/core/\nStandardOutput=inherit\nStandardError=inherit\nRestart=always\nUser=$CURRENT_USER\n\n[Install]\nWantedBy=multi-user.target" | tee /etc/systemd/system/eymo.service
  fi

  systemctl enable eymo
  systemctl start eymo


  # Finish the installation

	read -p "EYMO has been installed successfully. Do you want to reboot now? [Y/n] " -n 1 -r
	echo
	if [[ $REPLY =~ ^[Yy]$ ]]; then
		reboot
	fi
}

uninstall_eymo() {
	if [ "$EUID" -ne 0 ]; then
		printf "\033[0;33m[WARNING]\033[0m This script must be run as root.\n"
		sudo "$0" "$@"
		exit $?
	fi
	BOOT_PATH="/boot/firmware"
	if [ ! -d $BOOT_PATH ]; then
		BOOT_PATH="/boot"
	fi
	if [ ! -f $BOOT_PATH/config.txt ]; then
		printf "\033[0;31m[ERROR]\033[0m This script must be run on a Raspberry Pi.\n"
		exit 1
	fi
	read -p "Do you want to uninstall EYMO? [Y/n] " -n 1 -r
	echo
	if [[ $REPLY =~ ^[Yy]$ ]]; then

		dpkg --configure -a

		# Uninstall Python3, and delete the services

    systemctl disable eymo
    systemctl stop eymo
    rm -f /etc/systemd/system/eymo.service

		systemctl disable eymo_network
		systemctl stop eymo_network
		rm -f /etc/systemd/system/eymo_network.service

		apt-get remove --purge python3 python3-pip python3-rpi.gpio python3-opencv -y

		apt-get autoremove -y
    apt-get clean


		# Remove the eymo directory

	  rm -rf /home/"$CURRENT_USER"/eymo


		# Uninstall the access point, and delete the configuration

		systemctl stop hostapd
    systemctl stop dnsmasq
    apt-get remove --purge hostapd dnsmasq -y
    apt-get remove --purge iptables-persistent -y
    rm -f /etc/dhcpcd.conf
    rm -f /etc/dnsmasq.conf
    rm -f /etc/hostapd/hostapd.conf
    rm -f /etc/default/hostapd
    rm -f /etc/network/if-pre-up.d/iptables
    iptables -F
    iptables -t nat -F
    ip6tables -F

		apt autoremove -y

		read -p "EYMO has been uninstalled successfully. Do you want to reboot now? [Y/n] " -n 1 -r
		echo
		if [[ $REPLY =~ ^[Yy]$ ]]; then
			reboot
		fi
	fi
}

access_point() {
	if [ "$#" -lt 1 ] || [ "$#" -gt 3 ]; then

		printf "\033[0;31m[ERROR]\033[0m Invalid number of arguments.\n"
		printf "Usage: eymo access_point <action> [value]\n"
		exit 1
	fi
	if [ "$EUID" -ne 0 ]; then
		printf "\033[0;33m[WARNING]\033[0m This script must be run as root.\n"
		sudo "$0" "$@"
		exit $?
	fi
	BOOT_PATH="/boot/firmware"
	if [ ! -d $BOOT_PATH ]; then
		BOOT_PATH="/boot"
	fi
	if [ ! -f $BOOT_PATH/config.txt ]; then
		printf "\033[0;31m[ERROR]\033[0m This script must be run on a Raspberry Pi.\n"
		exit 1
	fi
	case $2 in
		enable)
			if [ "$#" -ne 2 ]; then
				printf "\033[0;31m[ERROR]\033[0m Invalid number of arguments.\n"
				printf "Usage: eymo access_point enable\n"
				exit 1
			fi
			if [ -f /etc/hostapd/hostapd.conf ]; then
				if systemctl is-active --quiet hostapd; then
					printf "\033[0;33m[WARNING]\033[0m The access point is already enabled.\n"
					exit 1
				fi
				systemctl unmask hostapd
				systemctl start hostapd
				systemctl restart dnsmasq
				printf "\033[0;32m[SUCCESS]\033[0m The access point has been enabled successfully.\n"
			else
				read -p "Enter the SSID (default: EYMO): " SSID
				SSID=${SSID:-EYMO}
				while [ ${#SSID} -gt 32 ] || [[ ! "$SSID" =~ ^[a-zA-Z0-9]*$ ]]; do
					printf "\033[0;31m[ERROR]\033[0m The SSID must be alphanumeric and have a maximum length of 32 characters.\n"
					read -p "Enter the SSID (default: EYMO): " SSID
					SSID=${SSID:-EYMO}
				done
				read -p "Enter the password (no password by default): " PASSWORD
				while [ ${#PASSWORD} -lt 8 ] || [ ${#PASSWORD} -gt 63 ] && [ -n "$PASSWORD" ]; do
					printf "\033[0;31m[ERROR]\033[0m The password must have a length between 8 and 63 characters.\n"
					read -p "Enter the password (no password by default): " PASSWORD
				done
				read -p "Do you want to block the access to the Internet? [Y/n] " -n 1 -r
				echo
				if [[ $REPLY =~ ^[Yy]$ ]]; then
					INTERNET_ACCESS=false
				else
					INTERNET_ACCESS=true
				fi

				rfkill unblock wlan
				apt-get install hostapd dnsmasq -y

				echo iptables-persistent iptables-persistent/autosave_v4 boolean true | debconf-set-selections
        echo iptables-persistent iptables-persistent/autosave_v6 boolean true | debconf-set-selections
        apt-get install iptables-persistent -y

				systemctl stop hostapd
				systemctl stop dnsmasq

				echo -e "\ninterface wlan0\nstatic ip_address=192.168.4.10/24\nnohook wpa_supplicant" | tee -a /etc/dhcpcd.conf

				service dhcpcd restart

				echo -e "interface=wlan0\ndhcp-range=192.168.4.11,192.168.4.30,255.255.255.0,24h" | tee /etc/dnsmasq.conf

				echo -e "interface=wlan0\ndriver=nl80211\nhw_mode=g\nchannel=7\nwmm_enabled=0\nmacaddr_acl=0\nauth_algs=1\nignore_broadcast_ssid=0\nap_isolate=1\nssid=$SSID" | tee /etc/hostapd/hostapd.conf
				if [ -n "$PASSWORD" ]; then
					echo -e "wpa=2\nwpa_passphrase=$PASSWORD\nwpa_key_mgmt=WPA-PSK\nwpa_pairwise=TKIP\nrsn_pairwise=CCMP" | tee -a /etc/hostapd/hostapd.conf
				fi
				echo 'DAEMON_CONF="/etc/hostapd/hostapd.conf"' | tee -a /etc/default/hostapd

				sed -i 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/' /etc/sysctl.conf

				iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
				sh -c "iptables-save > /etc/iptables.ipv4.nat"

				if [ "$INTERNET_ACCESS" = false ]; then
					iptables -I FORWARD -o eth0 -d 0.0.0.0/0 -j DROP
					iptables -I FORWARD -i eth0 -s 192.168.4.0/24 -j ACCEPT
					iptables -I FORWARD -i wlan0 -d 192.168.4.0/24 -j ACCEPT
					
					sh -c "iptables-save > /etc/iptables.ipv4.nat"
				fi

				iptables-save > /etc/iptables.ipv4.nat
				ip6tables-save > /etc/iptables.ipv6.nat

				systemctl unmask hostapd
				systemctl start hostapd
				systemctl start dnsmasq

				echo -e "#!/bin/sh\niptables-restore < /etc/iptables.ipv4.nat\nexit 0" | tee /etc/network/if-pre-up.d/iptables

				printf "\033[0;32m[SUCCESS]\033[0m The access point has been created successfully.\n"
			fi
			;;
		disable)
			if [ "$#" -ne 2 ]; then
				printf "\033[0;31m[ERROR]\033[0m Invalid number of arguments.\n"
				printf "Usage: eymo access_point disable\n"
				exit 1
			fi
			if [ -f /etc/hostapd/hostapd.conf ]; then
				if systemctl is-active --quiet hostapd; then
					systemctl stop hostapd
					systemctl disable hostapd
					printf "\033[0;32m[SUCCESS]\033[0m The access point has been disabled successfully.\n"
				else
					printf "\033[0;33m[WARNING]\033[0m The access point is already disabled.\n"
				fi
			else
				printf "\033[0;31m[ERROR]\033[0m The access point has not been created.\n"
				printf "Use \"eymo access_point enable\" to create an access point.\n"
			fi
			;;
		ssid)
			if [ "$#" -ne 2 ]; then
				printf "\033[0;31m[ERROR]\033[0m Invalid number of arguments.\n"
				printf "Usage: eymo access_point ssid\n"
				exit 1
			fi
			if [ -f /etc/hostapd/hostapd.conf ]; then
				read -p "Changing the SSID requires to disable the access point. Do you want to continue? [Y/n] " -n 1 -r
				echo
				if [[ ! $REPLY =~ ^[Yy]$ ]]; then
					printf "\033[0;33m[WARNING]\033[0m The SSID has not been changed.\n"
					exit 1
				fi
				read -p "Enter the new SSID: " SSID
				while [ ${#SSID} -gt 32 ] || [[ ! "$SSID" =~ ^[a-zA-Z0-9]*$ ]]; do
					printf "\033[0;31m[ERROR]\033[0m The SSID must be alphanumeric and have a maximum length of 32 characters.\n"
					read -p "Enter the new SSID: " SSID
				done
				printf "\033[0;33m[WARNING]\033[0m If you are connected to the access point, you will be disconnected.\n"
				systemctl stop hostapd
				systemctl disable hostapd
				sed -i "s/ssid=.*/ssid=$SSID/" /etc/hostapd/hostapd.conf
				systemctl start hostapd
				printf "\033[0;32m[SUCCESS]\033[0m The SSID has been changed successfully.\n"
			else
				printf "\033[0;31m[ERROR]\033[0m The access point has not been created.\n"
				printf "Use \"eymo access_point enable\" to create an access point.\n"
			fi
			;;
		password)
			if [ "$#" -ne 2 ]; then
				printf "\033[0;31m[ERROR]\033[0m Invalid number of arguments.\n"
				printf "Usage: eymo access_point password\n"
				exit 1
			fi
			if [ -f /etc/hostapd/hostapd.conf ]; then
				read -p "Changing the password requires to disable the access point. Do you want to continue? [Y/n] " -n 1 -r
				echo
				if [[ ! $REPLY =~ ^[Yy]$ ]]; then
					printf "\033[0;33m[WARNING]\033[0m The password has not been changed.\n"
					exit 1
				fi
				read -p "Enter the new password (no password by default): " PASSWORD
				while [ ${#PASSWORD} -lt 8 ] || [ ${#PASSWORD} -gt 63 ] && [ -n "$PASSWORD" ]; do
					printf "\033[0;31m[ERROR]\033[0m The password must have a length between 8 and 63 characters.\n"
					read -p "Enter the new password (no password by default): " PASSWORD
				done
				printf "\033[0;33m[WARNING]\033[0m If you are connected to the access point, you will be disconnected.\n"
				systemctl stop hostapd
				systemctl disable hostapd
				if [ -z "$PASSWORD" ]; then
					if grep -q "wpa_passphrase" /etc/hostapd/hostapd.conf; then
						sed -i '/wpa=2/d' /etc/hostapd/hostapd.conf
						sed -i '/wpa_passphrase/d' /etc/hostapd/hostapd.conf
						sed -i '/wpa_key_mgmt/d' /etc/hostapd/hostapd.conf
						sed -i '/wpa_pairwise/d' /etc/hostapd/hostapd.conf
						sed -i '/rsn_pairwise/d' /etc/hostapd/hostapd.conf
						echo -e "ap_isolate=1" | tee -a /etc/hostapd/hostapd.conf
						printf "\033[0;32m[SUCCESS]\033[0m The password has been removed successfully.\n"
					else
						printf "\033[0;33m[WARNING]\033[0m The access point does not have a password.\n"
					fi
				else
					if grep -q "wpa_passphrase" /etc/hostapd/hostapd.conf; then
						sed -i "s/wpa_passphrase=.*/wpa_passphrase=$PASSWORD/" /etc/hostapd/hostapd.conf
						printf "\033[0;32m[SUCCESS]\033[0m The password has been changed successfully.\n"
					else
						sed -i '/ap_isolate/d' /etc/hostapd/hostapd.conf
						echo -e "wpa=2\nwpa_passphrase=$PASSWORD\nwpa_key_mgmt=WPA-PSK\nwpa_pairwise=TKIP\nrsn_pairwise=CCMP" | tee -a /etc/hostapd/hostapd.conf
						printf "\033[0;32m[SUCCESS]\033[0m The password has been set successfully.\n"
					fi
				fi
				systemctl start hostapd
			else
				printf "\033[0;31m[ERROR]\033[0m The access point has not been created.\n"
				printf "Use \"eymo access_point enable\" to create an access point.\n"
			fi
			read -p "The password change requires to reboot the Raspberry Pi. Do you want to reboot now? [Y/n] " -n 1 -r
			echo
			if [[ $REPLY =~ ^[Yy]$ ]]; then
				reboot
			fi
			;;
		internet)
			if [ "$#" -ne 3 ]; then
				printf "\033[0;31m[ERROR]\033[0m Invalid number of arguments.\n"
				printf "Usage: eymo access_point internet <boolean>\n"
				exit 1
			fi
			if [ -f /etc/hostapd/hostapd.conf ]; then
				if [[ ! "$3" =~ ^[Tt]rue$|^[Ff]alse$ ]]; then
					printf "\033[0;31m[ERROR]\033[0m The value must be a boolean.\n"
					exit 1
				fi
				read -p "Changing the Internet access requires to disable the access point. Do you want to continue? [Y/n] " -n 1 -r
				echo
				if [[ ! $REPLY =~ ^[Yy]$ ]]; then
					printf "\033[0;33m[WARNING]\033[0m The Internet access has not been changed.\n"
					exit 1
				fi
				printf "\033[0;33m[WARNING]\033[0m If you are connected to the access point, you will be disconnected.\n"
				systemctl stop hostapd
				systemctl disable hostapd
				if [ "$2" = true ]; then
					INTERNET_ACCESS=true
				else
					INTERNET_ACCESS=false
				fi
				if [ "$INTERNET_ACCESS" = false ]; then
					iptables -I FORWARD -o eth0 -d 0.0.0.0/0 -j DROP
					iptables -I FORWARD -i eth0 -s 192.168.4.0/24 -j ACCEPT
					iptables -I FORWARD -i wlan0 -d 192.168.4.0/24 -j ACCEPT
				else
					iptables -D FORWARD -o eth0 -d
					iptables -D FORWARD -i eth0 -s
					iptables -D FORWARD -i wlan0 -d
				fi
				sh -c "iptables-save > /etc/iptables.ipv4.nat"
				systemctl start hostapd
				printf "\033[0;32m[SUCCESS]\033[0m The Internet access has been changed successfully.\n"
			else
				printf "\033[0;31m[ERROR]\033[0m The access point has not been created.\n"
				printf "Use \"eymo access_point enable\" to create an access point.\n"
			fi
			;;
		*)
			printf "\033[0;31m[ERROR]\033[0m Invalid action.\n"
			printf "Usage: eymo access_point <enable|disable|ssid|password|internet [value]>\n"
			exit 1
			;;
	esac
}

show_help() {
	printf "Usage: eymo.sh [OPTION]\n"
	printf "Install EYMO on a Raspberry Pi.\n"
	printf "\n"
	printf "Options:\n"
	printf "  install\t\tInstall EYMO\n"
	printf "  uninstall\t\tUninstall EYMO\n"
	printf "  access_point <action> [value]\n"
	printf "    enable\t\tEnable the access point\n"
	printf "    disable\t\tDisable the access point\n"
	printf "    ssid\t\tChange the SSID\n"
	printf "    password\t\tChange the password\n"
	printf "    internet <boolean>\tChange the Internet access\n"
	printf "  help\t\tShow this help message\n"
	printf "\n"
}

case $1 in
	install)
		install_eymo "$@"
		;;
	uninstall)
		uninstall_eymo "$@"
		;;
	access_point)
		access_point "$@"
		;;
	help)
		show_help
		;;
	*)
		printf "\033[0;31m[ERROR]\033[0m Invalid option.\n"
		show_help
		exit 1
		;;
esac

exit 0
