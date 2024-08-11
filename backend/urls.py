from django.urls import path
from . import views


urlpatterns = [
    # Application
    path('', views.home, name='home'),
    # path('upload-endpoint/', views.upload_directory, name='upload-directory'),
]