

def main(user_directory_file_path, user_profile_object):
    dobject = Directory.objects.create(
        user_directory_name = os.path.basename(user_directory_file_path),
        user_directory_path = user_directory_file_path,
        user_profile_obj = user_profile_object
    )
    dobject.save()

    could_not_process_file_list = []
    processed_files = set()
    invalid_directories = []
    valid_file_paths = []
    invalid_file_paths = []

    # Assuming process_directory_main.process_directory is a custom function
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
    # print(f"Valid File Paths: {valid_file_paths}")
    # print(f"Invalid Directories: {invalid_directories}")
    # print(f"Invalid File Paths: {invalid_file_paths}")

    category_prompt = Prompts.CATEGORIZATION_PROMPT_V1.value
    op_wrapper = OpenAIWrapper()

    with ThreadPoolExecutor() as executor:
        process_worker = partial(process_single_file, category_prompt=category_prompt, op_wrapper=op_wrapper, could_not_process_file_list=could_not_process_file_list)
        results = list(executor.map(process_worker, valid_file_paths))

    for result in results:
        if result:
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

    return results

