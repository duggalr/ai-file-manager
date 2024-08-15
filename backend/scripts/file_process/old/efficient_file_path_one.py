import os
import json
import base64
import concurrent.futures
import datetime
from functools import partial
import platform
from pdf2image import convert_from_path
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError
# from . import data_utils, open_ai_wrapper, prompts_wrapper
import data_utils, open_ai_wrapper, prompts_wrapper


class File(models.Model):
    """
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # user_directory_file_path = models.TextField()    
    
    file_path = models.TextField()
    file_name = models.TextField(blank=True, null=True)
    
    entity_type = models.TextField()
    primary_category = models.TextField()
    sub_categories = models.JSONField()
    
    file_size_in_bytes = models.IntegerField(blank=True, null=True)
    file_last_access_time = models.DateTimeField(blank=True, null=True)
    file_created_at_date_time = models.DateTimeField(blank=True, null=True)
    file_modified_at_date_time = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    directory_object = models.ForeignKey(Directory, on_delete=models.CASCADE, blank=True, null=True)


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

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

def get_screenshot(directory_fp):
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


def process_single_file(img_fp, category_prompt, op_wrapper):
    try:
        # Encode image to base64
        base64_image = encode_image(img_fp)
        image_open_ai_file_path = f"data:image/jpeg;base64,{base64_image}"

        # Generate file category JSON using OpenAI API
        response = op_wrapper.generate_file_category_json(
            image_file_path=image_open_ai_file_path,
            prompt=category_prompt,
        )
        json_response_data = json.loads(response)

        # Collect file metadata
        file_size = os.path.getsize(img_fp)
        last_access_time = datetime.datetime.fromtimestamp(os.path.getatime(img_fp)).strftime('%Y-%m-%d %H:%M:%S')
        last_modified_time = datetime.datetime.fromtimestamp(os.path.getmtime(img_fp)).strftime('%Y-%m-%d %H:%M:%S')
        creation_time = datetime.datetime.fromtimestamp(os.path.getctime(img_fp)).strftime('%Y-%m-%d %H:%M:%S')
        current_image_file_name = os.path.basename(img_fp)

        # Add metadata to the response
        json_response_data.update({
            'current_image_file_path': img_fp,
            'current_image_file_name': current_image_file_name,
            'file_size': file_size,
            'last_access_time': last_access_time,
            'last_modified_time': last_modified_time,
            'creation_time': creation_time
        })

        return json_response_data
    except Exception as e:
        print(f"Error processing file {img_fp}: {str(e)}")
        return None

def main(user_directory_file_path):
    file_path_output_dict = data_utils.main(directory_fp=user_directory_file_path)
    output_file_path_list = file_path_output_dict['output_file_path_list']
    could_not_process_file_list = file_path_output_dict['could_not_process_file_list']
    
    print(f"Could not process file paths: {could_not_process_file_list}")

    category_prompt = prompts_wrapper.Prompts.CATEGORIZATION_PROMPT_V1.value
    op_wrapper = open_ai_wrapper.OpenAIWrapper()

    # Using ThreadPoolExecutor for I/O-bound tasks like file processing
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Prepare the worker function with partial application of common arguments
        process_worker = partial(process_single_file, category_prompt=category_prompt, op_wrapper=op_wrapper)
        
        # Map the worker across all file paths concurrently
        results = list(executor.map(process_worker, output_file_path_list))

    # Filter out any None results due to errors
    results = [res for res in results if res is not None]

    return results


# results = main(
#     user_directory_file_path = '/Users/rahulduggal/Desktop/test_directory_two'
# )
# print(results)