import os

UTILS_DATA = {}
RPI_CHIPS = ['BCM2708', 'BCM2709', 'BCM2711', 'BCM2835', 'BCM2836', 'BCM2837', 'BCM2837B0', 'BCM2712', 'RP1']


def is_rpi() -> bool:
	"""Check if the current system is a Raspberry Pi.
	Returns:
		bool: True if the current system is a Raspberry Pi, False otherwise
	"""
	if 'is_rpi' in UTILS_DATA:
		return UTILS_DATA['is_rpi']
	if os.name != 'posix':
		UTILS_DATA['is_rpi'] = False
		return False
	try:
		with open('/proc/cpuinfo', 'r') as cpuinfo:
			for line in cpuinfo:
				if line.startswith('Hardware'):
					UTILS_DATA['is_rpi'] = any([chip in line for chip in RPI_CHIPS])
					return UTILS_DATA['is_rpi']
	except Exception:
		pass
	UTILS_DATA['is_rpi'] = False
	return False
