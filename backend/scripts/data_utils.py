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

    image.save(output_file_path, format='PNG')
    return output_file_path

def _main_file_to_image(input_file_path, output_file_path):
    """
    """
    file_extension = input_file_path.split('.')[-1]
    is_image = _is_image_file(input_file_path)

    if is_image:
        return _image_to_image(input_file_path, output_file_path)
    else:
        if file_extension == 'pdf':
            return _pdf_to_image(
                input_file_path, output_file_path
            )
        else:
            return _text_to_image(
                input_file_path, output_file_path
            )


def main(directory_fp):
    could_not_process_file_list = []
    output_file_path_list = []    
    for root, dirs, files in os.walk(directory_fp):
        for file in files:
            file_path = os.path.join(root, file)
            file_is_valid = _is_valid_file(file_path)
            if file_is_valid:
                fn_full = os.path.basename(file_path)
                f_just_file_name = fn_full.split('.')[0]
                output_file_path = os.path.join(output_dir_fp, f_just_file_name)
                output_file_path = f"{output_file_path}.png"
                # print(f"Input File: {file_path} | Output File: {output_file_path}")
                
                
                return_output_image_fp = _main_file_to_image(
                    input_file_path = file_path,
                    output_file_path = output_file_path
                )

                output_file_path_list.append(return_output_image_fp)
            else:
                could_not_process_file_list.append(file_path)
    
    di = {
        'output_file_path_list': output_file_path_list,
        'could_not_process_file_list': could_not_process_file_list
    }
    return di


current_script_fp = os.path.abspath(__file__)
current_script_directory = os.path.dirname(current_script_fp)
output_dir_fp = os.path.join(current_script_directory, 'test_output_files')

# user_directory_fp = '/Users/rahulduggal/Desktop/companion_old_files/new_old_one'
# main(
#     directory_fp = user_directory_fp
# )