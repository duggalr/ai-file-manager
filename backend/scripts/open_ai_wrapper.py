import os
from dotenv import load_dotenv, find_dotenv
ENV_FILE = find_dotenv()
load_dotenv(ENV_FILE)

from openai import OpenAI


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
