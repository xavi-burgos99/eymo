import logging
import vlc


class AudioPlayer:
    def __init__(self):
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.playlist = []
        self.current_index = -1

        self.is_playing = False
        self.paused = False
        self.stop_requested = False

        events = self.player.event_manager()
        events.event_attach(vlc.EventType.MediaPlayerEndReached, self._end_reached)

    def _end_reached(self, event):
        logging.info("[PLAYER] Song ended, moving to the next")
        self.next()

    def add_to_playlist(self, url):
        self.playlist.append(url)
        logging.info(f"[PLAYER] Added {url} to playlist")

    def play(self):
        if not self.playlist:
            logging.info("[PLAYER] Playlist is empty")
            return

        if self.paused:
            logging.info("[PLAYER] Resuming playback")
            self.player.play()
        else:
            logging.info("[PLAYER] Starting playback")
            self.current_index = 0
            self._play_current()

        self.is_playing = True
        self.paused = False
        self.stop_requested = False

    def _play_current(self):
        if self.current_index < len(self.playlist):
            url = self.playlist[self.current_index]
            media = self.instance.media_new(url)
            self.player.set_media(media)
            self.player.play()
            logging.info(f"[PLAYER] Now playing {url}")

    def pause(self):
        if self.is_playing and not self.paused:
            logging.info("[PLAYER] Pausing playback")
            self.player.pause()
            self.is_playing = False
            self.paused = True
        elif self.paused:
            logging.info("[PLAYER] Resuming playback")
            self.player.pause()
            self.is_playing = True
            self.paused = False

    def stop(self):
        logging.info("[PLAYER] Stopping playback and removing current song from playlist")
        self.stop_requested = True
        self.paused = False
        self.is_playing = False
        self.player.stop()

        if self.current_index < len(self.playlist):
            self.playlist.pop(self.current_index)

    def next(self):
        if self.current_index + 1 < len(self.playlist):
            self.current_index += 1
            self._play_current()
        else:
            logging.info("[PLAYER] End of playlist")
            self.is_playing = False
            self.current_index = -1

        if self.current_index < len(self.playlist):
            self.playlist.pop(self.current_index)
