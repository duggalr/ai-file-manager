from django.urls import path
from . import views


urlpatterns = [
    # Application
    path('', views.home, name='home'),
    path('file-view', views.file_view, name='file_view'),

    # Ajax
    path('handle-user-file-path-submit', views.handle_user_file_path_submit, name='handle_user_file_path_submit')
]