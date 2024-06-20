#!/bin/bash

CURRENT_USER=$(logname)
CURRENT_PATH=$(pwd)
APP_PATH="/opt/eymo"

install_eymo() {
	if [ "$EUID" -ne 0 ]; then
		printf "\033[0;33m[WARNING]\033[0m This script must be run as root.\n"
		sudo "$0" "$@"
		exit $?
	fi
  if [ -d "$APP_PATH" ]; then
    printf "\033[0;31m[ERROR]\033[0m The eymo directory already exists.\n"
    exit 1
  fi
  if [ ! -f "$CURRENT_PATH/eymo_app.zip" ]; then
    printf "\033[0;31m[ERROR]\033[0m The eymo_app.zip file does not exist.\n"
    exit 1
  fi

	clear
	print "Before starting the installation, you need to set the mDNS hostname. This hostname will be used to access the app (e.g., http://eymo.local)."
	read -p "Enter the mDNS hostname (default: eymo): " MDNS_HOSTNAME
	MDNS_HOSTNAME=${MDNS_HOSTNAME:-eymo}
	while [ ${#MDNS_HOSTNAME} -gt 63 ] || [[ ! "$MDNS_HOSTNAME" =~ ^[a-zA-Z0-9-]*$ ]]; do
		printf "\033[0;31m[ERROR]\033[0m The mDNS hostname must be alphanumeric and have a maximum length of 63 characters.\n"
		read -p "Enter the mDNS hostname (default: eymo): " MDNS_HOSTNAME
		MDNS_HOSTNAME=${MDNS_HOSTNAME:-eymo}
	done

  # Update the Raspberry Pi
	apt-get update
	apt-get upgrade -y

	# Set the mDNS hostname
	if [ -f /etc/hostname ]; then
		hostnamectl set-hostname "$MDNS_HOSTNAME"

		# Update /etc/hosts with the new hostname
    if grep -q "127.0.1.1" /etc/hosts; then
        sudo sed -i "s/127.0.1.1.*/127.0.1.1\t$MDNS_HOSTNAME/" /etc/hosts
    else
        echo "127.0.1.1\t$MDNS_HOSTNAME" | sudo tee -a /etc/hosts
    fi
	fi

  # Extract the zip file
  mkdir -p $APP_PATH
	clear
	unzip -q "$CURRENT_PATH/eymo_app.zip" -d $APP_PATH
  chown -R "$CURRENT_USER":"$CURRENT_USER" $APP_PATH
  chmod -R 755 $APP_PATH

  # Install the access point
  rfkill unblock wlan
  apt-get install hostapd dnsmasq dhcpcd5 -y
  systemctl stop hostapd
  systemctl stop dnsmasq
  systemctl stop dhcpcd
  echo -e "interface=wlan0\nssid=EYMO\nchannel=7\nignore_broadcast_ssid=0\n" | tee /etc/hostapd/hostapd.conf
  sed -i '/DAEMON_CONF=/d' /etc/default/hostapd
  echo 'DAEMON_CONF="/etc/hostapd/hostapd.conf"' | tee -a /etc/default/hostapd
  mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
  echo -e "interface=wlan0\ndhcp-range=192.168.44.2,192.168.44.20,255.255.255.0,24h" | tee /etc/dnsmasq.conf
  echo -e "\ninterface wlan0\n    static ip_address=192.168.44.1/24\n    nohook wpa_supplicant" | tee -a /etc/dhcpcd.conf
  systemctl start hostapd
  systemctl start dnsmasq
  systemctl start dhcpcd

	# Install Python3 and the required packages
  apt-get install python3 python3-pip python3-rpi.gpio python3-opencv python3-virtualenv vlc portaudio19-dev flac -y

	# Create a virtual environment and install the required packages
  sudo -u $CURRENT_USER virtualenv -p python3 $APP_PATH/venv
  source $APP_PATH/venv/bin/activate
  pip3 install -r $APP_PATH/requirements.txt
  pip3 install luma.oled

  # Enable the i2c interface
  if [ -f /boot/firmware/config.txt ]; then
  	CONFIG_FILE="/boot/firmware/config.txt"
	else
		CONFIG_FILE="/boot/config.txt"
	fi
	sed -i '/dtparam=i2c_arm=on/d' $CONFIG_FILE
	echo "dtparam=i2c_arm=on" | tee -a $CONFIG_FILE

	# Install the eymo network service
  echo -e "[Unit]\nDescription=Enable the access point automatically\nAfter=network.target\n\n[Service]\nExecStart=$APP_PATH/venv/bin/python3 $APP_PATH/network.py\nWorkingDirectory=$APP_PATH/\nStandardOutput=inherit\nStandardError=inherit\nRestart=always\nUser=$CURRENT_USER\n\n[Install]\nWantedBy=multi-user.target" | tee /etc/systemd/system/eymo_network.service
	systemctl enable eymo_network
	systemctl start eymo_network

	# Install the eymo main service
  echo -e "[Unit]\nDescription=Run the EYMO main program\nAfter=network.target\n\n[Service]\nExecStart=$APP_PATH/venv/bin/python3 $APP_PATH/main.py\nWorkingDirectory=$APP_PATH/\nStandardOutput=inherit\nStandardError=inherit\nRestart=always\nUser=$CURRENT_USER\n\n[Install]\nWantedBy=multi-user.target" | tee /etc/systemd/system/eymo.service
  systemctl enable eymo
  systemctl start eymo

  # Install Arduino-CLI
  curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
	mv bin/arduino-cli /usr/local/bin
	rm -rf bin
	sudo -u "$CURRENT_USER" arduino-cli core update-index
	sudo -u "$CURRENT_USER" arduino-cli core install arduino:avr
	sudo -u "$CURRENT_USER" arduino-cli lib update-index
	sudo -u "$CURRENT_USER" arduino-cli lib install Servo
	sudo -u "$CURRENT_USER" arduino-cli lib install Ultrasonic
	sudo -u "$CURRENT_USER" arduino-cli lib install ArduinoJson

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
  if [ ! -d "$APP_PATH" ]; then
    printf "\033[0;33m[WARNING]\033[0m The eymo directory does not exist.\n"
  fi

  # Stop the services
  systemctl stop eymo
  systemctl disable eymo
  systemctl stop eymo_network
  systemctl disable eymo_network

  # Remove the services
  rm /etc/systemd/system/eymo.service
  rm /etc/systemd/system/eymo_network.service
  apt-get remove python3 python3-pip python3-rpi.gpio python3-opencv python3-virtualenv vlc portaudio19-dev flac -y

  # Remove the access point
  systemctl stop hostapd
  systemctl stop dnsmasq
  systemctl stop dhcpcd
  apt-get remove hostapd dnsmasq dhcpcd5 -y

  # Remove the application
  rm -rf $APP_PATH

  # Remove the mDNS hostname
  hostnamectl set-hostname raspberrypi
  sed -i "s/$MDNS_HOSTNAME/raspberrypi/" /etc/hosts

  # Clean the system
  apt-get autoremove -y
  apt-get clean

  # Finish the uninstallation
  read -p "EYMO has been uninstalled successfully. Do you want to reboot now? [Y/n] " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    reboot
  fi
}

reinstall_eymo() {
	if [ "$EUID" -ne 0 ]; then
		printf "\033[0;33m[WARNING]\033[0m This script must be run as root.\n"
		sudo "$0" "$@"
		exit $?
	fi
	if [ ! -d "$APP_PATH" ]; then
		printf "\033[0;31m[ERROR]\033[0m The eymo directory does not exist.\n"
		exit 1
	fi
	if [ ! -f "$CURRENT_PATH/eymo_app.zip" ]; then
		printf "\033[0;31m[ERROR]\033[0m The eymo_app.zip file does not exist.\n"
		exit 1
	fi

	# Stop the services
	systemctl stop eymo
	systemctl disable eymo
	systemctl stop eymo_network
	systemctl disable eymo_network

	# Remove the application
	rm -rf $APP_PATH

	# Extract the zip file
  mkdir -p $APP_PATH
	clear
	unzip -q "$CURRENT_PATH/eymo_app.zip" -d $APP_PATH
  chown -R "$CURRENT_USER":"$CURRENT_USER" $APP_PATH
  chmod -R 755 $APP_PATH

  # Create a virtual environment and install the required packages
  sudo -u eymo virtualenv -p python3 $APP_PATH/venv
  source $APP_PATH/venv/bin/activate
  pip3 install -r $APP_PATH/requirements.txt

  # Enable the services
  systemctl enable eymo_network
  systemctl start eymo_network
  systemctl enable eymo
  systemctl start eymo

  # Finish the reinstallation
	read -p "EYMO has been reinstalled successfully. Do you want to reboot now? [Y/n] " -n 1 -r
	echo
	if [[ $REPLY =~ ^[Yy]$ ]]; then
		reboot
	fi
}

arduino_compile() {
	if [ "$EUID" -ne 0 ]; then
		printf "\033[0;33m[WARNING]\033[0m This script must be run as root.\n"
		sudo "$0" "$@"
		exit $?
	fi
	if [ ! -d "$APP_PATH" ]; then
		printf "\033[0;31m[ERROR]\033[0m The eymo directory does not exist.\n"
		exit 1
	fi

	# Compile the Arduino code
	sudo -u "$CURRENT_USER" arduino-cli compile --fqbn arduino:avr:nano $APP_PATH/arduino/arduino.ino
}

arduino_upload() {
	if [ "$EUID" -ne 0 ]; then
		printf "\033[0;33m[WARNING]\033[0m This script must be run as root.\n"
		sudo "$0" "$@"
		exit $?
	fi
	if [ ! -d "$APP_PATH" ]; then
		printf "\033[0;31m[ERROR]\033[0m The eymo directory does not exist.\n"
		exit 1
	fi

	# Get the Arduino USB port
	USB_PORT=$(ls /dev/ttyUSB* 2>/dev/null | head -n 1)
	if [ -z "$USB_PORT" ]; then
		printf "\033[0;31m[ERROR]\033[0m The Arduino USB port was not found.\n"
		exit 1
	fi

	# Compile the Arduino code
	sudo -u "$CURRENT_USER" arduino-cli compile --fqbn arduino:avr:nano $APP_PATH/arduino/arduino.ino

	# Upload the Arduino code
	sudo -u "$CURRENT_USER" arduino-cli upload -p $USB_PORT --fqbn arduino:avr:nano $APP_PATH/arduino/arduino.ino
}

show_help() {
  printf "EYMO Installer v1.0\n"
	printf "Usage: eymo.sh [OPTION]\n"
	printf "Install EYMO on a Raspberry Pi.\n"
	printf "\n"
	printf "Options:\n"
	printf "  install\t\tInstall EYMO\n"
	printf "  uninstall\t\tUninstall EYMO\n"
	printf "  reinstall\t\tReinstall EYMO\n"
	printf "  arduino <option>\n"
	printf "    compile\t\tCompile the Arduino code\n"
	printf "    upload\t\tCompile and upload the Arduino code\n"
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
	reinstall)
		reinstall_eymo "$@"
		;;
	arduino)
		case $2 in
			compile)
				arduino_compile "$@"
				;;
			upload)
				arduino_upload "$@"
				;;
			*)
				printf "\033[0;31m[ERROR]\033[0m Invalid option.\n"
				show_help
				exit 1
				;;
		esac
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
