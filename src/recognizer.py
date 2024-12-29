import speech_recognition as sr
from pathlib import Path
from pydub import AudioSegment


class Recognizer:
    def __init__(self) -> None:
        pass

    def recognize(self, audio_path: Path) -> dict:
        """
        Recognizes audio file

        Returns dict from recognizer.recognize_whisper
        """
        if audio_path.suffix != "wav":
            audio_path = self.convert_to_wav(audio_path)
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path.as_posix()) as source:
            audio_data = recognizer.record(source)
        transcript = recognizer.recognize_whisper(
            audio_data, model="base.en", show_dict=True
        )
        return transcript

    def convert_to_wav(self, audio_path: Path) -> Path:
        """
        Converts audio to wav

        Returns path to file
        """
        new_audio_path = audio_path.parent / (audio_path.name + ".wav")
        audio = AudioSegment.from_file(audio_path)
        audio.export(new_audio_path, format="wav")
        return new_audio_path
