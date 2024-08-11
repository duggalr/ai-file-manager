from enum import Enum


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
    "primary_category": "Primary Category Name",
    "sub_categories": [
        "Sub-category 1",
        "Sub-category 2",
        ...
    ]
}
"""
