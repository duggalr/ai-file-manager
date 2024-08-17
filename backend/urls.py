from django.urls import path
from . import views


urlpatterns = [
    # Auth0
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("callback", views.callback, name="callback"),

    # Application
    path('', views.landing, name='landing'),
    path('manage-file-path', views.manage_file_path, name='manage_file_path'),
    path('file-view', views.file_view, name='file_view'),
    path('files/unprocessed', views.unprocessed_file_view, name='unprocessed_file_view'),
    path('delete-user-file-path/<uuid:uuid>/', views.delete_user_file_path, name='delete_user_file_path'),

    # Ajax
    path('handle-user-file-path-submit', views.handle_user_file_path_submit, name='handle_user_file_path_submit'),
    path('handle_filtering_file_data', views.handle_filtering_file_data, name='handle_filtering_file_data'),
    path('switch_filtered_file_data', views.switch_filtered_file_data, name='switch_filtered_file_data'),
    path('open_user_file', views.open_user_file, name='open_user_file'),
    path('update-preference/', views.update_view_preference, name='update_view_preference'),
]