from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import AnnotationBuilder
import PyPDF2
from typing import List
import joblib

def annotate_pdf_blank_pages(pdf_path :str, annotation_text :List[str], output_path :str)->None:
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

        # Create a blank page with the same size as the original page
        blank_page = PyPDF2.PageObject.create_blank_page(
            None, page.mediabox.width, page.mediabox.height
        )
        writer.add_page(blank_page)

        # Create the annotation and add it
        annotation = AnnotationBuilder.free_text(
            annotation_text[page_num],
            rect=(0, 0, page.mediabox.width, page.mediabox.height),
            font="Arial",
            bold=True,
            italic=True,
            font_size="20pt",
            font_color="00ff00",
            border_color="0000ff",
            background_color="cdcdcd",
        )
        writer.add_annotation(page_number=-1, annotation=annotation)

    # Write the annotated file to disk
    with open(output_path, "wb") as fp:
        writer.write(fp)
        
if __name__ == "__main__":
    slide_text = joblib.load("output/lowering_threshold/slide_text.jl")
    pdf_path = 'data/BIOENG320-2023Apr24_lecture-finalized.pdf'
    annotate_pdf_blank_pages(
        pdf_path=pdf_path,
        annotation_text=slide_text,
        output_path="output/lowering_threshold/annotated.pdf",
    )
    