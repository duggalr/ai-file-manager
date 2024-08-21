from dotenv import load_dotenv
load_dotenv()
from django.shortcuts import render, get_object_or_404, redirect


def landing(request):
    return render(request, 'validation/landing.html')


def blog_post_one(request):
    # TODO: after blog post is created, register the url based on the blog content and proceed from there
    return render(request, 'validation/blog_post_one.html')
