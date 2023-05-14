import datetime
from datetime import timedelta
import os
from math import ceil

from moviepy.audio.AudioClip import concatenate_audioclips
from moviepy.editor import AudioFileClip
import joblib


def MP4ToMP3(mp4 :str, mp3 :str)->None:
    """Convert mp4 to mp3 using moviepy

    Parameters
    ----------
    mp4 : str
        mp4 file path
    mp3 : str
        mp3 file path
    """
    FILETOCONVERT = AudioFileClip(mp4)
    FILETOCONVERT.write_audiofile(mp3)
    FILETOCONVERT.close()

def get_audio_size_mb(mp3_path :str)->float:
    """Get mp3 file size in megabytes

    Parameters
    ----------
    mp3_path : str
        mp3 file path

    Returns
    -------
    float
        mp3 file size in megabytes
    """
    # Gets size in bytes and converts it to megabytes
    return os.path.getsize(mp3_path) / (1024*1024)

def calculate_number_subclips(mp3_path :str, mb_limitation :float=25.0)->int:
    """Calculate number of subclips to be generated

    Parameters
    ----------
    mp3_path : str
        mp3 file path
    mb_limitation : float, optional
        max size of the subclips, limited by the model used, if openai/whisper in May 2023 it is 25MB, by default 25.0

    Returns
    -------
    int
        number of subclips to be generated
    """
    return ceil(get_audio_size_mb(mp3_path)/mb_limitation)

def subclip_audio(mp3_path :str,
                  saving_folder :str,
                  stride :int =10, 
                  audio_start :datetime.timedelta =None, 
                  audio_end :datetime.timedelta =None, 
                  pause_start_time :datetime.timedelta =None,
                  pause_end_time :datetime.timedelta =None,
                  max_subclip_size_mb :float = 25.0) -> dict:
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
    audio_clip = AudioFileClip(mp3_path)
    print(f'audio_clip.duration normal: {audio_clip.duration}')
    if audio_end:
        audio_clip = audio_clip.subclip(0, audio_end.total_seconds())
    #   audio_clip = audio_clip.set_end(t=audio_end.total_seconds())
        print(f'audio_clip.duration end dropped: {audio_clip.duration}')

    if pause_start_time and pause_end_time:
        start_to_pause = audio_clip.subclip(0, pause_start_time.total_seconds())
        pasue_to_end = audio_clip.subclip(pause_end_time.total_seconds(), audio_clip.duration)
        audio_clip = concatenate_audioclips([start_to_pause, pasue_to_end])
        start_to_pause.close()
        pasue_to_end.close()

    #   audio_clip = audio_clip.cutout(ta=pause_start_time.total_seconds()-audio_start.total_seconds(),tb=pause_end_time.total_seconds()-audio_start.total_seconds())
        print(f'audio_clip.duration pause dropped: {audio_clip.duration}')
    
    if audio_start:
        audio_clip=audio_clip.subclip(audio_start.total_seconds(), audio_clip.duration)
    #   audio_clip = audio_clip.set_start(t=audio_start.total_seconds(), change_end=False)
        print(f'audio_clip.duration start dropped: {audio_clip.duration}')

    duration = round(audio_clip.duration)
    print(f'audio_clip.duration at the end: {audio_clip.duration}')
    nb_subclips = calculate_number_subclips(mp3_path=mp3_path, mb_limitation=max_subclip_size_mb)
    single_subclip_duration = ceil(duration/nb_subclips)
    subclips_timestamps = [dict(index=str(int(i/single_subclip_duration)), 
                                start=max(i-stride, 0), 
                                end=min(i+single_subclip_duration+stride, duration)) 
                            for i in range(0, duration, single_subclip_duration)]#{str(int(i/single_subclip_duration)):(i, i+single_subclip_duration) for i in range(0, duration, single_subclip_duration)}
    for subclip in subclips_timestamps:
        temp_clip = audio_clip.subclip(subclip['start'], subclip['end'])
        subclip['path'] = f"{saving_folder}/subclip_{subclip['index']}_{subclip['start']}_{subclip['end']}.mp3"
        # temp_clip.write_audiofile(subclip['path'])
        temp_clip.close()
    audio_clip.close()
    return subclips_timestamps


if __name__ == "__main__":
    VIDEO_FILE_PATH = "data/BIOENG320_lecture2(2023)_Prof-Yimon-AYE.mp4"
    AUDIO_FILE_PATH = "output/BIOENG320_lecture2(2023)_Prof-Yimon-AYE.mp3"

    # MP4ToMP3(VIDEO_FILE_PATH, AUDIO_FILE_PATH)

    subclips_list = subclip_audio(AUDIO_FILE_PATH, 
                saving_folder="output",
                audio_start=timedelta(hours=0, minutes=10, seconds=5),
                audio_end=timedelta(hours=1, minutes=56, seconds=4),
                pause_start_time=timedelta(hours=1, minutes=00, seconds=18),
                pause_end_time=timedelta(hours=1, minutes=13, seconds=10))
    
    joblib.dump(subclips_list, "output/subclips_list.jl")