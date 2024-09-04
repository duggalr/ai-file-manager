from django.urls import path
from . import views


urlpatterns = [
    # path('', views.landing, name='landing'),
    # path('blog/welcome', views.blog_post_one, name='blog_post_one'),

    # AJAX
    path('api/handle_email_submission', views.handle_email_submission, name='handle_email_submission'),
    path('api/get_email_subscriber_count', views.get_email_subscriber_count, name='get_email_subscriber_count'),
    path('api/save_user_profile', views.save_user_profile, name='save_user_profile'),
    path('api/get_user_filepaths', views.get_user_filepaths, name='get_user_filepaths'),

    path('api/check_processing_status', views.check_processing_status, name='check_processing_status'),
    path('api/handle_user_directory_filepath_submission', views.handle_user_directory_filepath_submission, name='handle_user_directory_filepath_submission'),


    path('api/get_user_profile_information', views.get_user_profile_information, name='get_user_profile_information'),

    path('api/view_directory_files', views.view_directory_files, name='view_directory_files'),

    path('api/update_view_preference', views.update_view_preference, name='update_view_preference'),
    path('api/switch_filtered_file_data', views.switch_filtered_file_data, name='switch_filtered_file_data'),

    path('api/handle_filtering_file_data', views.handle_filtering_file_data, name='handle_filtering_file_data'),
    path('api/open_user_file', views.open_user_file, name='open_user_file'),

    path('api/delete_user_file_path', views.delete_user_file_path, name='delete_user_file_path'),

]