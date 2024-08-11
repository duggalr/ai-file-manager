import pymupdf

def read_file_content(file):
    try:
        if file.content_type.startswith('text'):
            return file.read().decode('utf-8')
        elif file.content_type == 'application/pdf':
            return extract_pdf_text(file)
        else:
            return "File type not supported for content extraction."
    except Exception as e:
        return str(e)

def extract_pdf_text(file):
    try:
        import PyPDF2
        reader = PyPDF2.PdfFileReader(file)
        text = ""
        for page_num in range(reader.getNumPages()):
            text += reader.getPage(page_num).extract_text()
        return text
    except Exception as e:
        return str(e)


# fp = '/Users/rahulduggal/Desktop/deep learning and healthcare/978-981-99-9029-0.pdf'
# doc = pymupdf.open(fp)
# print(doc)

import docx2pdf
from pdf2image import convert_from_path
from PIL import Image

def word_first_page_screenshot(pdf_path, output_image_path):
    # # Convert DOCX to PDF
    # pdf_path = docx_path.replace('.docx', '.pdf')
    # docx2pdf.convert(docx_path, pdf_path)

    # Convert the first page of the PDF to an image
    pages = convert_from_path(pdf_path, first_page=1, last_page=1)
    first_page_image = pages[0]
    # Save the first page as an image
    first_page_image.save(output_image_path, 'PNG')

    return output_image_path


# docx_path = '/Users/rahulduggal/Documents/personal_work_documents/GLM-130B- An Open Bilingual Pre-trained Model.pdf'
# # /Users/rahulduggal/Desktop/deep learning and healthcare/978-981-99-9029-0.pdf
# output_image_path = 'second_page_screenshot.png'
# screenshot_path = word_first_page_screenshot(docx_path, output_image_path)
# print(f"Screenshot saved at: {screenshot_path}")


import pandas as pd
from PIL import Image, ImageDraw, ImageFont

def csv_to_image(csv_path, output_image_path):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_path)

    # Convert the DataFrame to a string format
    data_string = df.to_string()

    # Create a blank image with white background
    image = Image.new('RGB', (1000, 1000), 'white')
    draw = ImageDraw.Draw(image)

    # Load a font
    font = ImageFont.load_default()

    # Draw the text onto the image
    draw.text((10, 10), data_string, font=font, fill='black')

    # Crop the image to remove excess white space
    image = image.crop(image.getbbox())

    # Save the image
    image.save(output_image_path)

    return output_image_path


# # Example usage:
# csv_path = '/Users/rahulduggal/Documents/notebooks/mrp_2023-05-01.csv'
# output_image_path = 'csv_screenshot_two.png'
# screenshot_path = csv_to_image(csv_path, output_image_path)
# print(f"Screenshot saved at: {screenshot_path}")



from dotenv import load_dotenv
load_dotenv()
import os
import base64
import requests


# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


image_path = "/Users/rahulduggal/Desktop/Screenshot 2024-08-08 at 3.27.23 PM.png"
base64_image = encode_image(image_path)

prompt = """You are an AI that categorizes files based on their content. I have provided a screenshot of a file to you. Based on the screenshot, your task is to categorize the file into an entity type, the primary category and a few relevant sub-categories. Your response should be in JSON format.

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

api_key = os.environ['OPENAI_API_KEY']
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

payload = {
    "model": "gpt-4o",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": prompt
          },
          {
            "type": "image_url",
            "image_url": {
              "url": f"data:image/jpeg;base64,{base64_image}"
            }
          }
        ]
      }
    ],
    "max_tokens": 300
}

response = requests.post(
    "https://api.openai.com/v1/chat/completions", 
    headers = headers, 
    json = payload
)

print(response.json())

