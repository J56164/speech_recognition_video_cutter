import speech_recognition as sr
from pathlib import Path
from pydub import AudioSegment
from typing import List
from moviepy import VideoFileClip


class Recognizer:
    def __init__(self) -> None:
        pass

    def ensure_path_type(self, path: Path | str) -> Path:
        if isinstance(path, Path):
            return path
        elif isinstance(path, str):
            return Path(path)
        else:
            raise TypeError(
                f"Expected path to be of type Path or str, found {type(path)}."
            )

    def cut_video(
        self,
        video_path: Path | str,
        cut_timestamps: List[int],
        output_folder_path: Path | str | None = None,
    ) -> None:
        """
        Cuts a video file from timestamp
        """
        video_path = self.ensure_path_type(video_path)
        if output_folder_path is not None:
            output_folder_path = self.ensure_path_type(output_folder_path)

        for i in range(len(cut_timestamps) - 1):
            if cut_timestamps[i] > cut_timestamps[i + 1]:
                cut_timestamps = sorted(cut_timestamps)
                break

        video = VideoFileClip(video_path.as_posix())
        if cut_timestamps[-1] > video.duration:
            raise ValueError(
                "Cut timestamps must not exceed video duration. Expected to be <= {video.duration}. Found {cut_timestamps[-1]}."
            )

        if output_folder_path is None:
            output_folder_path = video_path.parent

        curr_timestamp = 0
        for idx, cut_timestamp in enumerate((*cut_timestamps, video.duration)):
            clip: VideoFileClip = video.subclipped(curr_timestamp, cut_timestamp)
            clip.write_videofile((output_folder_path / f"{idx}.mp4").as_posix())
            curr_timestamp = cut_timestamp

    def recognize_audio(self, audio_path: Path) -> dict:
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
