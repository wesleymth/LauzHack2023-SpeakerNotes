FROM huggingface/transformers-inference:4.24.0-pt1.13-cpu

WORKDIR /app

RUN apt-get update && apt-get -y upgrade
RUN apt-get install ffmpeg -y
RUN apt-get install tesseract-ocr -y
RUN apt-get install libpoppler-dev -y

RUN pip install PyPDF2
RUN pip install moviepy
RUN pip install pandas
RUN pip install matplotlib
RUN pip install scipy
RUN pip install openai==0.28
RUN pip install pdfminer pdfminer-six
RUN pip install pytesseract
RUN pip install pdf2image
RUN pip install PyMuPDF

# Streamlint specific stuff

# RUN pip install streamlit

# EXPOSE 8501

# HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]