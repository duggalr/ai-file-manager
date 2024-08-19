import os
import sys
import base64
import json
import uuid
import datetime
from io import BytesIO
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from dotenv import load_dotenv, find_dotenv
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError
from pdf2image import convert_from_path
from django.core.files.base import ContentFile
import django
from enum import Enum
from openai import OpenAI

# Load environment variables
ENV_FILE = find_dotenv()
load_dotenv(ENV_FILE)

# Set up Django environment
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
parent_path = os.path.join(BASE_DIR, 'ai_file_manager')
sys.path.append(parent_path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ai_file_manager.settings")
django.setup()

# Import Django models
from backend.models import Directory, File


class Prompts(Enum):
    """
    """
    CATEGORIZATION_PROMPT_V1 = """You task is to specialize in file categorization. I have provided you with a screenshot of a file. Your task is to analyze the content and context within the screenshot and categorize the file into an appropriate entity type, a primary category, and relevant sub-categories. Your categorization should be comprehensive and accurate, capturing the essence of the file's content. Also, generate a semantically appropriate, human-readble name for the file, based on the screenshot. The name you generate is meant to be shown on the website, for the user to easily identify the file.

Please structure your response in the following JSON format:

{
    "generated_file_name": "...",
    "entity_type": "Specify the type of the file (e.g., Book, Paper, Image, Invoice, Spreadsheet, etc.)",
    "primary_category": "Name of the main category that best describes the file",
    "sub_categories": [
        "Relevant sub-category 1",
        "Relevant sub-category 2",
        ...
    ]
}

Guidelines:
- **File Name:**: The semantic name of the file based on the screenshot.
- **Entity Type**: Identify the most accurate file type based on the content visible in the screenshot.
- **Primary Category**: Determine the overarching category that encapsulates the file’s primary purpose or theme.
- **Sub-categories/Tags**: List a few additional categories or tags that provide further context or details about the file's content.

Ensure the categorization is logical, and the chosen tags are relevant and specific to the file’s content. 
"""


class OpenAIWrapper:
    def __init__(self):
        self.api_key = os.environ['OPENAI_KEY']
        self.client = OpenAI(api_key=self.api_key)

    def generate_file_category_json(self, image_data, prompt):
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"{prompt}"},
                        {"type": "image_url", "image_url": {"url": f"{image_data}"}}
                    ],
                }
            ],
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content

# Helper functions
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

    return image


def tmp_task_one(file_path, op_wrapper, category_prompt, could_not_process_file_list):
    try:
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
            'screenshot_image': base64.b64encode(image_data).decode(),  # Serialize image data as base64
            # 'screenshot_image': ContentFile(image_data, name=f"{uuid.uuid4()}.png")
        })
        return json_response_data
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        could_not_process_file_list.append(file_path)
        return None


# def process_single_file(file_path, category_prompt, op_wrapper, could_not_process_file_list):
#     try:
#         image = _main_file_to_image(file_path)
#         image_data = encode_image(image)
#         response = op_wrapper.generate_file_category_json(
#             image_data=f"data:image/png;base64,{base64.b64encode(image_data).decode()}",
#             prompt=category_prompt
#         )
#         json_response_data = json.loads(response)
#         file_size = os.path.getsize(file_path)
#         last_access_time = datetime.datetime.fromtimestamp(os.path.getatime(file_path))
#         last_modified_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
#         creation_time = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
#         current_image_file_name = os.path.basename(file_path)
#         json_response_data.update({
#             'file_path': file_path,
#             'file_name': current_image_file_name,
#             'file_size_in_bytes': file_size,
#             'file_last_access_time': last_access_time,
#             'file_created_at_date_time': creation_time,
#             'file_modified_at_date_time': last_modified_time,
#             'screenshot_image': ContentFile(image_data, name=f"{uuid.uuid4()}.png")
#         })
#         return json_response_data
#     except Exception as e:
#         print(f"Error processing file {file_path}: {e}")
#         could_not_process_file_list.append(file_path)
#         return None


# def main(user_file_path, could_not_process_file_list):
#     category_prompt = Prompts.CATEGORIZATION_PROMPT_V1.value
#     op_wrapper = OpenAIWrapper()
#     return process_single_file(
#         user_file_path,
#         category_prompt,
#         op_wrapper,
#         could_not_process_file_list
#     )

    # with ThreadPoolExecutor() as executor:
    #     process_worker = partial(process_single_file, category_prompt=category_prompt, op_wrapper=op_wrapper, could_not_process_file_list=could_not_process_file_list)
    #     results = list(executor.map(process_worker, valid_file_paths))

    # for result in results:
    #     if result:
    #         file_path = result['file_path']
    #         if file_path not in processed_files:
    #             processed_files.add(file_path)
    #             file = File(
    #                 file_path=file_path,
    #                 file_name=result['file_name'],
    #                 generated_file_name=result['generated_file_name'],
    #                 entity_type=result['entity_type'],
    #                 primary_category=result['primary_category'],
    #                 sub_categories=result['sub_categories'],
    #                 file_size_in_bytes=result['file_size_in_bytes'],
    #                 file_last_access_time=result['file_last_access_time'],
    #                 file_created_at_date_time=result['file_created_at_date_time'],
    #                 file_modified_at_date_time=result['file_modified_at_date_time'],
    #                 screenshot_image=result['screenshot_image'],
    #                 processed=True,
    #                 directory_object=dobject
    #             )
    #             file.save()

    # for file_path in could_not_process_file_list:
    #     if file_path not in processed_files:
    #         processed_files.add(file_path)
    #         file = File(
    #             file_path=file_path,
    #             file_name=os.path.basename(file_path),
    #             processed=False,
    #             directory_object=dobject
    #         )
    #         file.save()

    # return results

