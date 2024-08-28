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
]