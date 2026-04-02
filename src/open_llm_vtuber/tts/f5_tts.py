import requests
from loguru import logger

from .tts_interface import TTSInterface


class TTSEngine(TTSInterface):
    def __init__(
        self,
        api_url: str = "http://127.0.0.1:9880/tts",
        speed: float = 1.0,
        remove_silence: bool = False,
    ):
        self.api_url = api_url
        self.speed = speed
        self.remove_silence = remove_silence
        self.file_extension = "wav"

    def generate_audio(self, text, file_name_no_ext=None):
        file_name = self.generate_cache_file_name(file_name_no_ext, self.file_extension)
        payload = {
            "text": text,
            "speed": self.speed,
            "remove_silence": self.remove_silence,
        }

        try:
            response = requests.post(self.api_url, json=payload, timeout=300)
            response.raise_for_status()
        except Exception as e:
            logger.critical(f"Error: Failed to generate audio from F5-TTS. {e}")
            return None

        with open(file_name, "wb") as audio_file:
            audio_file.write(response.content)
        return file_name
