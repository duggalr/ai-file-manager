from dotenv import load_dotenv, find_dotenv
ENV_FILE = find_dotenv()
load_dotenv(ENV_FILE)

from pathlib import Path
import os
import sys
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
parent_path = os.path.join(BASE_DIR, 'ai_file_manager')
sys.path.append(parent_path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ai_file_manager.settings")

import django
django.setup()

from backend.models import *

import base64
import json
import concurrent.futures
import datetime
import platform
from functools import partial
from pdf2image import convert_from_path
from enum import Enum
from openai import OpenAI


class Prompts(Enum):
    """
    """
    CATEGORIZATION_PROMPT_V1 = """You are an AI that categorizes files based on their content. I have provided a screenshot of a file to you. Based on the screenshot, your task is to categorize the file into an entity type, the primary category and a few relevant sub-categories. Also, generate a semantically appropriate, human-readble name for the file, based on the screenshot. The name you generate is meant to be shown on the website, for the user to easily identify the file. Your response should be in JSON format.

Please categorize the file as follows:
- **File Name:**: The semantic name of the file based on the screenshot.
- **Entity Type:**: The type of the file (ie. Book, Paper, Image, Invoice, CSV, etc.)
- **Primary Category:** The main category that best describes the file.
- **Sub-categories/Tags:** Additional categories or tags that further describe the file's content.

Return your response in the following JSON format:

{
    "generated_file_name": "...",
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

    # def _generate_openai_api_response(self, category_prompt, image_file_path, return_json=False):
    #     response = self.client.chat.completions.create(
    #         model="gpt-4o-mini",
    #         messages=[
    #             {
    #                 "role": "user",
    #                 "content": [
    #                     {
    #                         "type": "text",
    #                         "text": f"{category_prompt}"
    #                     },
    #                     {
    #                     "type": "image_url",
    #                     "image_url": {
    #                         "url": f"{image_file_path}",
    #                     },
    #                     },
    #                 ],
    #             }
    #         ],
    #         # max_tokens=300,
    #         response_format = { "type": "json_object" } if return_json else None,
    #     )
    #     msg_content = response.choices[0].message.content
    #     return msg_content

    # def generate_file_category_json(self, image_file_path, prompt):
    #     return self._generate_openai_api_response(
    #         category_prompt = prompt,
    #         image_file_path = image_file_path,
    #         return_json = True
    #     )

    def generate_file_category_json(self, image_data, prompt):
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
             messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"{prompt}"
                        },
                        {
                        "type": "image_url",
                        "image_url": {
                            "url": f"{image_data}",
                        },
                        },
                    ],
                }
            ],
            response_format= { "type": "json_object" },
        )
        return response.choices[0].message.content


def encode_image(image: Image.Image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return buffered.getvalue()



def _is_image_file(file_path):
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except (IOError, UnidentifiedImageError):
        return False


def _main_file_to_image(input_file_path):
    file_extension = input_file_path.split('.')[-1]
    if _is_image_file(input_file_path):
        return Image.open(input_file_path)
    elif file_extension == 'pdf':
        return convert_from_path(input_file_path, first_page=1, last_page=1)[0]
    else:
        with open(input_file_path, 'r') as file:
            text = file.read()
        return text_to_image(text)


def text_to_image(text):
    width, height = 800, 600
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("arial.ttf", size=20)
    except OSError:
        font = ImageFont.load_default()

    margin, offset = 10, 10
    for line in text.splitlines():
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        draw.text((margin, offset), line, font=font, fill="black")
        offset += text_height + 5
        if offset > height - margin:
            break

    # image.save(output_file_path, format='PNG')
    # return output_file_path
    return image

    # margin, offset = 10, 10
    # for line in text.splitlines():
    #     draw.text((margin, offset), line, font=font, fill="black")
    #     offset += draw.textsize(line, font=font)[1] + 5
    #     if offset > height - margin:
    #         break

    # return image

    # # font = ImageFont.truetype('arial.ttf', 40)
    # # # text = "Hello, World!"
    # # text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:4]
    # # position = ((image.width - text_width) // 2, (image.height - text_height) // 2)
    # # draw.text(position, text, fill='black', font=font)


def process_single_file(file_path, category_prompt, op_wrapper):
    # try:
    image = _main_file_to_image(file_path)
    image_data = encode_image(image)
    response = op_wrapper.generate_file_category_json(
        image_data=f"data:image/png;base64,{base64.b64encode(image_data).decode()}",
        prompt=category_prompt
    )
    json_response_data = json.loads(response)
    file_size = os.path.getsize(file_path)
    last_access_time = datetime.datetime.fromtimestamp(os.path.getatime(file_path))
    last_modified_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
    creation_time = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
    current_image_file_name = os.path.basename(file_path)
    json_response_data.update({
        'file_path': file_path,
        'file_name': current_image_file_name,
        'file_size_in_bytes': file_size,
        'file_last_access_time': last_access_time,
        'file_created_at_date_time': creation_time,
        'file_modified_at_date_time': last_modified_time,
        'screenshot_image': ContentFile(image_data, name=f"{uuid.uuid4()}.png")
    })
    return json_response_data
    # except Exception as e:
    #     print(f"Error processing file {file_path}: {e}")
    #     return None


import process_directory_main

# def main(user_directory_file_path, dobject):
def main(user_directory_file_path):

    dobject = Directory.objects.create(
        user_directory_name = os.path.basename(user_directory_file_path),
        user_directory_path = user_directory_file_path
    )
    dobject.save()
    
    could_not_process_file_list = []
    processed_files = set()
    invalid_directories = []
    valid_file_paths = []
    invalid_file_paths = []
    process_directory_main.process_directory(
        user_directory_file_path,
        invalid_directories,
        valid_file_paths,
        invalid_file_paths
    )

    print(f"Number of Valid File Paths: {len(valid_file_paths)}")
    print(f"Number of Invalid Directories: {len(invalid_directories)}")
    print(f"Number of Invalid File Paths: {len(invalid_file_paths)}")
    # print('-------------------------------------------------------------------')
    # print(f"Valid File Paths: {valid_file_paths}")
    # print(f"Invalid Directories: {invalid_directories}")
    # print(f"Invalid File Paths: {invalid_file_paths}")

    category_prompt = Prompts.CATEGORIZATION_PROMPT_V1.value
    op_wrapper = OpenAIWrapper()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        process_worker = partial(process_single_file, category_prompt=category_prompt, op_wrapper=op_wrapper)
        results = list(executor.map(process_worker, valid_file_paths))

    for result in results:
        if result:
            file_path = result['file_path']
            print(f"FIlE PATH: {file_path} | SET: {processed_files}")
            if file_path not in processed_files:  # Avoid duplicates
                processed_files.add(file_path)
                file = File(
                    file_path=file_path,
                    file_name=result['file_name'],
                    
                    generated_file_name=result['generated_file_name'],

                    entity_type=result['entity_type'],
                    primary_category=result['primary_category'],
                    sub_categories=result['sub_categories'],
                    file_size_in_bytes=result['file_size_in_bytes'],
                    file_last_access_time=result['file_last_access_time'],
                    file_created_at_date_time=result['file_created_at_date_time'],
                    file_modified_at_date_time=result['file_modified_at_date_time'],
                    screenshot_image=result['screenshot_image'],  # Save the image directly
                    processed=True,
                    directory_object=dobject
                )
                file.save()

    for file_path in could_not_process_file_list:
        if file_path not in processed_files:  # Avoid duplicates
            processed_files.add(file_path)
            file = File(
                file_path=file_path,
                file_name=os.path.basename(file_path),
                processed=False,
                directory_object=dobject
            )
            file.save()

    return results


# if __name__ == '__main__':
#     directory_list = [
#         # '/Users/rahulduggal/Desktop/test_directory_one',
#         # '/Users/rahulduggal/Desktop/test_directory_two',
#         # '/Users/rahulduggal/Desktop/test_directory_three',
#         '/Users/rahulduggal/Desktop/test_directory_four',
#     ]

#     directory_fp = directory_list[0]
#     d_object = Directory.objects.create(
#         user_directory_name = os.path.basename(directory_fp),
#         user_directory_path = directory_fp
#     )
#     d_object.save()

#     main(
#         user_directory_file_path = directory_fp,
#         dobject = d_object
#     )