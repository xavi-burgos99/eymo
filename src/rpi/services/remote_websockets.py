import asyncio
import logging

import websockets

from services.service import Service

from rpi.models.frame_type import FrameType


class RemoteWebsocketsService(Service):
	DEPENDENCIES = ['camera', 'screen']

	def init(self):
		"""Initialize the service."""
		pass

	def destroy(self):
		"""Destroy the service."""
		pass

	def before(self):
		"""Before the loop. (Before the loop method is called, in the service thread)"""
		asyncio.run(self.__init_stream__())

	async def __init_stream__(self):
		logging.info('Stream initialized at port 55158 using websockets.')
		async with websockets.serve(self.stream, "0.0.0.0", 55158):
			await asyncio.Future()  # run forever

	async def stream(self, websocket):
		logging.info(f"[WEBSOCKETS] Device connected: {websocket.remote_address}")
		try:
			while True:
				message_task = asyncio.ensure_future(websocket.recv())
				send_task = asyncio.ensure_future(self.send_frame(websocket))
				done, pending = await asyncio.wait(
					[message_task, send_task],
					return_when=asyncio.FIRST_COMPLETED
				)

				if message_task in done:
					message = message_task.result()
					await self.handle_message(message, websocket)

				if send_task in done:
					send_task.result()  # This will raise any exceptions if occurred

				for task in pending:
					task.cancel()  # Cancel any pending tasks

		except websockets.ConnectionClosed as e:
			logging.error(f"Device disconnected: {websocket.remote_address} with error: {e}")
		except Exception as e:
			logging.error(f"An error occurred in the websocket stream: {e}")
			await asyncio.sleep(1)

	async def send_frame(self, websocket):
		frame = self._services['camera'].get_frame(FrameType.BYTES)
		if frame is None:
			logging.warning("Received no frame from camera.")
			return
		await websocket.send(frame)
		logging.debug("Frame sent.")
		await asyncio.sleep(0.033)  # Send ~30 frames per second

	async def handle_message(self, message, websocket):
		logging.info(f"Received message from {websocket.remote_address}: {message}")
