import streamlit as st
import pandas as pd
import numpy as np

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

st.title('LauzHack 2023: Speaker Notes :pencil2: :notebook:')

if st.checkbox('Show full pipeline'):
    st.graphviz_chart('''
        digraph {
            video -> audio
            video -> scene_detection
            scene_detection -> slide_timestamps
            audio -> Whisper
            Whisper -> transcribed_text_over_time
            pdf -> blank_spaces
            pdf -> written_text_per_slide
            written_text_per_slide -> ChatGPT
            transcribed_text_over_time -> transcribed_text_per_slide
            slide_timestamps -> transcribed_text_per_slide
            transcribed_text_per_slide -> ChatGPT
            ChatGPT -> summary
            summary -> blank_spaces
            blank_spaces -> annotated_pdf
        }
    ''')

st.header('Input Data :open_file_folder: :arrow_down:', divider='blue')

col1, col2 = st.columns(2)
with col1:
    st.header("Pdf :clipboard:")
    input_pdf = st.file_uploader("Choose the slide deck of the presentation", type=['pdf'])
with col2:
    st.header("Video :movie_camera:")
    input_video = st.file_uploader("Choose the video of the presentation", type=['mov', 'mp4'])
    

st.header('Settings :wrench:', divider='blue')
scene_detect_tab, whisper_tab, chatgpt_tab, text_to_annotate_tab = st.tabs(
    [
        "Scene Detection", 
        "Whisper Model", 
        "ChatGPT", 
        "Annotation Text",
    ]
)
with scene_detect_tab:
    st.write("What should be the threshold of sensitivity of ffmpeg?")
    ffmpeg_sensitivity = st.slider('Ffmpeg scene detection sensitivity', 0.01, 0.1, 0.03)
    st.write("How much time do you consider to do a transition?")
    transition_time_threshold = st.slider('Transition time [s]', 0.5, 2., 1.)
with whisper_tab:
    st.write("Which Whisper model do you want to use for audio transcription?")
    option_model = st.selectbox(
        'Selected model',
        (
            "tiny",
            "base",
            "small",
            "medium",
            "large",
            "tiny.en",
            "base.en",
            "small.en",
            "medium.en",
        ),
        index=3,
    )
    st.write("""|  Size  | Parameters | English-only model | Multilingual model | Required VRAM | Relative speed |
|:------:|:----------:|:------------------:|:------------------:|:-------------:|:--------------:|
|  tiny  |    39 M    |     `tiny.en`      |       `tiny`       |     ~1 GB     |      ~32x      |
|  base  |    74 M    |     `base.en`      |       `base`       |     ~1 GB     |      ~16x      |
| small  |   244 M    |     `small.en`     |      `small`       |     ~2 GB     |      ~6x       |
| medium |   769 M    |    `medium.en`     |      `medium`      |     ~5 GB     |      ~2x       |
| large  |   1550 M   |        N/A         |      `large`       |    ~10 GB     |       1x       |""")
    
    
with chatgpt_tab:
    st.write("Would you like to try and remove repeated info between the text on the slides and the transcribed text?")
    ignore_repeated_text = st.toggle('Remove repeated info between texts')
    
with text_to_annotate_tab:
    st.write("Which color do you want the text to be written in?")
    color = st.color_picker('Pick A Color', '#000000')
    # st.write('The current color is, in hex format, ', color)
    # st.write('The current color is, in RGB format, ', hex_to_rgb(color))
    st.write("Which font do you want to use?")
    option_ft_name = st.selectbox(
        'Font name',
        (
            "Helv",
        )
    )
    st.write("Which font size do you want to use?")
    option_ft_size = st.slider('Font size [pt]', 6, 20, 10)
    

st.header('Run the Pipeline', divider='blue')


if 'api_key_inputed' not in st.session_state:
    st.session_state.api_key_inputed = False
def input_api_key():
    st.session_state.api_key_inputed = True
OPENAI_API_KEY = st.text_input('OpenAI API key :closed_lock_with_key:', '', on_change=input_api_key, type="password")

if 'pipeline_clicked' not in st.session_state:
    st.session_state.pipeline_clicked = False
if 'warn_api_key_missing' not in st.session_state:
    st.session_state.warn_api_key_missing = False
def click_button():
    if st.session_state.api_key_inputed:
        st.session_state.pipeline_clicked = True
        st.session_state.warn_api_key_missing = False
    else:
        st.session_state.warn_api_key_missing = True
        

st.button('Run Pipeline :point_left:', on_click=click_button)

if st.session_state.warn_api_key_missing:
    st.text('Please input your OpenAI API key before running the pipeline!!')
if st.session_state.pipeline_clicked:
    st.write('The pipeline is running!')


st.header('Intermediate Steps', divider='blue')
if not st.session_state.pipeline_clicked:
    st.write('Please run the pipeline beforehand.')

if not st.session_state.pipeline_clicked:
    st.header('Output :mailbox_with_no_mail:', divider='blue')
    st.write('Please run the pipeline beforehand.')
else:
    st.header('Output :mailbox_with_mail:', divider='blue')
    # if st.checkbox('Show raw data'):
    #     st.subheader('Raw data')
    #     st.write(data)
    # @st.cache
    # def convert_df(df):
    #     # IMPORTANT: Cache the conversion to prevent computation on every rerun
    #     return df.to_csv().encode('utf-8')
    # csv = convert_df(my_large_df)
    st.download_button(
        label="Download data as CSV",
        data=None,
        file_name='large_df.csv',
        mime='text/csv',
    )