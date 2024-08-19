import os
from celery import shared_task, group
from backend.models import UserProfile, File, Directory

# from .scripts.file_process import process_single_file_task

from .scripts.file_process.new import process_directory_main_two
from .scripts.file_process.mp_main_three import main


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


def handle_processing_results(results, dobject, could_not_process_file_list):
    processed_files = set()

    for result in results:
        if result and 'error' not in result:
            file_path = result['file_path']
            if file_path not in processed_files:
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
                    screenshot_image=result['screenshot_image'],
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


def process_directory(user_directory_path, user_profile_object):
    dobject, valid_file_paths, could_not_process_file_list = _prepare_directory_files(user_directory_path, user_profile_object)
    chunk_size = 10
    tasks = group(main(file_path, could_not_process_file_list) for file_path in valid_file_paths)
    results = tasks.chunks(chunk_size).apply_async().get()
    handle_processing_results(results, dobject, could_not_process_file_list)


@shared_task()
def process_user_directory(user_directory_path, user_profile_object_id):
    print('Processing user directory:', user_directory_path, user_profile_object_id)
    
    user_profile_object = UserProfile.objects.get(id=user_profile_object_id)

    # Set the flag to indicate files are being processed
    user_profile_object.files_under_process = True
    user_profile_object.save()

    # Call the refactored main function
    process_directory(user_directory_path, user_profile_object)
    
    # Reset the flag after processing is complete
    user_profile_object.files_under_process = False
    user_profile_object.save()
