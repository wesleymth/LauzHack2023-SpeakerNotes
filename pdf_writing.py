import re
from typing import List

import joblib
import PyPDF2
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import AnnotationBuilder


def line_break_on_full_stop(string: str) -> str:
    # Split the text only at periods followed by a space and a capital character, i.e. the end of a sentence
    return ".\n".join(re.split(r"\.\s(?=[A-Z])", string))


def split_string_into_sentences(string: str, max_length: int) -> list:
    # Split the string into sentences using regular expressions
    sentences = re.split(r"(?<=[.!?])\s+", string)

    # Create a list to store the smaller substrings
    substrings = []

    # Iterate over each sentence and split it into smaller substrings
    current_substring = ""
    for sentence in sentences:
        # Check if adding the current sentence to the current substring exceeds the maximum length
        if len(current_substring) + len(sentence) <= max_length:
            current_substring = current_substring + " " + sentence
        else:
            current_substring = line_break_on_full_stop(current_substring)
            substrings.append(current_substring)
            current_substring = sentence

    # Add the last remaining substring
    if current_substring:
        current_substring = line_break_on_full_stop(current_substring)
        substrings.append(current_substring)

    if substrings[0] == "":
        substrings = substrings[1:]

    return substrings


def annotate_pdf_blank_pages(
    pdf_path: str, annotation_text: List[str], output_path: str
) -> None:
    """_summary_

    Parameters
    ----------
    pdf_path : str
        _description_
    text : List[str]
        _description_
    output_path : str
        _description_
    """
    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        writer.add_page(page)

        for annotation_text_ in annotation_text[page_num]:
            # Create a blank page with the same size as the original page
            blank_page = PyPDF2.PageObject.create_blank_page(
                None, page.mediabox.width, page.mediabox.height
            )
            writer.add_page(blank_page)

            # Remove the leading spaces from whisper transcripts
            if annotation_text_[:2] == "  ":
                annotation_text_ = annotation_text_[2:]

            # Create the annotation and add it
            annotation = AnnotationBuilder.free_text(
                annotation_text_,
                rect=(0, 0, page.mediabox.width, page.mediabox.height),
                font="Arial",
                bold=True,
                italic=True,
                font_size="20pt",
                font_color="00ff00",
                border_color="0000ff",
                background_color="ffffff",
            )
            writer.add_annotation(page_number=-1, annotation=annotation)

    # Write the annotated file to disk
    with open(output_path, "wb") as fp:
        writer.write(fp)


if __name__ == "__main__":
    slide_text = joblib.load(
        "output/BIOENG320-lecture1(2023)_Prof-Yimon-AYE/slide_text.jl"
    )
    pdf_path = "data/syn_bio_rna_lecture_1/BIOENG320-2023Apr17_finalized.pdf"
    max_length = 4500

    slide_text = [split_string_into_sentences(text, max_length) for text in slide_text]

    annotate_pdf_blank_pages(
        pdf_path=pdf_path,
        annotation_text=slide_text,
        output_path=f"output/BIOENG320-lecture1(2023)_Prof-Yimon-AYE/lecture_1_annotated.pdf",
    )
