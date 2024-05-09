import logging
import vlc

class AudioPlayer:
    def __init__(self, url):
        self.url = url
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        media = self.instance.media_new(url)
        self.player.set_media(media)
        self.paused = False
        self.stop_requested = False

    def play(self):
        logging.info("[PLAYER] Starting playback")
        self.stop_requested = False
        self.paused = False
        self.player.play()

    def pause(self):
        if not self.paused:
            logging.info("[PLAYER] Pausing playback")
            self.player.pause()
            self.paused = True
        else:
            logging.info("[PLAYER] Resuming playback")
            self.player.pause()
            self.paused = False

    def stop(self):
        logging.info("[PLAYER] Stopping playback")
        self.stop_requested = True
        self.player.stop()