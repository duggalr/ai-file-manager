from dotenv import load_dotenv
load_dotenv()
from django.shortcuts import render, get_object_or_404, redirect


def landing(request):
    return render(request, 'validation/landing.html')
