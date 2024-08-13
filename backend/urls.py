from django.urls import path
from . import views


urlpatterns = [
    # Application
    path('', views.home, name='home'),
    path('file-view', views.file_view, name='file_view'),
    path('filtered', views.filtered_type_view, name='filtered_type_view'),

    # Ajax
    path('handle-user-file-path-submit', views.handle_user_file_path_submit, name='handle_user_file_path_submit')
]