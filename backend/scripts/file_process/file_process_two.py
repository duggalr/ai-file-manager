from dotenv import load_dotenv, find_dotenv
ENV_FILE = find_dotenv()
load_dotenv(ENV_FILE)

from pathlib import Path
import os
import sys
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
parent_path = os.path.join(BASE_DIR, 'ai_file_manager')
# /Users/rahulduggal/Documents/new_projects/ai_file_manager/ai_file_manager
print('PARENT:', parent_path)
sys.path.append(parent_path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ai_file_manager.settings")

import django
django.setup()

from backend.models import *

import json
import base64
import concurrent.futures
import datetime
import platform
import uuid
from functools import partial
from django.db import models
from pdf2image import convert_from_path
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError
# from . import data_utils, open_ai_wrapper, prompts_wrapper

from enum import Enum
from openai import OpenAI



class Prompts(Enum):
    """
    """
    CATEGORIZATION_PROMPT_V1 = """You are an AI that categorizes files based on their content. I have provided a screenshot of a file to you. Based on the screenshot, your task is to categorize the file into an entity type, the primary category and a few relevant sub-categories. Your response should be in JSON format.

Please categorize the file as follows:
- **Entity Type:**: The type of the file (ie. Book, Paper, Image, Invoice, CSV, etc.)
- **Primary Category:** The main category that best describes the file.
- **Sub-categories/Tags:** Additional categories or tags that further describe the file's content.

Return your response in the following JSON format:

{
    "entity_type": "...",
    "primary_category": "Primary Category Name",
    "sub_categories": [
        "Sub-category 1",
        "Sub-category 2",
        ...
    ]
}
"""

class OpenAIWrapper(object):
    """
    """
    def __init__(self):
        self.api_key = os.environ['OPENAI_KEY']
        self.client = OpenAI(
            api_key = self.api_key
        )

    def _generate_openai_api_response(self, category_prompt, image_file_path, return_json=False):
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"{category_prompt}"
                        },
                        {
                        "type": "image_url",
                        "image_url": {
                            "url": f"{image_file_path}",
                        },
                        },
                    ],
                }
            ],
            # max_tokens=300,
            response_format = { "type": "json_object" } if return_json else None,
        )
        msg_content = response.choices[0].message.content
        return msg_content

    def generate_file_category_json(self, image_file_path, prompt):
        return self._generate_openai_api_response(
            category_prompt = prompt,
            image_file_path = image_file_path,
            return_json = True
        )


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def is_hidden(filepath):
    if platform.system() != 'Windows':
        return os.path.basename(filepath).startswith('.')
    else:
        try:
            import ctypes
            attrs = ctypes.windll.kernel32.GetFileAttributesW(str(filepath))
            return attrs != -1 and (attrs & 2)
        except Exception:
            return False

def _is_valid_file(filepath):
    if is_hidden(filepath):
        return False
    file_extension = filepath.split('.')[-1]
    file_size_in_bytes = os.path.getsize(filepath)
    valid_file_size_bytes = 50000000 if file_extension == 'pdf' else 10000000
    return file_size_in_bytes <= valid_file_size_bytes

def _is_image_file(file_path):
    try:
        with Image.open(file_path) as img:
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
    first_page_image.save(output_fp)
    return output_fp

def _text_to_image(input_file_path, output_file_path):
    with open(input_file_path, 'r') as file:
        text = file.read()
    width, height = 800, 600
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("arial.ttf", size=20)
    except OSError:
        font = ImageFont.load_default()
    margin, offset = 10, 10
    for line in text.splitlines():
        draw.text((margin, offset), line, font=font, fill="black")
        offset += draw.textsize(line, font=font)[1] + 5
        if offset > height - margin:
            break
    image.save(output_file_path, format='PNG')
    return output_file_path

def _main_file_to_image(input_file_path, output_file_path):
    file_extension = input_file_path.split('.')[-1]
    if _is_image_file(input_file_path):
        return _image_to_image(input_file_path, output_file_path)
    elif file_extension == 'pdf':
        return _pdf_to_image(input_file_path, output_file_path)
    else:
        return _text_to_image(input_file_path, output_file_path)

def get_screenshots(directory_fp):
    could_not_process_file_list = []
    output_file_path_list = []
    for root, _, files in os.walk(directory_fp):
        for file in files:
            file_path = os.path.join(root, file)
            if _is_valid_file(file_path):
                output_file_path = os.path.splitext(file_path)[0] + ".png"
                output_file_path = _main_file_to_image(file_path, output_file_path)
                output_file_path_list.append(output_file_path)
            else:
                could_not_process_file_list.append(file_path)
    return output_file_path_list, could_not_process_file_list

def process_single_file(img_fp, category_prompt, op_wrapper):
    try:
        base64_image = encode_image(img_fp)
        image_open_ai_file_path = f"data:image/jpeg;base64,{base64_image}"
        response = op_wrapper.generate_file_category_json(
            image_file_path=image_open_ai_file_path,
            prompt=category_prompt,
        )
        json_response_data = json.loads(response)
        file_size = os.path.getsize(img_fp)
        last_access_time = datetime.datetime.fromtimestamp(os.path.getatime(img_fp))
        last_modified_time = datetime.datetime.fromtimestamp(os.path.getmtime(img_fp))
        creation_time = datetime.datetime.fromtimestamp(os.path.getctime(img_fp))
        current_image_file_name = os.path.basename(img_fp)
        json_response_data.update({
            'file_path': img_fp,
            'file_name': current_image_file_name,
            'file_size_in_bytes': file_size,
            'file_last_access_time': last_access_time,
            'file_created_at_date_time': creation_time,
            'file_modified_at_date_time': last_modified_time
        })
        return json_response_data
    except Exception:
        return None


def main(user_directory_file_path):
    output_file_path_list, could_not_process_file_list = get_screenshots(user_directory_file_path)
    category_prompt = Prompts.CATEGORIZATION_PROMPT_V1.value
    op_wrapper = OpenAIWrapper()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        process_worker = partial(process_single_file, category_prompt=category_prompt, op_wrapper=op_wrapper)
        results = list(executor.map(process_worker, output_file_path_list))

    for result in results:
        if result:
            print('result:', result)
            file = File(
                file_path=result['file_path'],
                file_name=result['file_name'],
                entity_type=result['entity_type'],
                primary_category=result['primary_category'],
                sub_categories=result['sub_categories'],
                file_size_in_bytes=result['file_size_in_bytes'],
                file_last_access_time=result['file_last_access_time'],
                file_created_at_date_time=result['file_created_at_date_time'],
                file_modified_at_date_time=result['file_modified_at_date_time'],
                screenshot_image=result['file_path'],
                processed=True
            )
            file.save()

    for file_path in could_not_process_file_list:
        file = File(
            file_path=file_path,
            file_name=os.path.basename(file_path),
            processed=False
        )
        file.save()

    return results


if __name__ == '__main__':
    # main('/Users/username/Desktop/test_folder')
    
    directory_list = [
        '/Users/rahulduggal/Desktop/test_directory_one'
    ]
    for directory in directory_list:
        main(directory)

# TODO:
    # test functionality and ensure solid (connect and test in django as well)
    # benchmark and optimize


# {'entity_type': 'Paper', 'primary_category': 'Research', 'sub_categories': ['Medical Imaging', 'Deep Learning', 'Transfer Learning', '3D Imaging'], 'file_path': '/Users/rahulduggal/Desktop/test_
# directory_one/MED3D- TRANSFER LEARNING FOR 3D MEDICAL IMAGE ANALYSIS.png', 'file_name': 'MED3D- TRANSFER LEARNING FOR 3D MEDICAL IMAGE ANALYSIS.png', 'file_size_in_bytes': 589571, 'file_last_access_time
# ': datetime.datetime(2024, 8, 15, 14, 20, 20, 369235), 'file_created_at_date_time': datetime.datetime(2024, 8, 15, 14, 20, 18, 304250), 'file_modified_at_date_time': datetime.datetime(2024, 8, 15, 14, 2
# 0, 18, 304250)}
