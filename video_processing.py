import datetime
import subprocess
from datetime import timedelta

from moviepy.editor import VideoFileClip, concatenate_videoclips


def clean_video(
    mp4_path: str,
    clean_video_path: str,
    video_start: datetime.timedelta = None,
    video_end: datetime.timedelta = None,
    pause_start_time: datetime.timedelta = None,
    pause_end_time: datetime.timedelta = None,
) -> None:
    """Subclip audio into smaller clips

    Parameters
    ----------
    mp3_path : str
        mp3 file path
    saving_folder : str
        folder to save the subclips
    stride : int, optional
        seconds to add before and after each clip for better transcription, by default 10
    audio_start : datetime.timedelta, optional
        transcription start time, by default None
    audio_end : datetime.timedelta, optional
        transcription end time, by default None
    pause_start_time : datetime.timedelta, optional
        if there is a pause in the video, pause_end_time also needs to be set, by default None
    pause_end_time : datetime.timedelta, optional
        if there is a pause in the video, pause_start_time also needs to be set, by default None
    max_subclip_size_mb : float, optional
        max size of the subclips, limited by the model used, if openai/whisper in May 2023 it is 25MB, by default 25.0

    Returns
    -------
    dict
        list of subclips with their start and end time, as well as file path
    """
    video_clip = VideoFileClip(mp4_path)
    if video_end:
        video_clip = video_clip.subclip(0, video_end.total_seconds())

    if pause_start_time and pause_end_time:
        start_to_pause = video_clip.subclip(0, pause_start_time.total_seconds())
        pause_to_end = video_clip.subclip(
            pause_end_time.total_seconds(), video_clip.duration
        )
        video_clip = concatenate_videoclips([start_to_pause, pause_to_end])
        start_to_pause.close()
        pause_to_end.close()

    if video_start:
        video_clip = video_clip.subclip(
            video_start.total_seconds(), video_clip.duration
        )
    video_clip.write_videofile(clean_video_path)
    video_clip.close()


def detect_frame_changes(
    cleaned_vieo_path: str,
    metadata_output_path: str,
    frames_output_path: str,
    sensitivity_threshold: float = 0.05,
) -> None:
    bash_command = f"""ffmpeg -i {cleaned_vieo_path} -filter_complex "select='gt(scene,{str(sensitivity_threshold)})',metadata=print:file={metadata_output_path}" -start_number 0 -fps_mode vfr {frames_output_path}"""
    # ffmpeg -i 'data/syn_bio_rna_lecture_1/BIOENG320-lecture1(2023)_Prof-Yimon-AYE.mp4' -filter_complex "select='gt(scene,0.05)',metadata=print:file=output/BIOENG320-lecture1(2023)_Prof-Yimon-AYE/frame_changes.txt" -start_number 0 -fps_mode vfr 'output/BIOENG320-lecture1(2023)_Prof-Yimon-AYE/frames/frame-%03d.png'
    print(
        f"\nDetecting frame changes in video {cleaned_vieo_path} using the command:\n{bash_command}"
    )
    process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()


if __name__ == "__main__":
    # clean_video(
    #     mp4_path="data/BIOENG320_lecture2(2023)_Prof-Yimon-AYE.mp4",
    #     clean_video_path="output/cleaned_BIOENG320_lecture2(2023)_Prof-Yimon-AYE.mp4",
    #     video_start=timedelta(hours=0, minutes=10, seconds=5),
    #     video_end=timedelta(hours=1, minutes=56, seconds=4),
    #     pause_start_time=timedelta(hours=1, minutes=00, seconds=18),
    #     pause_end_time=timedelta(hours=1, minutes=13, seconds=10),
    # )
    detect_frame_changes(
        cleaned_vieo_path="data/syn_bio_rna_lecture_1/BIOENG320-lecture1(2023)_Prof-Yimon-AYE.mp4",
        metadata_output_path="output/BIOENG320-lecture1(2023)_Prof-Yimon-AYE/frame_changes.txt",
        frames_output_path="output/BIOENG320-lecture1(2023)_Prof-Yimon-AYE/frames/frame-%03d.png",
        sensitivity_threshold=0.05,
    )
