class ControlMode:
	OFF = 0
	MANUAL = 1
	TRIPOD = 2
	AUTO = 3

	@staticmethod
	def last():
		"""Return the last control mode index."""
		return 3

	@staticmethod
	def get_name(mode: int) -> str:
		"""Return the control mode name."""
		modes = ['OFF', 'MANUAL', 'TRIPOD', 'AUTO']
		if mode < 0 or mode >= len(modes):
			return 'UNKNOWN'
		return modes[mode]