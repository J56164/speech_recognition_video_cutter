import speech_recognition as sr
from pathlib import Path
from pydub import AudioSegment
from typing import List
from moviepy import VideoFileClip
import tempfile
import re
import shutil


class VideoCutter:
    def cut_video_recognize(
        self,
        video_path: Path | str,
        output_folder_path: Path | str | None = None,
    ):
        """
        Recognizes and cuts video with the word 'cut'
        """
        video_path = self.ensure_path_type(video_path)
        if output_folder_path is None:
            output_folder_path = video_path.parent
        else:
            output_folder_path = self.ensure_path_type(output_folder_path)
        if not output_folder_path.exists():
            output_folder_path.mkdir(parents=True)

        recognization = self.recognize_audio(video_path)
        cut_timestamps = []
        for segment in recognization["segments"]:
            if re.search(r"\bcut\b", segment["text"], re.IGNORECASE):
                cut_timestamps.append(segment["end"])
        if len(cut_timestamps) >= 1:
            self.cut_video(
                video_path, cut_timestamps, output_folder_path, timestamp_exceed_ok=True
            )
        else:
            if output_folder_path is None:
                shutil.copy(video_path, video_path.parent / (f"0{video_path.suffix}"))
            else:
                shutil.copy(video_path, output_folder_path / (f"0{video_path.suffix}"))

    def ensure_path_type(self, path: Path | str) -> Path:
        """
        Returns a pathlib.Path object of path

        Raises TypeError if type of path is not Path | str
        """
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
        timestamp_exceed_ok: bool = False,
    ) -> None:
        """
        Cuts a video file from timestamp and save it

        For now, cut_timestamps must not be empty.

        Raises ValueError if value of cut_timestamps exceeds video length
        and timestamp_exceed_ok is False
        """
        video_path = self.ensure_path_type(video_path)
        if output_folder_path is None:
            output_folder_path = video_path.parent
        else:
            output_folder_path = self.ensure_path_type(output_folder_path)
        if not output_folder_path.exists():
            output_folder_path.mkdir(parents=True)

        for i in range(len(cut_timestamps) - 1):
            if cut_timestamps[i] > cut_timestamps[i + 1]:
                cut_timestamps = sorted(cut_timestamps)
                break

        video = VideoFileClip(video_path.as_posix())
        if timestamp_exceed_ok:
            while len(cut_timestamps) >= 1 and cut_timestamps[-1] > video.duration:
                cut_timestamps.pop()
        elif cut_timestamps[-1] > video.duration:
            raise ValueError(
                f"Cut timestamps must not exceed video duration. Expected to be <= {video.duration}. Found {cut_timestamps[-1]}."
            )

        curr_timestamp = 0
        for idx, cut_timestamp in enumerate((*cut_timestamps, video.duration)):
            clip: VideoFileClip = video.subclipped(curr_timestamp, cut_timestamp)
            clip.write_videofile((output_folder_path / f"{idx}.mp4").as_posix())
            curr_timestamp = cut_timestamp

    def recognize_audio(self, audio_path: Path | str) -> dict:
        """
        Recognizes audio or video file

        *args and **kwargs will be passed to recognizer.recognize_whisper

        Returns dict from recognizer.recognize_whisper
        """
        audio_path = self.ensure_path_type(audio_path)

        temp_filepaths: List[Path] = []
        if audio_path.suffix != "wav":
            with tempfile.NamedTemporaryFile("wb", suffix=".wav", delete=False) as file:
                temp_filepath = Path(file.name)
            audio_path = self.convert_audio_to_wav(
                audio_path, output_path=temp_filepath
            )

        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path.as_posix()) as source:
            audio_data = recognizer.record(source)
        transcript = recognizer.recognize_whisper(
            audio_data, model="base.en", show_dict=True, verbose=False
        )

        for temp_filepath in temp_filepaths:
            temp_filepath.unlink(missing_ok=True)

        return transcript

    def convert_audio_to_wav(
        self, audio_path: Path | str, output_path: Path | str | None = None
    ) -> Path:
        """
        Converts audio or video to wav

        Defaults to same path

        Returns path to file
        """
        audio_path = self.ensure_path_type(audio_path)
        if output_path is None:
            output_path = audio_path.parent / (audio_path.name + ".wav")
        else:
            output_path = self.ensure_path_type(output_path)
            if output_path.suffix != ".wav":
                output_path = output_path.parent / (output_path.name + ".wav")
        if not output_path.parent.exists():
            output_path.mkdir(parents=True, exist_ok=True)

        audio = AudioSegment.from_file(audio_path)
        audio.export(output_path, format="wav")
        return output_path
