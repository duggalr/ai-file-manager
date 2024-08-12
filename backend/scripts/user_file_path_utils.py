import os
import time
import base64
import json
import datetime
from . import data_utils, open_ai_wrapper, prompts_wrapper


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def main(user_file_path):
    file_path_output_dict = data_utils.main(
        directory_fp = user_file_path
    )
    output_file_path_list = file_path_output_dict['output_file_path_list']
    could_not_process_file_list = file_path_output_dict['could_not_process_file_list']
    print(f"Could not process file paths: {could_not_process_file_list}")

    category_prompt = prompts_wrapper.Prompts.CATEGORIZATION_PROMPT_V1.value
    op_wrapper = open_ai_wrapper.OpenAIWrapper()

    rv = []
    for img_fp in output_file_path_list:
        base64_image = encode_image(img_fp)
        image_open_ai_file_path = f"data:image/jpeg;base64,{base64_image}"

        print(f"Process Image Filepath with Openai: {img_fp}")

        response = op_wrapper.generate_file_category_json(
            image_file_path = image_open_ai_file_path,
            prompt = category_prompt,
        )
        json_response_data = json.loads(response)

        file_size = os.path.getsize(img_fp)

        last_access_time = os.path.getatime(img_fp)
        last_modified_time = os.path.getmtime(img_fp)
        creation_time = os.path.getctime(img_fp)
        last_access_time = datetime.datetime.fromtimestamp(last_access_time).strftime('%Y-%m-%d %H:%M:%S')
        last_modified_time = datetime.datetime.fromtimestamp(last_modified_time).strftime('%Y-%m-%d %H:%M:%S')
        creation_time = datetime.datetime.fromtimestamp(creation_time).strftime('%Y-%m-%d %H:%M:%S')

        json_response_data['current_image_file_path'] = img_fp
        json_response_data['file_size'] = file_size
        json_response_data['last_access_time'] = last_access_time
        json_response_data['last_modified_time'] = last_modified_time
        json_response_data['creation_time'] = creation_time

        rv.append(json_response_data)

    return rv

## TODO: delete testing code below
# directory_file_path = '/Users/rahulduggal/Desktop/search_fund_material'
# main(
#     user_file_path = directory_file_path
# )

# file_path = '/Users/rahulduggal/Downloads/beater_top_two.jpg'
# file_size = os.path.getsize(file_path)

# last_access_time = os.path.getatime(file_path)
# last_modified_time = os.path.getmtime(file_path)
# creation_time = os.path.getctime(file_path)
# last_access_time = datetime.datetime.fromtimestamp(last_access_time).strftime('%Y-%m-%d %H:%M:%S')
# last_modified_time = datetime.datetime.fromtimestamp(last_modified_time).strftime('%Y-%m-%d %H:%M:%S')
# creation_time = datetime.datetime.fromtimestamp(creation_time).strftime('%Y-%m-%d %H:%M:%S')

# # Output the metadata information
# print(f"File Size: {file_size} bytes")
# print(f"Last Accessed: {last_access_time}")
# print(f"Last Modified: {last_modified_time}")
# print(f"Creation Time: {creation_time}")