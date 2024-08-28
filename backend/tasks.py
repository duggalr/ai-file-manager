from celery import shared_task
from backend.models import UserProfile
# from .scripts.file_process import mp_main_two
from .scripts_two.file_process import mp_main_two


@shared_task()
def process_user_directory(user_directory_path, user_profile_object_id):
    print('Processing user directory:', user_directory_path, user_profile_object_id)
    
    user_profile_object = UserProfile.objects.get(id=user_profile_object_id)
    user_profile_object.files_under_process = True
    user_profile_object.save()

    mp_main_two.main(
        user_directory_file_path = user_directory_path,
        user_profile_object = user_profile_object
    )