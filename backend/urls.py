from django.urls import path
from . import views


urlpatterns = [
    path('', views.landing, name='landing'),
    path('blog/welcome', views.blog_post_one, name='blog_post_one'),

    # AJAX
    path('handle_email_submission', views.handle_email_submission, name='handle_email_submission'),
]