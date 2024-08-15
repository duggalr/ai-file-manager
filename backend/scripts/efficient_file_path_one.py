import os
import json
import base64
import concurrent.futures
import datetime
from functools import partial
from . import data_utils, open_ai_wrapper, prompts_wrapper



def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

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


# TODO:
    # test and finalize this script
        # integrate in web app with Celery task scheduler
            # implement all functionaltiy on the frontend
            # proceed from there to determine what is left before internal release
                # embeddings for search
                # auth0 integration and refactor models to include user object
                # testing and finalization of backend + ui
                # simple refresh on directory rather than chrome extension for V1
                # simple landing page and deployment on aws with custom domain
                    # i use myself (test out, etc.)
                    # release to chuan/ml-team <-- Tuesday of next week