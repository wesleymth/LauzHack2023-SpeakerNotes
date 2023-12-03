from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTFigure
import numpy as np
import fitz
from PIL import Image
from scipy import signal
import matplotlib.pyplot as plt
# import gtp_summary as gtp

def parse_layout(layout):
    """Function to recursively parse the layout tree."""
    obj = []
    for lt_obj in layout:
        if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine) or isinstance(lt_obj, LTFigure):
            obj.append(list(lt_obj.bbox))
    return obj

    
def find_object(path) :
    fp = open(path, 'rb')
    parser = PDFParser(fp)
    doc = PDFDocument(parser)

    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    full_obj = {}
    for i, page in enumerate(PDFPage.create_pages(doc)):
        interpreter.process_page(page)
        layout = device.get_result()
        obj = parse_layout(layout)
        full_obj[i] = obj
    return full_obj

def generate_mask(path, full_obj):

    pdf_document = fitz.open(path)
    mask_dict = {}

    for page_num in range(pdf_document.page_count):
        print('Page number: ', page_num)
        page = pdf_document[page_num]
        image_list = page.get_pixmap()
        # Convert the image to a format that matplotlib can handle
        img = Image.frombytes("RGB", [image_list.width, image_list.height], image_list.samples)
        img = img.convert("RGB")
        mask = np.ones((img.size[1],img.size[0]), dtype=np.uint8)

        # Define the bounding box coordinates (x0, y0, x1, y1)
        for bbox in full_obj[page_num] :
            
            mask[int(img.size[1]-bbox[3]):int(img.size[1]-bbox[1]), int(bbox[0]):int(bbox[2])] = 0
        mask_dict[page_num] = mask
            
    return mask_dict

def find_largest_square_helper(a):
    for i in range(2, min(a.shape)): # changed this to 2, because the 1 is trivial
        kernel = np.ones((i, i), dtype=int)
        if signal.convolve(a, kernel, mode = "valid").max() != i**2:
            return(i-1), signal.convolve(a,  np.ones((i-1, i-1), dtype=int), mode = "valid")


def generate_rectangle_res(a):
    max_square_size, conv = find_largest_square_helper(a)
    opt_y, opt_x = np.where(conv == max_square_size**2) # Find the optimum indexes

    # print(f"{opt_x=}, {opt_y=}")

    # Find the unique indexes and their counts
    unique_y, count_y = np.unique(opt_y, return_counts=True)
    unique_x, count_x = np.unique(opt_x, return_counts=True)

    # print(f"{count_x=}, {count_y=}")

    if np.max(count_y) > np.max(count_x): # If you have more duplicates in the y dimension (better to expand)
        best_y_index = unique_y[np.argmax(count_y)] # The index to expand on 
        
        first_x_index =  opt_x[np.where(opt_y == best_y_index)[0][0]] 
        last_x_index = opt_x[np.where(opt_y == best_y_index)[0][-1]]
        
        # print("y")
        
        
        # a[best_y_index:best_y_index+max_square_size, first_x_index:last_x_index+max_square_size] = 3
        return {
            "x0":first_x_index,
            "x1":last_x_index+max_square_size,
            "y0":best_y_index,
            "y1":best_y_index+max_square_size,
        }
    else:
        best_x_index = unique_x[np.argmax(count_x)] # The index to expand on 
        
        first_y_index =  opt_y[np.where(opt_x == best_x_index)[0][0]] 
        last_y_index = opt_y[np.where(opt_x == best_x_index)[0][-1]]
        # print("x")
        
        return {
            "x0":best_x_index,
            "x1":best_x_index+max_square_size,
            "y0":first_y_index,
            "y1":last_y_index+max_square_size,
        }
        
        # a[first_y_index:last_y_index+max_square_size, best_x_index:best_x_index+max_square_size] = 3
   
def extract_many_rectangle(mask, nb_of_rectangle) :
    dict_rect = []
    msk = mask.copy()
    
    for i in range(nb_of_rectangle) :
    
        res = generate_rectangle_res(msk)
        dict_rect.append(res)
        msk[res["y0"]:res["y1"], res["x0"]:res["x1"]] = 0
    return dict_rect
 
def choose_rect (rect_list, text, font, fs) :
    
    font = fitz.Font(font)
    x = text.split("\n")
    
    fs = 10
    i = 0
    j = 0
    text_list = []
    rect_l = []

    while len(rect_list) > j  and len(x)> i :
        rect = [rect_list[j]["x0"]+5, rect_list[j]["y0"]+5, rect_list[j]["x1"]-5, rect_list[j]["y1"]-5]
        available_line = (rect[3]-rect[1]) / ((font.ascender - font.descender) * fs)
        nb_line = 0
        current = ""

        while available_line >  np.ceil(nb_line) and len(x)> i :
        
            if current == "" :
                current = x[i]
            else :
                current = current + "\n" + x[i]
                
            tl = font.text_length(current, fontsize=fs)
            nb_line += tl / (rect[2]-rect[0])
            i += 1
            
        text_list.append(current)
        rect_l.append(rect)
        j += 1
    return text_list, rect_l

def add_all_notes_slides(page, text_list, rect_list, fontname, color):
    for rect, text in zip(rect_list, text_list):
        write_slides(page, rect, text, color, fontname)
    
    
def write_slides (page, rect, text, rgb_color, fontname="Helv" ) :
    page.insert_textbox(rect, text,  fontsize=9, fontname=fontname, fontfile=None, color=rgb_color/255, rotate=0)
    
if __name__ == "__main__":


    full_obj = find_object("../01-NX422 keyconcepts_organized.pdf")

    mask_dict = generate_mask("../01-NX422 keyconcepts_organized.pdf", full_obj)
    
    key_openai = "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"

    #prompt = gtp.generate_prompt('transcript_audio.txt','transcript_slides.txt',False)
    blank_space_dict = {}
    
    filename = '../01-NX422 keyconcepts_organized.pdf'
    doc = fitz.open(filename) 
    for key, mask in mask_dict.items():
        res = extract_many_rectangle(mask, 3)
        blank_space_dict[key] = res
        text = "adjkasdjkadjkfsjlkfnsshchescuhriuvhuiegu \n sfbgjkhcudbcjneuchjdkmfkhiuc hckjfnnjk " #gtp.generate_response(prompt[key], key_openai) 
        
        txt, rect = choose_rect(res, text, "helv", 10)
        print(rect)

        page = doc[key] 

        add_all_notes_slides(page, txt, rect, "Helv", color = 0)
    doc.save("output23.pdf")  # save to new file
               
    # import matplotlib.pyplot as plt

    # for (k1, mask), (k1, ress) in zip(mask_dict.items(),blank_space_dict.items()) :
    #     plt.imshow(mask, cmap='gray')
    #     for res in ress :
    #         plt.plot(res["x0"], res["y0"], 'ro')
    #         plt.plot(res["x0"], res["y1"], 'ro')
    #         plt.plot(res["x1"], res["y0"], 'ro')
    #         plt.plot(res["x1"], res["y1"], 'ro')
    #     plt.show()

