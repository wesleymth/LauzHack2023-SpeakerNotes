# speaker-notes

Automatically transcribe the audio and annotate each slide of a presentation with the speaker's commentary, from zoom recordings of the presentation (mp4 file format), as well as the pdf of the presentation.

```
conda create --name lauz python=3.11.5
conda activate lauz
pip install PyPDF2
pip install moviepy
pip install matplotlib, scipy
pip install torch torchvision torchaudio
pip install 'transformers[torch]'
pip install pdfminer
pip3 install pdfminer-six
pip install pytesseract
pip install openai==0.28
# Check if transformers download worked
python -c "from transformers import pipeline; print(pipeline('sentiment-analysis')('we love you'))"
```


# Docker
```
docker build -t lauzhack2023/speaker-notes:0.1.0 .
docker run -it -d --name speaker_notes_container -v $(pwd):/app lauzhack2023/speaker-notes:0.1.0 /bin/bash
docker exec -it speaker_notes_container /bin/bash
python audio_transcribe_scene_detect.py  # How to run a file
```
