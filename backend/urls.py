from django.urls import path
from . import views


urlpatterns = [
    # Application
    path('', views.home, name='home'),
    path('file-view', views.file_view, name='file_view'),
    path('handle_filtering_file_data', views.handle_filtering_file_data, name='handle_filtering_file_data'),
    path('switch_filtered_file_data', views.switch_filtered_file_data, name='switch_filtered_file_data'),

    # Ajax
    path('handle-user-file-path-submit', views.handle_user_file_path_submit, name='handle_user_file_path_submit')
]