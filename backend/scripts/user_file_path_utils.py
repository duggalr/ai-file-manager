import base64
import json
import data_utils
import open_ai_wrapper
import prompts_wrapper


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

        response = op_wrapper.generate_file_category_json(
            image_file_path = image_open_ai_file_path,
            prompt = category_prompt,
        )
        json_response_data = json.loads(response)
        json_response_data['current_image_file_path'] = img_fp
        rv.append(json_response_data)

    return rv

## TODO: delete testing code below
# directory_file_path = '/Users/rahulduggal/Desktop/search_fund_material'
# main(
#     user_file_path = directory_file_path
# )