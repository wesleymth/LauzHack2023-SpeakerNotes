# pip install git+https://github.com/openai/whisper.git 
import whisper
import torch
import joblib


print(whisper.available_models())

subclips_list = joblib.load('output/subclips_list.jl')

print(subclips_list[0]['path'])

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print("Using device:", device)
model = whisper.load_model(name="medium.en", device=device)

transcription = [model.transcribe(subclips_list[i]['path'], verbose=False) for i, _ in enumerate(subclips_list)]
joblib.dump(transcription, 'output/transcription_(only_first).jl')