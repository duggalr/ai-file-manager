import os
from pdf2image import convert_from_path
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError
import docx
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import ImageFormatter
import openpyxl
import subprocess


def _is_image_file(file_path):
    """
    Check if a given file is an image.

    :param file_path: Path to the file.
    :return: True if the file is an image, False otherwise.
    """
    try:
        with Image.open(file_path) as img:
            # Attempt to load the image (this verifies it's an image)
            img.verify()
        return True
    except (IOError, UnidentifiedImageError):
        return False

def _pdf_to_image(pdf_path, output_image_path):
    pages = convert_from_path(pdf_path, first_page=1, last_page=1)
    first_page_image = pages[0]
    first_page_image.save(output_image_path, format='PNG')
    return output_image_path

def _txt_to_image(txt_path, output_image_path):
    with open(txt_path, 'r') as file:
        text = file.read()

    image = Image.new('RGB', (1000, 1000), 'white')
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text((10, 10), text, font=font, fill='black')
    image = image.crop(image.getbbox())
    image.save(output_image_path)
    return output_image_path

def docx_to_image(docx_path, output_image_path):
    doc = docx.Document(docx_path)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])

    image = Image.new('RGB', (1000, 1000), 'white')
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text((10, 10), text, font=font, fill='black')
    image = image.crop(image.getbbox())
    image.save(output_image_path)
    return output_image_path

def xlsx_to_image(xlsx_path, output_image_path):
    wb = openpyxl.load_workbook(xlsx_path)
    sheet = wb.active
    text = ""
    for row in sheet.iter_rows(min_row=1, max_row=10, values_only=True):
        text += "\t".join([str(cell) if cell is not None else "" for cell in row]) + "\n"

    image = Image.new('RGB', (1000, 1000), 'white')
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text((10, 10), text, font=font, fill='black')
    image = image.crop(image.getbbox())
    image.save(output_image_path, format='PNG')
    return output_image_path

def image_to_image(input_image_path, output_image_path=None):
    """
    Opens an image file and saves it in its original format or a specified format.

    :param input_image_path: Path to the input image file.
    :param output_image_path: Path to save the output image. If None, saves in the original format.
    :return: Path to the saved image file.
    """
    image = Image.open(input_image_path)
    # image_format = image.format
 
    if output_image_path is None:
        base_name = os.path.splitext(input_image_path)[0]
        # output_image_path = f"{base_name}.{image_format.lower()}"
        output_image_path = f"{base_name}.png"

    # image.save(output_image_path, format=image_format)
    image.save(output_image_path, format='PNG')
    return output_image_path

def py_to_image(py_path, output_image_path):
    with open(py_path, 'r') as file:
        code = file.read()

    formatter = ImageFormatter(
        line_numbers=True, style='colorful', image_format='PNG'
    )
    with open(output_image_path, 'wb') as img_file:
        highlight(code, PythonLexer(), formatter, img_file)
    
    return output_image_path

def pages_to_image(pages_path, output_image_path):
    # Convert .pages to .pdf using unoconv (requires LibreOffice)
    pdf_path = pages_path.replace('.pages', '.pdf')
    subprocess.run(['unoconv', '-f', 'pdf', pages_path])
    return _pdf_to_image(pdf_path, output_image_path)


def generate_image_for_file(input_file_path, output_file_path):
    _, file_extension = os.path.splitext(input_file_path)

    if _is_image_file(input_file_path):
        print("--- file is image...")
        return image_to_image(input_file_path, output_file_path)
    else:
        if file_extension.lower() == '.pdf':
            return _pdf_to_image(input_file_path, output_file_path)

        elif file_extension.lower() == '.txt':
            return _txt_to_image(input_file_path, output_file_path)

        elif file_extension.lower() == '.py':
            return py_to_image(input_file_path, output_file_path)

        elif file_extension.lower() == '.docx':
            return docx_to_image(input_file_path, output_file_path)

        elif file_extension.lower() == '.xlsx':
            return xlsx_to_image(input_file_path, output_file_path)
        
        # TODO:
            #csv, other coding file extensions, ignoring all hidden file types

        # elif file_extension.lower() == '.pages':
        #     return pages_to_image(input_file_path, output_file_path)
        


# input_path = '/Users/rahulduggal/Documents/new_projects/ai_file_manager/backend/views.py'
# output_path = 'views_py_screenshot.png'
# py_to_image(
#     input_path, output_path
# )

output_dir_fp = '/Users/rahulduggal/Documents/new_projects/ai_file_manager/scripts/test_output_files'
files = [
    # TODO: start here by parsing all the different file types and generating images for each; go from there...
    '/Users/rahulduggal/Downloads/91a2de6f-c04f-4f69-a841-0fe328376f5c.png',
    # '/Users/rahulduggal/Downloads/97029cc4-7ea7-4a82-92af-2e935dd5dc5d.png',
    # '/Users/rahulduggal/Downloads/Studio Innate Freebies/Nike-Blazer-By-Studio-Innate.psd',
    # '/Users/rahulduggal/Desktop/crypto_readings/The emerging tech guide for independent artists.pdf',
    # '/Users/rahulduggal/Desktop/backend_arxivpaper_202406121355.csv',
    # '/Users/rahulduggal/Downloads/File Storage - Cost Breakdown by Compartment (OCI).xlsx'
]

for full_fp in files:
    print(f"On File: {full_fp}")
    fn_full = os.path.basename(full_fp)
    f_just_file_name = fn_full.split('.')[0]
    # fn_dir_name = os.path.dirname(full_fp)
    output_file_path = os.path.join(output_dir_fp, f_just_file_name)
    # print(output_file_path)
    generate_image_for_file(
        input_file_path = full_fp,
        output_file_path = output_file_path
    )
