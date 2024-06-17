import os
import time
import subprocess

CHECK_INTERVAL = 5
DISCONNECTED_THRESHOLD = 10

os.chdir(os.path.dirname(os.path.abspath(__file__)))
NETWORK_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state/network")
NETWORK_FILE = NETWORK_DIR + "/connected"
PING_SERVERS = ["8.8.8.8", "1.1.1.1", "8.8.4.4"]
current_server_index = 0

def is_connected():
	global current_server_index
	server = PING_SERVERS[current_server_index]
	try:
		subprocess.check_call(["ping", "-c", "1", server], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
		current_server_index = (current_server_index + 1) % len(PING_SERVERS)
		return True
	except subprocess.CalledProcessError:
		current_server_index = (current_server_index + 1) % len(PING_SERVERS)
		return False


def enable_access_point():
	os.system("sudo systemctl start hostapd")
	os.system("sudo systemctl start dnsmasq")


def disable_access_point():
	os.system("sudo systemctl stop hostapd")
	os.system("sudo systemctl stop dnsmasq")


def check_access_point():
	hostapd = subprocess.run(["systemctl", "is-active", "hostapd"], stdout=subprocess.PIPE)
	dnsmasq = subprocess.run(["systemctl", "is-active", "dnsmasq"], stdout=subprocess.PIPE)
	return hostapd.stdout.decode().strip() == "active" and dnsmasq.stdout.decode().strip() == "active"


def main():
	if os.path.exists(NETWORK_DIR):
		if os.path.exists(NETWORK_FILE):
			os.remove(NETWORK_FILE)
	else:
		os.makedirs(NETWORK_DIR)
	disconnected_time = DISCONNECTED_THRESHOLD
	while True:
		if is_connected():
			disconnected_time = 0
			if check_access_point():
				disable_access_point()
				if not os.path.exists(NETWORK_FILE):
					open(NETWORK_FILE, "w").close()
		else:
			disconnected_time += CHECK_INTERVAL
			if disconnected_time >= DISCONNECTED_THRESHOLD:
				if not check_access_point():
					enable_access_point()
					if os.path.exists(NETWORK_FILE):
						os.remove(NETWORK_FILE)
		time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
	main()
