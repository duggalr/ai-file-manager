import os
import platform
from pdf2image import convert_from_path
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError



def is_hidden(filepath):
    # Check for Unix-based systems (Linux/MacOS)
    if platform.system() != 'Windows':
        return os.path.basename(filepath).startswith('.')
    # Check for Windows
    else:
        try:
            import ctypes
            attrs = ctypes.windll.kernel32.GetFileAttributesW(str(filepath))
            return attrs != -1 and (attrs & 2)  # FILE_ATTRIBUTE_HIDDEN == 2
        except Exception as e:
            print(f"Error checking hidden attribute: {e}")
            return False

def _is_valid_file(filepath):
    if is_hidden(filepath):
        return False
    
    file_extension = filepath.split('.')[-1]
    file_size_in_bytes = os.path.getsize(filepath)

    if file_extension == 'pdf': # we will process large pdf files
        valid_file_size_bytes = 50000000
    else:
        valid_file_size_bytes = 10000000

    if file_size_in_bytes > valid_file_size_bytes:
        return False
    
    return True

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

def _image_to_image(input_fp, output_fp):
    image = Image.open(input_fp)
    image.save(output_fp)
    return output_fp

def _pdf_to_image(input_fp, output_fp):
    pages = convert_from_path(input_fp, first_page=1, last_page=1)
    first_page_image = pages[0]

    # output_fp_list = os.path.splitext(output_fp)
    # output_file_extension = output_fp_list[-1]

    print(f"saving file path: {output_fp}")

    first_page_image.save(output_fp)
    return output_fp

def _text_to_image(input_file_path, output_file_path):
    with open(input_file_path, 'r') as file:
        text = file.read()

    width, height = 800, 600  # You can adjust these values as needed
    image = Image.new('RGB', (width, height), color='white')

    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("arial.ttf", size=20)
    except OSError:
        font = ImageFont.load_default()

    margin = 10
    offset = 10
    for line in text.splitlines():
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        draw.text((margin, offset), line, font=font, fill="black")
        offset += text_height + 5
        if offset > height - margin:
            break

    image.save(output_file_path)
    return output_file_path


def main(input_file_path, output_file_path):
    """
    """
    file_extension = input_file_path.split('.')[-1]
    is_image = _is_image_file(input_file_path)

    if is_image:
        _image_to_image(input_file_path, output_file_path)
    else:
        if file_extension == 'pdf':
            _pdf_to_image(
                input_file_path, output_file_path
            )
        else:
            _text_to_image(
                input_file_path, output_file_path
            )



if __name__ == "__main__":

    output_dir_fp = '/Users/rahulduggal/Documents/new_projects/ai_file_manager/scripts/test_output_files'
    file_list = [
        # # '/Users/rahulduggal/Downloads/91a2de6f-c04f-4f69-a841-0fe328376f5c.png',
        # # '/Users/rahulduggal/Desktop/crypto_readings/The emerging tech guide for independent artists.pdf',
        # '/Users/rahulduggal/Documents/ml-team-work/personal-reader/text_files/todo.txt',
        # '/Users/rahulduggal/Documents/ml-team-work/personal-reader/reader_backend/manage.py',
        # '/Users/rahulduggal/Documents/ml-team-work/personal-reader/reader_extension/background.js',
        # '/Users/rahulduggal/Documents/ml-team-work/personal-reader/reader_extension/manifest.json',
        # '/Users/rahulduggal/Documents/ml-team-work/personal-reader/reader_extension/jquery-3.7.1.js',
        # '/Users/rahulduggal/Documents/ml-team-work/personal-reader/reader_extension/hello.html',
        # '/Users/rahulduggal/Documents/ml-team-work/alzheimer_detection/kaggle_ad/data_exploration.ipynb',
        
        # '/Users/rahulduggal/Documents/ml-team-work/alzheimer_detection/ad-venv/pyvenv.cfg',
        # '/Users/rahulduggal/Documents/notebooks/mrp_2023-05-01.csv',
        # '/Users/rahulduggal/Documents/ml-team-work/final_rv.csv',
        # '/Users/rahulduggal/Desktop/tmp_branch_two/parse_pdf.py',
        # '/Users/rahulduggal/Desktop/main_screenshots_one/Screenshot 2024-07-10 at 10.15.52 AM.png',
        # '/Users/rahulduggal/Library/CloudStorage/GoogleDrive-rahul@lambdal.com/My Drive/maxio_bad_debt_customers_output (3).csv'

        # '/Users/rahulduggal/Desktop/ll-master/www/frontend_log.json',
        # '/Users/rahulduggal/Desktop/ll-master/www/svr/fraud.py',
        # '/Users/rahulduggal/Desktop/ll-master/www/svr/tools/__init__.py',
        # '/Users/rahulduggal/Desktop/ll-master/www/setup.cfg',
        # '/Users/rahulduggal/Desktop/ll-master/README.md',
        # '/Users/rahulduggal/Desktop/Nicolas Vandeput - Inventory Optimization_ Models and Simulations-De Gruyter (2020).pdf',
        # '/Users/rahulduggal/Desktop/ll-master/frontend/src/cloud/strings.tsx',
        # '/Users/rahulduggal/Desktop/ll-master/frontend/src/cloud/types.ts',

        '/Users/rahulduggal/Desktop/ll-master/frontend/src/cloud/components/BillingAddressEditForm.module.scss',
        '/Users/rahulduggal/Desktop/ll-master/frontend/src/cloud/api.ts',
        '/Users/rahulduggal/Desktop/ll-master/.flake8'
    ]

    # fp = '/Users/rahulduggal/Desktop/ll-master/www/.coveragerc'
    # hidden_file = is_hidden(fp)
    # print(f"hidden-file: {hidden_file}")

    could_not_process_file_list = []
    for full_fp in file_list:
        print(f"On File: {full_fp}")

        file_is_valid = _is_valid_file(full_fp)
        if file_is_valid:
            fn_full = os.path.basename(full_fp)
            f_just_file_name = fn_full.split('.')[0]
            output_file_path = os.path.join(output_dir_fp, f_just_file_name)
            main(
                input_file_path = full_fp,
                output_file_path = output_file_path
            )
        else:
            could_not_process_file_list.append(full_fp)

    print(f"Could not process files: {could_not_process_file_list}")

    # TODO: fix above issue (see cmd) and go from there
        # target --> aim to get V1 robust file to screenshot + UI complete
        # after will be --> efficiency/speed of processing, etc.
    
    #     hidden_file = is_hidden(full_fp)
        
    #     if hidden_file:
    #         could_not_process_file_list.append(hidden_file)
    #     else:
    #         fn_full = os.path.basename(full_fp)
    #         f_just_file_name = fn_full.split('.')[0]
    #         output_file_path = os.path.join(output_dir_fp, f_just_file_name)
    #         output_file_path = f"{output_file_path}.png"

    #         print(f"Output File Path: {output_file_path}")
    #         main(
    #             input_file_path = full_fp,
    #             output_file_path = output_file_path
    #         )

