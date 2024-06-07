import subprocess
import platform


def check_network_connection():
	"""
	Check if the Raspberry Pi has an active network connection by pinging Google's DNS server.
	:return: True if there's connection, False otherwise
	"""
	try:
		if platform.system() == 'Windows':
			subprocess.check_output(['ping', '-n', '1', '8.8.8.8'], stderr=subprocess.STDOUT)
		else:
			subprocess.check_output(['ping', '-c', '1', '8.8.8.8'], stderr=subprocess.STDOUT)
		return True
	except subprocess.CalledProcessError:
		return False
	except Exception as e:
		print(f"An error occurred while checking network connection: {e}")
		return False
