import os
import uuid
import base64
from django.core.files.base import ContentFile
from celery import shared_task, group, chord
from backend.models import UserProfile, File, Directory

# from .scripts.file_process import process_single_file_task

from .scripts.file_process.new import process_directory_main_two
from .scripts.file_process import mp_main_three


def _prepare_directory_files(user_directory_file_path, user_profile_object):
    dobject = Directory.objects.create(
        user_directory_name = os.path.basename(user_directory_file_path),
        user_directory_path = user_directory_file_path,
        user_profile_obj = user_profile_object
    )
    dobject.save()

    invalid_directories = []
    valid_file_paths = []
    invalid_file_paths = []
    could_not_process_file_list = []

    process_directory_main_two.process_directory(
        user_directory_file_path,
        invalid_directories,
        valid_file_paths,
        invalid_file_paths
    )

    print(f"Number of Valid File Paths: {len(valid_file_paths)}")
    print(f"Number of Invalid Directories: {len(invalid_directories)}")
    print(f"Number of Invalid File Paths: {len(invalid_file_paths)}")
    print('-------------------------------------------------------------------')

    return dobject, valid_file_paths, could_not_process_file_list


@shared_task()
def handle_processing_results(results, dobject_id, could_not_process_file_list, user_profile_object_id):
    processed_files = set()
    dobject = Directory.objects.get(id=dobject_id)

    for result in results:
        if result and 'error' not in result:
            file_path = result['file_path']
            if file_path not in processed_files:

                screenshot_image = result['screenshot_image']
                image_data = base64.b64decode(screenshot_image)
                content_file = ContentFile(image_data, name=f"{uuid.uuid4()}.png")

                processed_files.add(file_path)
                file = File(
                    file_path=file_path,
                    file_name=result['file_name'],
                    generated_file_name=result['generated_file_name'],
                    entity_type=result['entity_type'],
                    primary_category=result['primary_category'],
                    sub_categories=result['sub_categories'],
                    file_size_in_bytes=result['file_size_in_bytes'],
                    file_last_access_time=result['file_last_access_time'],
                    file_created_at_date_time=result['file_created_at_date_time'],
                    file_modified_at_date_time=result['file_modified_at_date_time'],
                    screenshot_image=content_file,
                    # screenshot_image=result['screenshot_image'],
                    processed=True,
                    directory_object=dobject
                )
                file.save()

    # Handle files that couldn't be processed
    for file_path in could_not_process_file_list:
        if file_path not in processed_files:
            processed_files.add(file_path)
            file = File(
                file_path=file_path,
                file_name=os.path.basename(file_path),
                processed=False,
                directory_object=dobject
            )
            file.save()

    user_profile_object = UserProfile.objects.get(id=user_profile_object_id)
    user_profile_object.files_under_process = False
    user_profile_object.save()



@shared_task()
def process_single_file(file_path, could_not_process_file_list):
    category_prompt = mp_main_three.Prompts.CATEGORIZATION_PROMPT_V1.value
    op_wrapper = mp_main_three.OpenAIWrapper()
    
    return mp_main_three.tmp_task_one(
        file_path = file_path,
        op_wrapper = op_wrapper,
        category_prompt = category_prompt,
        could_not_process_file_list = could_not_process_file_list
    )


def process_directory(user_directory_path, user_profile_object):
    dobject, valid_file_paths, could_not_process_file_list = _prepare_directory_files(user_directory_path, user_profile_object)

    # Create the group of tasks
    tasks = [
        process_single_file.s(file_path, could_not_process_file_list)
        for file_path in valid_file_paths
    ]

    # Create a chord to handle the results once all tasks are complete
    callback = handle_processing_results.s(dobject.id, could_not_process_file_list, user_profile_object.id)
    chord(tasks)(callback)

    # user_profile_object.files_under_process = False
    # user_profile_object.save()


    # # Create a group of tasks to be executed in parallel
    # tasks = group(
    #     process_single_file.s(file_path, could_not_process_file_list)
    #     for file_path in valid_file_paths
    # )
    
    # # # Execute the group of tasks and collect the results
    # # results = tasks.apply_async().get()  # get() waits for all tasks to complete
    # # Never call result.get() within a task!

    # # Handle the processing results
    # handle_processing_results(results, dobject, could_not_process_file_list)


    # jobs = process_single_file.chunks(list_of_millions_of_ids, 30) # break the list into 30 chunks. Experiment with what number works best here.
    # jobs.apply_async()
    
    # chunk_size = 10
    # tasks = group(main(file_path, could_not_process_file_list) for file_path in valid_file_paths)
    # results = tasks.chunks(chunk_size).apply_async().get()

    # mp_main_three.chunks(zip(valid_file_paths, [dobject.id] * len(valid_file_paths)), 30)

    # dobject, valid_file_paths, could_not_process_file_list = prepare_directory_files(user_directory_path, user_profile_object)

    # # Using chunks to process files in parallel
    # task = process_single_file_task.chunks(zip(valid_file_paths, [dobject.id] * len(valid_file_paths)), 30)
    # results = task.apply_async().get()

    # handle_processing_results(results, dobject, could_not_process_file_list)


@shared_task()
def process_user_directory(user_directory_path, user_profile_object_id):
    print('Processing user directory:', user_directory_path, user_profile_object_id)
    
    user_profile_object = UserProfile.objects.get(id=user_profile_object_id)

    # Set the flag to indicate files are being processed
    user_profile_object.files_under_process = True
    user_profile_object.save()

    # Call the refactored main function
    process_directory(user_directory_path, user_profile_object)
    
    # # Reset the flag after processing is complete
    # user_profile_object.files_under_process = False
    # user_profile_object.save()
