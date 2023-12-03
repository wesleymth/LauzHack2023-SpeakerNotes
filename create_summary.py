import PyPDF2
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTFigure
from pdf2image import convert_from_path
import os
import pytesseract
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

def generate_slide_summary(reader, slide_number : int) -> str:
    page = reader.pages[slide_number]
    text = page.extract_text((slide_number, 0))
    
    return text

def crop_image(element, pageObj):
    # Get the coordinates to crop the image from the PDF
    [image_left, image_top, image_right, image_bottom] = [element.x0,element.y0,element.x1,element.y1] 
    # Crop the page using coordinates (left, bottom, right, top)
    pageObj.mediabox.lower_left = (image_left, image_bottom)
    pageObj.mediabox.upper_right = (image_right, image_top)
    # Save the cropped page to a new PDF
    cropped_pdf_writer = PyPDF2.PdfWriter()
    cropped_pdf_writer.add_page(pageObj)
    # Save the cropped PDF to a new file
    with open('cropped_image.pdf', 'wb') as cropped_pdf_file:
        cropped_pdf_writer.write(cropped_pdf_file)

# Create a function to convert the PDF to images
def convert_to_images(input_file):
    images = convert_from_path(input_file)
    return images[0]

# Create a function to read text from images
def image_to_text(img):
    text = pytesseract.image_to_string(img)
    return text

def extract_all_text (pdf_path = '01-NX422 keyconcepts.pdf') :

    pdfReaded = PyPDF2.PdfReader(pdf_path)

    text_per_page = {}
    # We extract the pages from the PDF
    for pagenum, page in enumerate(extract_pages(pdf_path)):
        
        print('Page number: ', pagenum)
        
        # Initialize the variables needed for the text extraction from the page
        pageObj = pdfReaded.pages[pagenum]
        page_text = []
        text_from_images = []
        page_content = []

        # Find all the elements
        page_elements = [(element.y1, element) for element in page._objs]
        # Sort all the elements as they appear in the page 
        page_elements.sort(key=lambda a: a[0], reverse=True)
        
        text = generate_slide_summary(pdfReaded, pagenum)
        text = text.split("\n")
        

        # Find the elements that composed a page
        for component in page_elements:
            element = component[1]

            # Check the elements for images
            if isinstance(element, LTFigure):
                # Crop the image from the PDF
                crop_image(element, pageObj)
                image = convert_to_images('cropped_image.pdf')
                # Extract the text from the image
                image_text = image_to_text(image)
                text_from_images.append(image_text)
                page_content.append(image_text)

        # Create the key of the dictionary
        dctkey = 'Page_'+str(pagenum)
        # Add the list of list as the value of the page key
        text_images = [text for text in text_from_images if text != '']
        page_text.append(text_images)
        text_per_page[dctkey]= [text, text_images]#, page_content]
        
    os.remove('cropped_image.pdf')
    return text_per_page



if __name__ == "__main__":
    text = extract_all_text("slides_AXA_cropped.pdf")
    print(text)
