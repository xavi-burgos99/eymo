import logging
from datetime import datetime

from rpi.services.service import Service


class RemindersService(Service):
	DEPENDENCIES = ['data_manager']
	LOOP_DELAY = 15

	def init(self):
		"""Initialize the service."""
		self.reminders = []

	def destroy(self):
		"""Destroy the service."""
		pass

	def before(self):
		"""Before the loop. (Before the loop method is called, in the service thread)"""
		self.reminders = self._services['data_manager'].subscribe('reminders', self.__on_update_reminders)

	def loop(self):
		"""Service loop."""
		now = datetime.now()
		current_date = now.date()
		current_time = now.time()

		for reminder in self.reminders:
			if reminder.get('date') == current_date:
				logging.info(
					f"Reminder: {reminder.get('reminder')} is due today but at {reminder.get('time')}, now it's {current_time}.")
				if reminder.get('time') <= current_time:
					logging.info(f"Reminder: {reminder['reminder']} is due now!")
					reminder_info = reminder.get("reminder")

					if reminder.get('callback'):
						reminder.get('callback')(reminder_info)
					self.reminders.remove(reminder)
					self._services['data_manager'].update_data('reminders', self.reminders)
				continue
			logging.info(f"Reminder: {reminder.get('reminder')} is not due yet on today.")

	def set_reminder(self, args, callback):
		reminder = args.get('reminder')

		date = datetime.today().date()
		try:
			date = datetime.strptime(args.get('date'), '%Y-%m-%d').date()
		except Exception:
			logging.warning("Invalid date format. Please use YYYY-MM-DD.")

		time = datetime.now().time()
		try:
			time = datetime.strptime(args.get('time'), '%H:%M').time()
		except Exception:
			logging.warning("Invalid time format. Please use HH:MM:SS.")

		logging.info(f"Reminder: {reminder} at {date} {time}")
		self.reminders.append({'reminder': reminder, 'date': date, 'time': time, 'callback': callback})
		self._services['data_manager'].update_data('reminders', self.reminders)
		logging.info(f"Recordatorio añadido: '{reminder}' para {date} a las {time}")

		return reminder

	def __on_update_reminders(self, key, value):
		if key == "reminders":
			self.reminders = value
