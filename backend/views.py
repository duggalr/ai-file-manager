from dotenv import load_dotenv
load_dotenv()
import json
import datetime
from hurry.filesize import size
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

        # if user_profile_obj.files_under_process is False:  # the processing has been completed
        #     return JsonResponse({
        #         'files_under_process': user_profile_obj.files_under_process,
        #     })

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
        directory_id = data['directory_object_id']  # TODO: verify this dir id

        # print('DIRECTORY OBJECT ID:', directory_id, directory_id == 'null')

        user_auth_obj = UserOAuth.objects.get(
            auth_zero_id = user_info_dict['sub']
        )
        user_profile_obj = UserProfile.objects.get(
            user_auth_obj = user_auth_obj
        )
        # print('user-profile-object:', user_profile_obj, directory_id)

        if directory_id == 'null':
            directory_objects = Directory.objects.filter(
                user_profile_obj = user_profile_obj
            )
        else:
            directory_objects = Directory.objects.filter(
                id = directory_id,
                user_profile_obj = user_profile_obj
            )

        if len(directory_objects) == 0:
            return JsonResponse({'success': False, 'message': 'Directory object not found...'}, status=400)
        
        else:
            final_entity_type_and_file_count_rv = []

            # # TODO: go through the directory objects
            # dir_object = directory_objects[0]

            for dir_object in directory_objects:

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

        user_auth_obj = UserOAuth.objects.get(
            auth_zero_id = user_info_dict['sub']
        )
        user_profile_obj = UserProfile.objects.get(
            user_auth_obj = user_auth_obj
        )

        data = json.loads(request.body)
        current_filter_value = data['current_filter_value']        
        switch_view_to_value = data['switch_view_to']

        directory_object_id = data['directory_object_id']

        if current_filter_value == 'Home':

            if directory_object_id == 'null':
                filtered_file_objects = File.objects.filter(
                    processed = True,
                    directory_object__user_profile_obj = user_profile_obj
                )
            else:
                directory_obj = Directory.objects.get(
                    id = directory_object_id,
                    user_profile_obj = user_profile_obj
                )
                filtered_file_objects = File.objects.filter(
                    processed = True,
                    directory_object = directory_obj,
                    directory_object__user_profile_obj = user_profile_obj
                )

            if switch_view_to_value == 'entity':
                
                if directory_object_id == 'null':
                    filtered_file_count = File.objects.filter(
                        processed = True,
                        directory_object__user_profile_obj = user_profile_obj
                    ).annotate(
                        primary_text=F('entity_type')
                    ).values('primary_text').annotate(file_count=Count('entity_type')).order_by('-file_count')
                    global_view_type = 'entity'
                else:
                    directory_obj = Directory.objects.get(
                        id = directory_object_id,
                        user_profile_obj = user_profile_obj
                    )
                    filtered_file_count = File.objects.filter(
                        processed = True,
                        directory_object = directory_obj,
                        directory_object__user_profile_obj = user_profile_obj
                    ).annotate(
                        primary_text=F('entity_type')
                    ).values('primary_text').annotate(file_count=Count('entity_type')).order_by('-file_count')
                    global_view_type = 'entity'


            # TODO: add sub-categories
            elif switch_view_to_value == 'Sub-Categories':

                if directory_object_id == 'null':
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
                        global_view_type = 'subcategory'
                                
                        filtered_file_count = []
                        for li in results:
                            filtered_file_count.append({
                                'primary_text': li[0],
                                'file_count': li[1]
                            })
                else:
                    with connection.cursor() as cursor:
                        cursor.execute("""
                    SELECT 
                        sub_category as primary_text, COUNT(*) as file_count
                    FROM (
                        SELECT jsonb_array_elements_text(sub_categories) as sub_category
                        FROM public.backend_file 
                        WHERE processed = true
                        AND directory_object_id = %s
                    ) AS subcategory_unnested
                    GROUP BY sub_category
                    ORDER BY file_count DESC
                """, [directory_object_id])
                
                        results = cursor.fetchall()
                        global_view_type = 'subcategory'
                                
                        filtered_file_count = []
                        for li in results:
                            filtered_file_count.append({
                                'primary_text': li[0],
                                'file_count': li[1]
                            })
                
            else:

                if directory_object_id == 'null':
                    filtered_file_count = File.objects.filter(
                        processed = True,
                        directory_object__user_profile_obj = user_profile_obj
                    ).annotate(
                        primary_text=F('primary_category')
                    ).values('primary_text').annotate(file_count=Count('primary_category')).order_by('-file_count')
                    global_view_type = 'category'

                else:
                    directory_obj = Directory.objects.get(
                        id = directory_object_id,
                        user_profile_obj = user_profile_obj
                    )
                    filtered_file_count = File.objects.filter(
                        processed = True,
                        directory_object = directory_obj,
                        directory_object__user_profile_obj = user_profile_obj
                    ).annotate(
                        primary_text=F('primary_category')
                    ).values('primary_text').annotate(file_count=Count('primary_category')).order_by('-file_count')
                    global_view_type = 'category'


            serialized_file_objects = []
            for fn_obj in filtered_file_objects:
                file_size_string = size(fn_obj.file_size_in_bytes)
                current_file_name_clean = (fn_obj.file_name).capitalize()
                fn_last_access_time = datetime.datetime.strftime(fn_obj.file_last_access_time, "%Y-%m-%d")
                fn_created_at_time = datetime.datetime.strftime(fn_obj.file_created_at_date_time, "%Y-%m-%d")
                fn_modified_at_time = datetime.datetime.strftime(fn_obj.file_modified_at_date_time, "%Y-%m-%d")

                file_dict = {
                    # 'user_directory_file_path': fn_obj.user_directory_file_path,
                    # 'current_file_path': fn_obj.current_file_path,
                    # 'current_file_name': current_file_name_clean,

                    'file_object_id': fn_obj.id,

                    'user_directory_name': fn_obj.directory_object.user_directory_name,
                    'user_directory_file_path': fn_obj.directory_object.user_directory_path,
                    'current_file_path': fn_obj.file_path,
                    'current_file_name': current_file_name_clean,

                    'entity_type': fn_obj.entity_type,
                    'primary_category': fn_obj.primary_category,
                    'sub_categories': fn_obj.sub_categories,
                    'file_size_in_bytes': file_size_string,

                    'file_size_string': file_size_string,
                    'file_last_access_time': fn_last_access_time,
                    'file_created_at_date_time': fn_created_at_time,
                    'file_modified_at_date_time': fn_modified_at_time,
                }
                serialized_file_objects.append(file_dict)

            serialized_file_count = list(filtered_file_count)
            return JsonResponse({
                'success': True,
                'filtered_file_objects': serialized_file_objects,
                'filtered_file_count': serialized_file_count,
                'global_view_type': global_view_type,
                'home': True
            })


        else:
            # breadcrumb_value_list = filter_data['breadcrumb_value_list'][1:]  # always skip the first value since it is home
            breadcrumb_value_list = data['breadcrumb_value_list'][1:]  # always skip the first value since it is home

            filtered_entity_list_values = []
            filtered_category_list_values = []
            original_filter_value = current_filter_value.split('-')[0]
            global_filter_type_value = ''
            
            # if 'entity' in current_filter_value:
            #     global_filter_type_value = 'category'
            #     filter_value_string = current_filter_value.split('entity-')[1]
            #     filtered_entity_list_values.append(filter_value_string)
            # elif 'category' in current_filter_value:
            #     global_filter_type_value = 'entity'
            #     filter_value_string = current_filter_value.split('category-')[1]
            #     filtered_category_list_values.append(filter_value_string)

            for bc in breadcrumb_value_list:
                if 'entity' in bc:
                    filter_value_string = bc.split('entity-')[1]
                    filtered_entity_list_values.append(filter_value_string)
                elif 'category' in bc:
                    filter_value_string = bc.split('category-')[1]
                    filtered_category_list_values.append(filter_value_string)

            filtered_entity_list_values = list(set(filtered_entity_list_values))
            filtered_category_list_values = list(set(filtered_category_list_values))
            print('filtered_entity_list_values:', filtered_entity_list_values)
            print('filtered_category_list_values:', filtered_category_list_values)

            filters = {}
            if filtered_entity_list_values:
                filters['entity_type__in'] = filtered_entity_list_values
            if filtered_category_list_values:
                filters['primary_category__in'] = filtered_category_list_values

            filters['processed'] = True
            filters['directory_object__user_profile_obj'] = user_profile_obj

            if directory_object_id != 'null':
                directory_obj = Directory.objects.filter(
                    id = directory_object_id,
                    user_profile_obj = user_profile_obj
                )
                filters['directory_object'] = directory_obj


            filtered_file_objects = File.objects.filter(**filters)
            print(f"GLOBAL ORIGINAL FILTER VALUE: {original_filter_value}")

            if switch_view_to_value == 'entity':
                filtered_file_count = File.objects.filter(
                    **filters
                ).annotate(
                    primary_text=F('entity_type')
                ).values('primary_text').annotate(file_count=Count('entity_type')).order_by('-file_count')

                global_view_type = 'entity'

            else:
                filtered_file_count = File.objects.filter(
                    **filters
                ).annotate(
                    primary_text=F('primary_category')
                ).values('primary_text').annotate(file_count=Count('primary_category')).order_by('-file_count')
                global_view_type = 'category'

            serialized_file_objects = []
            for fn_obj in filtered_file_objects:
                file_size_string = size(fn_obj.file_size_in_bytes)
                current_file_name_clean = (fn_obj.file_name).capitalize()
                fn_last_access_time = datetime.datetime.strftime(fn_obj.file_last_access_time, "%Y-%m-%d")
                fn_created_at_time = datetime.datetime.strftime(fn_obj.file_created_at_date_time, "%Y-%m-%d")
                fn_modified_at_time = datetime.datetime.strftime(fn_obj.file_modified_at_date_time, "%Y-%m-%d")

                file_dict = {
                    # 'user_directory_file_path': fn_obj.user_directory_file_path,
                    # 'current_file_path': fn_obj.current_file_path,
                    # 'current_file_name': current_file_name_clean,

                    'file_object_id': fn_obj.id,

                    'user_directory_name': fn_obj.directory_object.user_directory_name,
                    'user_directory_file_path': fn_obj.directory_object.user_directory_path,
                    'current_file_path': fn_obj.file_path,
                    'current_file_name': current_file_name_clean,

                    'entity_type': fn_obj.entity_type,
                    'primary_category': fn_obj.primary_category,
                    'sub_categories': fn_obj.sub_categories,
                    'file_size_in_bytes': file_size_string,

                    'file_size_string': file_size_string,
                    'file_last_access_time': fn_last_access_time,
                    'file_created_at_date_time': fn_created_at_time,
                    'file_modified_at_date_time': fn_modified_at_time,
                }
                serialized_file_objects.append(file_dict)

            serialized_file_count = list(filtered_file_count)

            print('RETURN GLOBAL VIEW TYPE:', global_view_type)

            return JsonResponse({
                'success': True,
                'filtered_file_objects': serialized_file_objects,
                'filtered_file_count': serialized_file_count,
                'global_view_type': global_filter_type_value,
                'home': False
            })



@csrf_exempt
def handle_filtering_file_data(request):
    if request.method == 'POST':
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

        user_auth_obj = UserOAuth.objects.get(
            auth_zero_id = user_info_dict['sub']
        )
        user_profile_obj = UserProfile.objects.get(
            user_auth_obj = user_auth_obj
        )

        data = json.loads(request.body)
        current_filter_value = data['current_filter_value']

        if current_filter_value == 'Home':
            # filtered_file_objects = File.objects.all()
            filtered_file_objects = File.objects.filter(
                processed = True,
                directory_object__user_profile_obj = user_profile_obj
            )

            if user_profile_obj.user_view_preference == 'entity':
                # final_entity_type_and_file_count = File.objects.filter(
                filtered_file_count = File.objects.filter(
                    processed = True,
                    directory_object__user_profile_obj = user_profile_obj
                ).annotate(
                    primary_text=F('entity_type')
                ).values('primary_text').annotate(file_count=Count('entity_type')).order_by('-file_count')
            
            elif user_profile_obj.user_view_preference == 'category':
                # final_entity_type_and_file_count = File.objects.filter(
                filtered_file_count = File.objects.filter(
                    processed = True,
                    directory_object__user_profile_obj = user_profile_obj
                ).annotate(
                    primary_text=F('primary_category')
                ).values('primary_text').annotate(file_count=Count('primary_category')).order_by('-file_count')

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
                    filtered_file_count = []
                    # final_entity_type_and_file_count = []
                    for li in results:
                        filtered_file_count.append({
                        # final_entity_type_and_file_count.append({
                            'primary_text': li[0],
                            'file_count': li[1]
                        })

            # global_view_type = 'entity'
            global_view_type = user_profile_obj.user_view_preference

            serialized_file_objects = []
            for fn_obj in filtered_file_objects:
                file_size_string = size(fn_obj.file_size_in_bytes)
                # current_file_name_clean = (fn_obj.file_name).capitalize()
                current_file_name_clean = (fn_obj.generated_file_name).capitalize()

                fn_last_access_time = datetime.datetime.strftime(fn_obj.file_last_access_time, "%Y-%m-%d")
                fn_created_at_time = datetime.datetime.strftime(fn_obj.file_created_at_date_time, "%Y-%m-%d")
                fn_modified_at_time = datetime.datetime.strftime(fn_obj.file_modified_at_date_time, "%Y-%m-%d")

                file_dict = {
                    'file_object_id': fn_obj.id,

                    'user_directory_name': fn_obj.directory_object.user_directory_name,
                    'user_directory_file_path': fn_obj.directory_object.user_directory_path,
                    'current_file_path': fn_obj.file_path,
                    'current_file_name': current_file_name_clean,

                    'entity_type': fn_obj.entity_type,
                    'primary_category': fn_obj.primary_category,
                    'sub_categories': fn_obj.sub_categories,
                    'file_size_in_bytes': file_size_string,

                    'file_size_string': file_size_string,
                    'file_last_access_time': fn_last_access_time,
                    'file_created_at_date_time': fn_created_at_time,
                    'file_modified_at_date_time': fn_modified_at_time,
                }
                serialized_file_objects.append(file_dict)

            serialized_file_count = list(filtered_file_count)
            return JsonResponse({
                'success': True,
                'filtered_file_objects': serialized_file_objects,
                'filtered_file_count': serialized_file_count,
                'global_view_type': global_view_type,
                'home': True
            })

        else:
            breadcrumb_value_list = data['breadcrumb_value_list'][1:]  # always skip the first value since it is home

            filtered_entity_list_values = []
            filtered_category_list_values = []
            filtered_subcategory_list_values = []
            original_filter_value = current_filter_value.split('-')[0]
            global_filter_type_value = ''
            
            print(original_filter_value, breadcrumb_value_list)

            if 'entity' in current_filter_value:
                global_filter_type_value = 'category'
                filter_value_string = current_filter_value.split('entity-')[1]
                filtered_entity_list_values.append(filter_value_string)
            elif 'subcategory' in current_filter_value:
                global_filter_type_value = 'entity'
                filter_value_string = current_filter_value.split('subcategory-')[1]
                filtered_subcategory_list_values.append(filter_value_string)
            elif 'category' in current_filter_value:
                global_filter_type_value = 'entity'
                filter_value_string = current_filter_value.split('category-')[1]
                filtered_category_list_values.append(filter_value_string)

            for bc in breadcrumb_value_list:
                if 'entity' in bc:
                    filter_value_string = bc.split('entity-')[1]
                    filtered_entity_list_values.append(filter_value_string)
                elif 'subcategory' in bc:
                    filter_value_string = bc.split('subcategory-')[1]
                    filtered_subcategory_list_values.append(filter_value_string)
                elif 'category' in bc:
                    filter_value_string = bc.split('category-')[1]
                    filtered_category_list_values.append(filter_value_string)

            filtered_entity_list_values = list(set(filtered_entity_list_values))
            filtered_category_list_values = list(set(filtered_category_list_values))
            filtered_subcategory_list_values = list(set(filtered_subcategory_list_values))
            print('filtered_entity_list_values:', filtered_entity_list_values)
            print('filtered_category_list_values:', filtered_category_list_values)
            print('filtered_subcategory_list_values:', filtered_subcategory_list_values)

            filters = {}
            if filtered_entity_list_values:
                filters['entity_type__in'] = filtered_entity_list_values
            if filtered_category_list_values:
                filters['primary_category__in'] = filtered_category_list_values
            if filtered_subcategory_list_values:
                filters['sub_categories__contains'] = filtered_subcategory_list_values

            filters['processed'] = True
            filters['directory_object__user_profile_obj'] = user_profile_obj

            filtered_file_objects = File.objects.filter(**filters)

            print(f"GLOBAL ORIGINAL FILTER VALUE: {original_filter_value}")
            print(f"ALL FILTER LISTER: {filters}")

            if len(filtered_entity_list_values) > 0 and len(filtered_category_list_values) > 0:
                filtered_file_count = None
                serialized_file_count = None
            else:
                if original_filter_value == 'entity':
                    filtered_file_count = File.objects.filter(
                        **filters
                    ).annotate(
                        primary_text=F('primary_category')
                    ).values('primary_text').annotate(file_count=Count('primary_category')).order_by('-file_count')

                elif original_filter_value == 'category':
                    filtered_file_count = File.objects.filter(
                        **filters
                    ).annotate(
                        primary_text=F('entity_type')
                    ).values('primary_text').annotate(file_count=Count('entity_type')).order_by('-file_count')

                elif original_filter_value == 'subcategory':
                    filtered_file_count = File.objects.filter(
                        **filters
                    ).annotate(
                        primary_text=F('entity_type')
                    ).values('primary_text').annotate(file_count=Count('entity_type')).order_by('-file_count')

                serialized_file_count = list(filtered_file_count)

            serialized_file_objects = []
            for fn_obj in filtered_file_objects:
                file_size_string = size(fn_obj.file_size_in_bytes)
                # current_file_name_clean = (fn_obj.file_name).capitalize()
                current_file_name_clean = (fn_obj.generated_file_name).capitalize()
                
                fn_last_access_time = datetime.datetime.strftime(fn_obj.file_last_access_time, "%Y-%m-%d")
                fn_created_at_time = datetime.datetime.strftime(fn_obj.file_created_at_date_time, "%Y-%m-%d")
                fn_modified_at_time = datetime.datetime.strftime(fn_obj.file_modified_at_date_time, "%Y-%m-%d")

                file_dict = {
                    # 'user_directory_file_path': fn_obj.user_directory_file_path,
                    # 'current_file_path': fn_obj.current_file_path,
                    # 'current_file_name': current_file_name_clean,

                    'file_object_id': fn_obj.id,

                    'user_directory_name': fn_obj.directory_object.user_directory_name,
                    'user_directory_file_path': fn_obj.directory_object.user_directory_path,
                    'current_file_path': fn_obj.file_path,
                    'current_file_name': current_file_name_clean,

                    'entity_type': fn_obj.entity_type,
                    'primary_category': fn_obj.primary_category,
                    'sub_categories': fn_obj.sub_categories,
                    'file_size_in_bytes': file_size_string,

                    'file_size_string': file_size_string,
                    'file_last_access_time': fn_last_access_time,
                    'file_created_at_date_time': fn_created_at_time,
                    'file_modified_at_date_time': fn_modified_at_time,
                }
                serialized_file_objects.append(file_dict)

            return JsonResponse({
                'success': True,
                'filtered_file_objects': serialized_file_objects,
                'filtered_file_count': serialized_file_count,
                'global_view_type': global_filter_type_value,
                'home': False
            })


import os
import subprocess
import platform

@csrf_exempt
def open_user_file(request):
    if request.method == 'POST':
        # print("POST-open-file:", request.POST)
        data = json.loads(request.body)

        file_id = data['file_id']
        try:
            file = File.objects.get(id=file_id)
            current_file_path = file.file_path
            
            # Open file based on OS
            if platform.system() == 'Darwin':  # macOS
                subprocess.call(('open', current_file_path))
            elif platform.system() == 'Windows':  # Windows
                os.startfile(current_file_path)
            else:  # Linux
                subprocess.call(('xdg-open', current_file_path))

            return JsonResponse({'success': True})
        except File.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'File not found'})

