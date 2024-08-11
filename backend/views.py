from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
load_dotenv()
import os
from openai import OpenAI


def home(request):
    return render(request, 'home.html')


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


@csrf_exempt
def upload_directory(request):
    if request.method == 'POST':
        uploaded_files = request.FILES.getlist('files[]')

        # Read contents of the files
        file_data = []
        for file in uploaded_files:
            file_content = read_file_content(file)
            file_data.append({
                'name': file.name,
                'type': file.content_type,
                'content': file_content[:2000]  # Limit content to 2000 characters
            })

        # # Gather file information for GPT
        # file_info = [{'name': file.name, 'type': file.content_type} for file in uploaded_files]

        # # Use GPT to categorize files
        # categories = categorize_files_with_gpt(file_info)
        # print(categories)

        # # Print the files and their categories
        # for file, category in zip(uploaded_files, categories):
        #     print(f"File: {file.name}, Category: {category}")

        # Use GPT to categorize files based on content
        categories = categorize_files_with_gpt(file_data)
        print(categories)

        # # Print the files and their categories
        # for file, category in zip(uploaded_files, categories):
        #     print(f"File: {file.name}, Category: {category}")

        return JsonResponse({'status': 'success', 'categories': categories})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


def categorize_files_with_gpt(file_info):
    # Prepare the prompt for GPT
    prompt = "You are an AI that organizes files semantically. Here is a list of files with their names and types:\n\n"
    
    for file in file_info:
        prompt += f"- File Name: {file['name']}, File Type: {file['type']}\n"
    
    prompt += "\nPlease categorize these files into meaningful groups (e.g., Documents, Images, Books, etc.). Provide a list of categories corresponding to each file. Please return your response in JSON format."

    client = OpenAI(
        # This is the default and can be omitted
        api_key = os.environ.get("OPENAI_API_KEY"),
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model = "gpt-4o-2024-05-13",
    )

    model_output = chat_completion.choices[0].message.content
    return model_output

