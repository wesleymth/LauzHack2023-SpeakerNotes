from datetime import timedelta

# pip install git+https://github.com/openai/whisper.git 
import whisper
import torch
import joblib

from audio_preprocess import subclip_audio


VIDEO_FILE_PATH = "/content/drive/MyDrive/Colab Notebooks/BIOENG320_lecture2(2023)_Prof-Yimon-AYE.mp4"
AUDIO_FILE_PATH = "/content/drive/MyDrive/Colab Notebooks/BIOENG320_lecture2(2023)_Prof-Yimon-AYE.mp3"

# MP4ToMP3(VIDEO_FILE_PATH, AUDIO_FILE_PATH)

subclips_list = subclip_audio(AUDIO_FILE_PATH, 
              saving_folder="/content/drive/MyDrive/Colab Notebooks",
              audio_start=timedelta(hours=0, minutes=10, seconds=5),
              audio_end=timedelta(hours=1, minutes=56, seconds=4),
              pause_start_time=timedelta(hours=1, minutes=00, seconds=18),
              pause_end_time=timedelta(hours=1, minutes=13, seconds=10))


print(whisper.available_models())
model = whisper.load_model("medium.en", torch.device('cuda' if torch.cuda.is_available() else 'cpu'))

transcription = [model.transcribe(subclips_list[i]['path'], verbose=True) for i, _ in enumerate(subclips_list)]
joblib.dump(transcription, 'transcription.jl')