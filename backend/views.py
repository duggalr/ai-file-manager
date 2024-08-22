from dotenv import load_dotenv
load_dotenv()
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db import IntegrityError
from .models import EmailSubscriber



def landing(request):
    total_email_subscribers = EmailSubscriber.objects.count()
    tmp_email_subscriber_count = 127 + total_email_subscribers  # TODO: delete afterwards
    return render(request, 'validation/landing.html', {
        'total_email_subscribers': tmp_email_subscriber_count
    })


def blog_post_one(request):
    return render(request, 'validation/blog_post_one.html')


def handle_email_submission(request):
    if request.method == 'POST':
        email = request.POST.get('email', None)
        if not email:
            return JsonResponse({'success': False, 'error': 'Invalid email'}, status=400)

        try:
            em_obj = EmailSubscriber.objects.create(email=email)
            em_obj.save()
            total_email_subscribers = EmailSubscriber.objects.count()

            # TODO:
                # send email to user (do manual first to save time and avoid any errors or further complexity...)

            return JsonResponse({'success': True, 'total_email_subscribers': total_email_subscribers})
        except Exception as e:
            print(f"Unexpected error: {e}")
            return JsonResponse({'success': False, 'error': 'Email already exists', 'duplicate': True})

