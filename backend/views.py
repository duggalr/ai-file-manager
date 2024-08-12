from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
load_dotenv()

from .models import File
# from .scripts import user_file_path_utils


# AJAX
def handle_user_file_path_submit(request):
    if request.method == 'POST':
        user_file_path = request.POST['user_file_path']
        print('user-fp:', user_file_path)

        rv_list = user_file_path_utils.main(
            user_file_path = user_file_path
        )

        for di in rv_list:
            fobj = File.objects.create(
                user_directory_file_path = user_file_path,
                current_file_path = di['current_image_file_path'],
                entity_type = di['entity_type'],
                primary_category = di['primary_category'],
                sub_categories = di['sub_categories']
            )
            fobj.save()

        return JsonResponse({
            'success': True
        })


def home(request):
    return render(request, 'home.html')


def file_view(request):
    file_objects = File.objects.all()

    category_dict = {}
    for fn_obj in file_objects:
        ctg = fn_obj.primary_category
        if ctg in category_dict:
            l = category_dict[ctg]
            l.append(fn_obj)
            category_dict[ctg] = l
        else:
            category_dict[ctg] = [fn_obj]

    rv = []
    for ctg in category_dict:
        rv.append([ctg, category_dict[ctg]])

    return render(request, 'file_view.html', {
        # 'file_objects': file_objects
        'categorized_files': rv
    })



# def read_file_content(file):
#     try:
#         if file.content_type.startswith('text'):
#             return file.read().decode('utf-8')
#         elif file.content_type == 'application/pdf':
#             return extract_pdf_text(file)
#         else:
#             return "File type not supported for content extraction."
#     except Exception as e:
#         return str(e)

# def extract_pdf_text(file):
#     try:
#         import PyPDF2
#         reader = PyPDF2.PdfFileReader(file)
#         text = ""
#         for page_num in range(reader.getNumPages()):
#             text += reader.getPage(page_num).extract_text()
#         return text
#     except Exception as e:
#         return str(e)


# @csrf_exempt
# def upload_directory(request):
#     if request.method == 'POST':
#         uploaded_files = request.FILES.getlist('files[]')

#         # Read contents of the files
#         file_data = []
#         for file in uploaded_files:
#             file_content = read_file_content(file)
#             file_data.append({
#                 'name': file.name,
#                 'type': file.content_type,
#                 'content': file_content[:2000]  # Limit content to 2000 characters
#             })

#         # # Gather file information for GPT
#         # file_info = [{'name': file.name, 'type': file.content_type} for file in uploaded_files]

#         # # Use GPT to categorize files
#         # categories = categorize_files_with_gpt(file_info)
#         # print(categories)

#         # # Print the files and their categories
#         # for file, category in zip(uploaded_files, categories):
#         #     print(f"File: {file.name}, Category: {category}")

#         # Use GPT to categorize files based on content
#         categories = categorize_files_with_gpt(file_data)
#         print(categories)

#         # # Print the files and their categories
#         # for file, category in zip(uploaded_files, categories):
#         #     print(f"File: {file.name}, Category: {category}")

#         return JsonResponse({'status': 'success', 'categories': categories})

#     return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


# def categorize_files_with_gpt(file_info):
#     # Prepare the prompt for GPT
#     prompt = "You are an AI that organizes files semantically. Here is a list of files with their names and types:\n\n"
    
#     for file in file_info:
#         prompt += f"- File Name: {file['name']}, File Type: {file['type']}\n"
    
#     prompt += "\nPlease categorize these files into meaningful groups (e.g., Documents, Images, Books, etc.). Provide a list of categories corresponding to each file. Please return your response in JSON format."

#     client = OpenAI(
#         # This is the default and can be omitted
#         api_key = os.environ.get("OPENAI_API_KEY"),
#     )

#     chat_completion = client.chat.completions.create(
#         messages=[
#             {
#                 "role": "user",
#                 "content": prompt,
#             }
#         ],
#         model = "gpt-4o-2024-05-13",
#     )

#     model_output = chat_completion.choices[0].message.content
#     return model_output

