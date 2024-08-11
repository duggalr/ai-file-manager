import os
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI
import prompts_wrapper


class OpenAIWrapper(object):
    """
    """

    def __init__(self):
        self.api_key = os.environ['OPENAI_KEY']  # Safer to use getenv
        self.model_name = "gpt-4o-2024-05-13"
        self.client = OpenAI(
            api_key = self.api_key
        )
        # self.prompt = prompts_wrapper.Prompts.CATEGORIZATION_PROMPT_V1.value
    
    def _generate_openai_api_response(self, prompt, return_json=False):
        response = self.client.chat.completions.create(
            model = self.model_name,
            messages=[
                {"role": "user", "content": prompt},
            ],
            response_format = { "type": "json_object" } if return_json else None,
        )

        model_output = response.choices[0].message.content
        return model_output

    def generate_file_category_json(self, prompt):
        return self._generate_openai_api_response(
            prompt = prompt,
            return_json = True
        )

