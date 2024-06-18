import os
import json
import time
import threading
import subprocess

CHECK_INTERVAL = 5
DISCONNECTED_THRESHOLD = 10

os.chdir(os.path.dirname(os.path.abspath(__file__)))
NETWORK_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state/network")
NETWORK_FILE = os.path.join(NETWORK_DIR, "connected")
WIFI_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static/wifi.json")
PING_SERVERS = ["8.8.8.8", "1.1.1.1", "8.8.4.4"]
current_server_index = 0
is_trying = False
lock = threading.Lock()

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

def connect_wifi(ssid, password):
    global is_trying
    with lock:
        is_trying = True
        os.system("sudo systemctl stop networking")
        os.system(f"sudo wpa_passphrase {ssid} {password} >> /etc/wpa_supplicant/wpa_supplicant.conf")
        os.system("sudo systemctl start networking")
        time.sleep(10)
        is_trying = False

def try_connection():
    global is_trying
    if is_trying:
        return
    if not os.path.exists(WIFI_CONFIG_FILE):
        return
    with open(WIFI_CONFIG_FILE, "r") as file:
        config = json.load(file)
        if "ssid" not in config or "password" not in config:
            return
    threading.Thread(target=connect_wifi, args=(config["ssid"], config["password"])).start()

def main():
    if os.path.exists(NETWORK_DIR):
        if os.path.exists(NETWORK_FILE):
            os.remove(NETWORK_FILE)
    else:
        os.makedirs(NETWORK_DIR)
    disconnected_time = 0
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
                try_connection()
                if not check_access_point():
                    enable_access_point()
                    if os.path.exists(NETWORK_FILE):
                        os.remove(NETWORK_FILE)
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()