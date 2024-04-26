import subprocess


def check_network_connection():
    """
    Check if the Raspberry Pi has an active network connection by pinging Google's DNS server.
    :return: True if there's connection, False otherwise
    """
    try:
        subprocess.check_output(['ping', '8.8.8.8'], stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError:
        return False
    except Exception as e:
        print(f"An error occurred while checking network connection: {e}")
        return False
