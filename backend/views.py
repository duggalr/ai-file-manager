from dotenv import load_dotenv
load_dotenv()
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import EmailSubscriber


# def landing(request):
#     total_email_subscribers = EmailSubscriber.objects.count()
#     tmp_email_subscriber_count = 127 + total_email_subscribers  # TODO: delete afterwards
#     return render(request, 'validation/landing.html', {
#         'total_email_subscribers': tmp_email_subscriber_count
#     })


# def blog_post_one(request):
#     return render(request, 'validation/blog_post_one.html')


@csrf_exempt
def handle_email_submission(request):
    print('post', request.POST)
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email', None)
        if not email:
            return JsonResponse({'success': False, 'error': 'Invalid email'}, status=400)
        try:
            em_obj = EmailSubscriber.objects.create(email=email)
            em_obj.save()
            total_email_subscribers = EmailSubscriber.objects.count()
            return JsonResponse({'success': True, 'total_email_subscribers': total_email_subscribers})
        except Exception as e:
            print(f"Unexpected error: {e}")
            return JsonResponse({'success': False, 'error': 'Email already exists', 'duplicate': True})


@csrf_exempt
def get_email_subscriber_count(request):
    if request.method == 'POST':
        total_email_subscribers = EmailSubscriber.objects.count()
        tmp_email_subscriber_count = 127 + total_email_subscribers  # TODO: delete afterwards
        return JsonResponse({'total_email_subscribers': tmp_email_subscriber_count})
