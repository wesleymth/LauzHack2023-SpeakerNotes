from moviepy.editor import AudioFileClip
from transformers import pipeline
import os
import re
import pandas as pd
import openai


def MP4ToMP3(mp4: str, mp3: str) -> None:
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
    
    
def transcribe_audio(audio_file:str, whisper_model:str="openai/whisper-medium.en")->dict:
    pipe = pipeline(
        "automatic-speech-recognition", 
        model=whisper_model,
        chunk_length_s=30,
    )
    transcription = pipe(audio_file, return_timestamps=True)
    return transcription


def detect_frame_changes(input_video:str, detection_threshold:float=0.03, scene_detection_output:str="scene_detection_output")->None:
    os.makedirs(scene_detection_output, exist_ok=True)
    os.system(
        f"""ffmpeg -i '{input_video}' -filter_complex "select='gt(scene,{detection_threshold})',metadata=print:file='{os.path.join(scene_detection_output, "detected_frames.txt")}'" -start_number 0 -fps_mode vfr {os.path.join(scene_detection_output, "frame%03d.png")}"""
    )
    

def read_ffmpeg_scene_detection_output(detected_frames_output: str) -> list[dict]:
    # Read the text file
    with open(detected_frames_output, "r") as file:
        content = file.read()
    # Extract frame numbers and pts_time numbers using regular expressions
    frame_numbers = re.findall(r"frame:(\d+)", content)
    # pts_time_numbers = re.findall(r'pts_time:(\d+\.\d+)', content)
    pts_time_numbers = re.findall(r"pts_time:(\d+.\d+)", content)

    return [
        {"frame_id": int(frame_numbers[i]), "pts_time": float(pts_time_numbers[i])}
        for i in range(len(frame_numbers))
    ]
    

def create_frame_transition_df(
    detected_frames_file:str=os.path.join("scene_detection_output", "detected_frames.txt"),
    same_transition_time_threshold:float=1
)->pd.DataFrame:
    frame_transition_df = pd.DataFrame(read_ffmpeg_scene_detection_output(detected_frames_file))
    mask = (frame_transition_df['pts_time'].diff() > same_transition_time_threshold).to_numpy()
    mask[0] = True
    frame_transition_df = frame_transition_df[mask]
    return frame_transition_df


def wrap_transciption_in_df(transcription:dict)->pd.DataFrame:
    time_text_df = pd.DataFrame(transcription["chunks"])
    return time_text_df


def create_slide_transitions_df(
    frame_transition_df:pd.DataFrame,
    time_text_df:pd.DataFrame,
)->pd.DataFrame:

    slide_timestamps = ([0.0] + frame_transition_df["pts_time"].tolist() + [time_text_df["timestamp"].iloc[-1][-1]])
    slide_transitions = pd.DataFrame(
        [
            {"timestamps" : (start, end), "slide_num" : slide_num, } 
            for slide_num, (start, end) in enumerate(zip(slide_timestamps, slide_timestamps[1:]), start=1)
        ]
    )
    return slide_transitions

def assign_slide_text(time_text_df, slide_transitions):
    idx_slide = 0
    for index, text_row in time_text_df.iterrows():
        if text_row['timestamps'][1] > slide_transitions['timestamps'][idx_slide][1]:
            idx_slide+=1
        slide_transitions['slide_text'][idx_slide] += text_row['text']

    return slide_transitions

def written_text_slides(slide_info):
        filtered_page_dict = {key: value for key, value in slide_info.items() if 'Page_4' <= key <= 'Page_9'}
        first_values_list = [value[0] for value in filtered_page_dict.values()]
        return pd.DataFrame({'Written_text': first_values_list})

def generate_response(prompt):
    messag=[{"role": "system", "content": "You are a chatbot"}]
    
    ## build a chat history: you can CONDITION the bot on the style of replies you want to see - also getting weird behaviors... such as KanyeGPT
    history_bot = ["Yes, I'm ready, I will only output the asked without adding any extra information."]
    
    # ask ChatGPT to return STRUCTURED, parsable answers that you can extract easily - often better providing examples of desired behavior (1-2 example often enough)
    history_user = ["I'll give you two texts (i.e., for each of my messages) you will summarize the first one wihtout repeting infomation that can be found in the second one. \n\nfor example:\nmy input = First Text:  I have a background in computer vision, so I played a lot with mobile apps and previous hackathon challenges. I missed there. Previous hackathon challenges used to be around computer vision. You can do a lot of cool stuff with them. You can still do them today, but surprise, you don't have to do them manually. You can just ask the API to do it for you. \n Second Text: ['##ch_internal##', 'DOCUMENT UNDERSTANDING•Classification•Field extraction (OCR + HWR)•Semantic understanding•Process automation•Videos are also documents!•Your class notes are also docs!'] \n\nyour output =   \nready to start?"]
    
    for user_message, bot_message in zip(history_user, history_bot):
        messag.append({"role": "user", "content": str(user_message)})
        messag.append({"role": "system", "content": str(bot_message)})
    messag.append({"role": "user", "content": str(prompt)})

    response = openai.ChatCompletion.create(
        
    # please use gtp3.5 although gpt4 is much better for $$
    model="gpt-3.5-turbo",
        messages=messag
    )
    result = ''
    for choice in response.choices:
        result += choice.message.content
    history_bot.append(result)
    history_user.append(str(prompt))
    return result


if __name__ == "__main__":
    video_file = "ShortVideo.mov"
    audio_file = "ShortVideo.mp3"
    
    MP4ToMP3(video_file, audio_file)
    transcription = transcribe_audio(audio_file)
    detect_frame_changes(video_file)
    frame_transition_df = create_frame_transition_df()
    time_text_df = wrap_transciption_in_df(transcription)
    slide_transitions = create_slide_transitions_df(frame_transition_df, time_text_df)
    slide_transitions = assign_slide_text(time_text_df, slide_transitions)
    slide_transitions['slide_text'].to_csv('transcript_audio.txt', index=False, header=False, sep='\t')

    slide_info = pd.read_pickle('info_slides.pkl')
    
    transcript_slides = written_text_slides(slide_info)

    transcript_slides.to_csv('transcript_slides.txt', index=False, header=False, sep='\t')
    '''
    # OpenAI
    try:
        with open('keys.txt', 'r') as file:
            openai_key = file.read()
    except Exception as e:
            print(e)

    openai.api_key = openai_key
    mykey = openai_key

    print(generate_response("The power of human language and thought arises from it"))
    '''
    # time_text_df.to_csv("time_text_df.csv")
    # slide_transitions.to_csv("slide_transitions.csv")
    
