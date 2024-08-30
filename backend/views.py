from dotenv import load_dotenv
load_dotenv()
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.db.models import Count, F
from .models import EmailSubscriber, UserOAuth, Directory, UserProfile, File
from .scripts_two import token_validation


# def landing(request):
#     total_email_subscribers = EmailSubscriber.objects.count()
#     tmp_email_subscriber_count = 127 + total_email_subscribers  # TODO: delete afterwards
#     return render(request, 'validation/landing.html', {
#         'total_email_subscribers': tmp_email_subscriber_count
#     })


# def blog_post_one(request):
#     return render(request, 'validation/blog_post_one.html')


# Helper function to get user object from access token
def get_user_from_token(request):
    # Extract access token from the Authorization header
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return JsonResponse({'success': False, 'message': 'Authorization token is missing'}, status=401), None, None

    try:
        access_token = auth_header.split()[1]
    except IndexError:
        return JsonResponse({'success': False, 'message': 'Invalid token format'}, status=401), None, None

    # Verify the access token
    user_verified, user_info_dict = token_validation.verify_access_token(access_token=access_token)

    print(f"Verified: {user_verified}")
    print(f"User Info Dict: {user_info_dict}")

    if not user_verified or user_info_dict is None:
        return JsonResponse({'success': False, 'message': 'Authorization token is invalid'}, status=403), None, None

    try:
        user_auth_obj = UserOAuth.objects.get(auth_zero_id=user_info_dict['sub'])
        user_profile_obj = UserProfile.objects.get(user_auth_obj=user_auth_obj)
        return None, user_auth_obj, user_profile_obj
    except UserOAuth.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found'}, status=404), None, None
    except UserProfile.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User profile not found'}, status=404), None, None





@csrf_exempt
def get_user_profile_information(request):
    if request.method == 'POST':
        error_response, user_auth_obj, user_profile_obj = get_user_from_token(request)
        if error_response:
            return error_response
        
        return JsonResponse({
            'success': True,
            'user_details': {
                'name': user_auth_obj.name,
                'email': user_auth_obj.email,
                'profile_picture_url': user_auth_obj.profile_picture_url,
            }
        })



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


@csrf_exempt
def save_user_profile(request):
    if request.method == 'POST':
        print('headers:', request.headers)

        access_token = request.headers.get('Authorization').split()[1]
        print('access-token:', access_token)
        if not access_token:
            return JsonResponse({'success': False, 'message': 'Authorization token is missing'}, status=401)
        
        user_verified, user_token_dict = token_validation.verify_access_token(
            access_token = access_token
        )

        if user_verified is False:
            return JsonResponse({'success': False, 'message': 'Authorization token is invalid'}, status=403)

        user_profile_info = json.loads(request.body)

        print(f"Verified: {user_verified}")
        print(f"User Profile Dict: {user_profile_info}")

        user_auth_zero_sub_id = user_profile_info['sub']
        exisiting_user_auth_objects = UserOAuth.objects.filter(
            auth_zero_id = user_auth_zero_sub_id
        )
        if len(exisiting_user_auth_objects) > 0:
            return JsonResponse({'success': True, 'message': 'User profile saved successfully'})
        else:
            user_auth_object = UserOAuth.objects.create(
                auth_zero_id = user_auth_zero_sub_id,
                name = user_profile_info['name'],
                email = user_profile_info['email'],
                email_verified = user_profile_info['email_verified'],
                profile_picture_url = user_profile_info['picture']
            )
            user_auth_object.save()

            user_profile_object = UserProfile.objects.create(
                user_auth_obj = user_auth_object
            )
            user_profile_object.save()
            return JsonResponse({'success': True, 'message': 'User profile saved successfully'})



@csrf_exempt
def get_user_filepaths(request):
    if request.method == 'POST':
        print('headers:', request.headers)
        
        access_token = request.headers.get('Authorization').split()[1]
        if not access_token:
            return JsonResponse({'success': False, 'message': 'Authorization token is missing'}, status=401)
        
        user_verified, user_info_dict = token_validation.verify_access_token(
            access_token = access_token
        )

        print(f"Verified: {user_verified}")
        print(f"User Info Dict: {user_info_dict}")

        if user_info_dict is None:
            return JsonResponse({'success': False, 'message': 'Authorization token is invalid'}, status=403)

        user_auth_obj = UserOAuth.objects.get(
            auth_zero_id = user_info_dict['sub']
        )
        user_profile_obj = UserProfile.objects.get(
            user_auth_obj = user_auth_obj
        )
        directory_objects = Directory.objects.filter(
            user_profile_obj = user_profile_obj
        )

        user_rv_dict = {
            'email': user_profile_obj.user_auth_obj.email,
            'name': user_auth_obj.name,
            'profile_picture_url': user_auth_obj.profile_picture_url,
        }

        dir_rv = [[dobj.id, dobj.user_directory_name, dobj.user_directory_path] for dobj in directory_objects]
        return JsonResponse({
            'success': True,
            'user_directory_list': dir_rv,
            'user_object_details': user_rv_dict
        })


from .tasks import process_user_directory

@csrf_exempt
def check_processing_status(request):
    # user_profile_object = get_user_profile(request)
     # Call the utility function to get user information

    if request.method == 'POST':

        print(request.headers)

        error_response, user_auth_obj, user_profile_obj = get_user_from_token(request)

        if error_response:
            return error_response

        return JsonResponse({
            'files_under_process': user_profile_obj.files_under_process
        })


@csrf_exempt
def handle_user_directory_filepath_submission(request):
    if request.method == 'POST':
        # access_token = request.headers.get('Authorization').split()[1]
        # if not access_token:
        #     return JsonResponse({'success': False, 'message': 'Authorization token is missing'}, status=401)
        
        # user_verified, user_info_dict = token_validation.verify_access_token(
        #     access_token = access_token
        # )

        # print(f"Verified: {user_verified}")
        # print(f"User Info Dict: {user_info_dict}")

        # if user_info_dict is None:
        #     return JsonResponse({'success': False, 'message': 'Authorization token is invalid'}, status=403)

        # user_auth_obj = UserOAuth.objects.get(
        #     auth_zero_id = user_info_dict['sub']
        # )
        # user_profile_obj = UserProfile.objects.get(
        #     user_auth_obj = user_auth_obj
        # )    
        # user_profile_obj.files_under_process = True
        # user_profile_obj.save()

        error_response, user_auth_obj, user_profile_obj = get_user_from_token(request)
        data = json.loads(request.body)

        user_directory_path = data['directory_path']
        task = process_user_directory.delay(
            user_directory_path = user_directory_path,
            user_profile_object_id = user_profile_obj.id
        )

        print(f"Task ID: {task.id}")
        return JsonResponse({
            'success': True,
            'task_id': task.id  # Send task ID to the frontend
        })


# TODO:
@csrf_exempt
def view_directory_files(request):
    if request.method == 'POST':
        print('headers:', request.headers)
        
        access_token = request.headers.get('Authorization').split()[1]
        if not access_token:
            return JsonResponse({'success': False, 'message': 'Authorization token is missing'}, status=401)
        
        user_verified, user_info_dict = token_validation.verify_access_token(
            access_token = access_token
        )

        print(f"Verified: {user_verified}")
        print(f"User Info Dict: {user_info_dict}")

        if user_info_dict is None:
            return JsonResponse({'success': False, 'message': 'Authorization token is invalid'}, status=403)


        data = json.loads(request.body)
        directory_id = data['directory_object_id']

        user_auth_obj = UserOAuth.objects.get(
            auth_zero_id = user_info_dict['sub']
        )
        user_profile_obj = UserProfile.objects.get(
            user_auth_obj = user_auth_obj
        )
        directory_objects = Directory.objects.filter(
            id = directory_id,
            user_profile_obj = user_profile_obj
        )

        if len(directory_objects) == 0:
            return JsonResponse({'success': False, 'message': 'Directory object not found...'}, status=403)
        
        else:
            dir_object = directory_objects[0]

            final_entity_type_and_file_count_rv = []

            if user_profile_obj.user_view_preference == 'entity':
                final_entity_type_and_file_count = File.objects.filter(
                    directory_object = dir_object,
                    processed = True
                ).annotate(
                    primary_text=F('entity_type')
                ).values('primary_text').annotate(file_count=Count('entity_type')).order_by('-file_count')
                
                for itm in final_entity_type_and_file_count:
                    final_entity_type_and_file_count_rv.append({
                        'primary_text': itm['primary_text'],
                        'file_count': itm['file_count']
                    })
            
            elif user_profile_obj.user_view_preference == 'category':
                final_entity_type_and_file_count = File.objects.filter(
                    directory_object = dir_object,
                    processed = True
                ).annotate(
                    primary_text=F('primary_category')
                ).values('primary_text').annotate(file_count=Count('primary_category')).order_by('-file_count')

                for itm in final_entity_type_and_file_count:
                    final_entity_type_and_file_count_rv.append({
                        'primary_text': itm['primary_text'],
                        'file_count': itm['file_count']
                    })
    
            elif user_profile_obj.user_view_preference == 'sub_category':        
                with connection.cursor() as cursor:
                    cursor.execute("""
                SELECT 
                    sub_category as primary_text, COUNT(*) as file_count
                FROM (
                    SELECT jsonb_array_elements_text(sub_categories) as sub_category
                    FROM public.backend_file 
                    WHERE processed = true
                    AND directory_object_id IN (
                        SELECT id FROM public.backend_directory
                        WHERE user_profile_obj_id = %s
                    )
                ) AS subcategory_unnested
                GROUP BY sub_category
                ORDER BY file_count DESC
            """, [user_profile_obj.id])
            
                    results = cursor.fetchall()
                    # # filtered_file_count = []
                    # final_entity_type_and_file_count = []
                    for li in results:
                        # filtered_file_count.append({
                        # final_entity_type_and_file_count.append({
                        final_entity_type_and_file_count_rv.append({
                            'primary_text': li[0],
                            'file_count': li[1]
                        })

            return JsonResponse({
                'success': True,
                'user_profile_preference': user_profile_obj.user_view_preference,
                'entity_type_and_file_count': final_entity_type_and_file_count_rv,
                # 'directory_objects': directory_objects,
                # 'user_profile_object': user_profile_obj,
            })



@csrf_exempt
def update_view_preference(request):
    if request.method == 'POST':
       
        print('headers:', request.headers)
        
        access_token = request.headers.get('Authorization').split()[1]
        if not access_token:
            return JsonResponse({'success': False, 'message': 'Authorization token is missing'}, status=401)
        
        user_verified, user_info_dict = token_validation.verify_access_token(
            access_token = access_token
        )

        print(f"Verified: {user_verified}")
        print(f"User Info Dict: {user_info_dict}")

        if user_info_dict is None:
            return JsonResponse({'success': False, 'message': 'Authorization token is invalid'}, status=403)

        data = json.loads(request.body)
        user_preference = data['preference']

        user_auth_obj = UserOAuth.objects.get(
            auth_zero_id = user_info_dict['sub']
        )
        user_profile_obj = UserProfile.objects.get(
            user_auth_obj = user_auth_obj
        )
        user_profile_obj.user_view_preference = user_preference
        user_profile_obj.save()
        
        return JsonResponse({'success': True, 'message': 'Preference updated successfully.'})

    return JsonResponse({'success': False, 'message': 'Invalid request.'})



# TODO: finalize this function and go from there
@csrf_exempt
def switch_filtered_file_data(request):
    if request.method == 'POST':
        print('post-data:', request.POST)

        access_token = request.headers.get('Authorization').split()[1]
        if not access_token:
            return JsonResponse({'success': False, 'message': 'Authorization token is missing'}, status=401)
        
        user_verified, user_info_dict = token_validation.verify_access_token(
            access_token = access_token
        )

        print(f"Verified: {user_verified}")
        print(f"User Info Dict: {user_info_dict}")

        if user_info_dict is None:
            return JsonResponse({'success': False, 'message': 'Authorization token is invalid'}, status=403)

        # TODO: implement from github from here...

