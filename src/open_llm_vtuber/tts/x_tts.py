import re
import threading
import time

import requests
from loguru import logger
from .tts_interface import TTSInterface


class TTSEngine(TTSInterface):
    def __init__(
        self,
        api_url: str = "http://127.0.0.1:8020/tts_to_audio",
        speaker_wav: str = "female",
        language: str = "en",
        speed: float = 0.96,
        temperature: float = 0.65,
        top_p: float = 0.9,
        top_k: int = 50,
        repetition_penalty: float = 2.0,
        length_penalty: float = 1.0,
        enable_text_splitting: bool = False,
    ):
        self.api_url = api_url
        self.speaker_wav = speaker_wav
        self.language = language
        self.speed = speed
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.repetition_penalty = repetition_penalty
        self.length_penalty = length_penalty
        self.enable_text_splitting = enable_text_splitting
        self.new_audio_dir = "cache"
        self.file_extension = "wav"
        self._request_lock = threading.Lock()

    def _sanitize_text(self, text: str) -> str:
        """Remove markup/tags that often break XTTS inference."""
        cleaned = text or ""
        # Remove emotion/style tags like [smirk], [surprise], etc.
        cleaned = re.sub(r"\[[^\[\]\n]{1,40}\]", " ", cleaned)
        # Normalize whitespace and strip control chars while keeping PT-BR chars.
        cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", " ", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    def generate_audio(self, text, file_name_no_ext=None):
        file_name = self.generate_cache_file_name(file_name_no_ext, self.file_extension)
        sanitized_text = self._sanitize_text(text)

        if not sanitized_text:
            logger.warning("XTTS received empty text after sanitization.")
            return None

        # Prepare the data for the POST request
        data = {
            "text": sanitized_text,
            "speaker_wav": self.speaker_wav,
            "language": self.language,
            "speed": self.speed,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "repetition_penalty": self.repetition_penalty,
            "length_penalty": self.length_penalty,
            "enable_text_splitting": self.enable_text_splitting,
        }

        # XTTS on Colab tends to crash under concurrent requests, so serialize them.
        with self._request_lock:
            for attempt in range(2):
                response = requests.post(self.api_url, json=data, timeout=300)

                if response.status_code == 200:
                    with open(file_name, "wb") as audio_file:
                        audio_file.write(response.content)
                    return file_name

                logger.critical(
                    "Error: Failed to generate audio. "
                    f"Status code: {response.status_code}. "
                    f"Body: {response.text[:500]}"
                )

                if attempt == 0:
                    time.sleep(1.5)

        return None
