import json

class ScreenAnimations:
    
    PROGRESS_BAR = 'progress_bar.json'
    TALK = 'talk.json'
    SUN = 'sun.json'
    CLOUDY = 'cloudy.json'
    RAIN = 'rain.json'
    STORM = 'storm.json'
    SNOW = 'snow.json'
    CHECKBOX = 'checkbox.json'
    SHUTDOWN = 'shutdown.json'
    WIFI = 'wifi.json'
    CLOUD_PROGRESS = 'cloud_progress.json'
    WARNING = 'warning.json'
    SONG = 'song.json'
    WAVES = 'waves.json'
    
    @staticmethod
    def get_list():
        return [
            'PROGRESS_BAR',
            'TALK',
            'SUN',
            'CLOUDY',
            'RAIN',
            'STORM',
            'SNOW',
            'CHECKBOX',
            'SHUTDOWN',
            'WIFI',
            'CLOUD_PROGRESS',
            'WARNING',
            'SONG',
            'WAVES'
        ]
    
    @staticmethod
    def get_animation_path(animation: str, path: str = 'static/icons'):
        return f'{path}/{animation}'
    
    @staticmethod
    def get(name: str):
        animation = getattr(ScreenAnimations, name)
        path = ScreenAnimations.get_animation_path(animation)
        with open(path) as f:
            return json.load(f)
