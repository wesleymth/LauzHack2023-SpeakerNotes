import os
import re
from typing import List

import joblib
import pandas as pd


def create_audio_clip_df(
    transcription: List[dict], subclip_info_df: pd.DataFrame
) -> pd.DataFrame:
    """_summary_

    Parameters
    ----------
    transcription : List[dict]
        _description_
    subclip_info_df : pd.DataFrame
        _description_

    Returns
    -------
    pd.DataFrame
        _description_
    """
    subclip_0_df = pd.DataFrame(transcription[0]["segments"])
    subclip_0_df["subclip_index"] = int(subclip_info_df["index"].iloc[0])
    subclip_0_df["start"] += subclip_info_df["start"].iloc[0]
    subclip_0_df["end"] += subclip_info_df["start"].iloc[0]
    for i in range(1, len(transcription)):
        subclip_i_df = pd.DataFrame(transcription[i]["segments"])
        subclip_i_df["subclip_index"] = int(subclip_info_df["index"].iloc[i])
        subclip_i_df["start"] += subclip_info_df["start"].iloc[i]
        subclip_i_df["end"] += subclip_info_df["start"].iloc[i]
        subclip_0_df = pd.concat([subclip_0_df, subclip_i_df], ignore_index=True)

    subclip_0_df = subclip_0_df.sort_values(by=["start"])
    subclip_0_df = subclip_0_df.reset_index(drop=True)
    return subclip_0_df


def remove_overlapping_segments(clip_df: pd.DataFrame) -> None:
    """_summary_

    Parameters
    ----------
    subclip_0_df : pd.DataFrame
        _description_
    """
    for i in range(1, len(transcription)):
        min_start_i = clip_df[(clip_df["subclip_index"] == i)]["start"].min()

        clip_df.drop(
            clip_df[
                (clip_df["start"] > min_start_i) & (clip_df["subclip_index"] < i)
            ].index,
            inplace=True,
        )


def read_ffmpeg_scene_detection_output(detected_frames_output: str) -> List[dict]:
    # Read the text file
    with open(detected_frames_output, "r") as file:
        content = file.read()
    # Extract frame numbers and pts_time numbers using regular expressions
    frame_numbers = re.findall(r"frame:(\d+)", content)
    # pts_time_numbers = re.findall(r'pts_time:(\d+\.\d+)', content)
    pts_time_numbers = re.findall(r"pts_time:(\d+)", content)

    return [
        {"frame_id": int(frame_numbers[i]), "pts_time": int(pts_time_numbers[i])}
        for i in range(len(frame_numbers))
    ]


def extract_png_file_names_and_ids(folder_path: str) -> dict:
    # Extract PNG file names and IDs
    file_names = []
    ids = []

    for file_name in os.listdir(folder_path):
        if file_name.endswith(".png"):
            file_names.append(file_name)
            img_id = file_name.split("img")[1].split(".png")[0]
            ids.append(int(img_id))

    # Print the file names and IDs
    return {"file_names": file_names, "ids": ids}


def filter_frame_list(frame_list: List[dict], extracted: dict) -> dict:
    return {
        frame["frame_id"]: frame["pts_time"]
        for frame in frame_list
        if frame["frame_id"] in extracted["ids"]
    }


def add_frame_ids_to_df(audio_clip_df: pd.DataFrame, filtered_dict: dict) -> None:
    # Sort the dictionary by timestamp value in ascending order
    sorted_dict = {
        k: v for k, v in sorted(filtered_dict.items(), key=lambda item: int(item[1]))
    }

    # Attribute the ID to each row in the DataFrame
    current_id = 0
    for idx, row in audio_clip_df.iterrows():
        timestamp = row["start"]
        for id_, ts in sorted_dict.items():
            if int(ts) > timestamp:
                break
            current_id = id_
        audio_clip_df.loc[idx, "frame_id"] = str(current_id)

    return audio_clip_df


def get_slide_text(audio_clip_df: pd.DataFrame) -> List[str]:
    return [
        "".join(audio_clip_df[audio_clip_df["frame_id"] == str(i)]["text"].to_list())
        for i in audio_clip_df["frame_id"].unique().tolist()
    ]


if __name__ == "__main__":
    transcription = joblib.load(
        "output/BIOENG320-lecture1(2023)_Prof-Yimon-AYE/transcription_biosyn_lecture_1.jl"
    )
    subclips_list = joblib.load(
        "output/BIOENG320-lecture1(2023)_Prof-Yimon-AYE/subcplips_info_biosyn_lecture_1.jl"
    )

    subclip_info_df = pd.DataFrame(subclips_list)
    audio_clip_df = create_audio_clip_df(
        transcription=transcription, subclip_info_df=subclip_info_df
    )

    remove_overlapping_segments(clip_df=audio_clip_df)

    detected_scenes_metadata = read_ffmpeg_scene_detection_output(
        detected_frames_output="output/BIOENG320-lecture1(2023)_Prof-Yimon-AYE/frame_metadata.txt"
    )

    detected_scenes_folder_path = (
        "output/BIOENG320-lecture1(2023)_Prof-Yimon-AYE/frames"
    )

    scene_file_names_and_ids = extract_png_file_names_and_ids(
        folder_path=detected_scenes_folder_path
    )

    filtered_frame_list = filter_frame_list(
        frame_list=detected_scenes_metadata, extracted=scene_file_names_and_ids
    )

    add_frame_ids_to_df(audio_clip_df=audio_clip_df, filtered_dict=filtered_frame_list)

    slide_text = get_slide_text(audio_clip_df=audio_clip_df)

    joblib.dump(
        slide_text, "output/BIOENG320-lecture1(2023)_Prof-Yimon-AYE/slide_text.jl"
    )
