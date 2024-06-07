class ScreenMode:
	STANDBY = 0
	SPEAKING = 1
	MOVING = 2
	SUNNY = 3
	CLOUDY = 4
	RAINY = 5
	STORMY = 6
	SNOWY = 7
	SHUTDOWN = 8
	ERROR = 9
	MUSIC = 10
	RECOGNIZING = 11
	STARTUP = 12
	WIFI = 13
	REMINDER = 14
	CONNECT = 15

	@staticmethod
	def last():
		"""Return the last screen mode index."""
		return 15
