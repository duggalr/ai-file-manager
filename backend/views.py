from dotenv import load_dotenv
load_dotenv()
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, F
from django.db import connection
from django.conf import settings
import os
import json
import datetime
from urllib.parse import quote_plus, urlencode
from hurry.filesize import size
from authlib.integrations.django_client import OAuth

from .models import File, Directory, UserOAuth, UserProfile
# from .scripts.file_process import mp_main_two


oauth = OAuth()
oauth.register(
    "auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
)

def callback(request):
    # token = oauth.auth0.authorize_access_token(request)
    # request.session["user"] = token
    # return redirect(request.build_absolute_uri(reverse("manage_file_path")))

    token = oauth.auth0.authorize_access_token(request)
    request.session["user"] = token

    user_info = token['userinfo']
    user_email = user_info['email']
    user_auth_type = user_info['sub']
    user_email_verified = user_info['email_verified']
    user_name = user_info['name']

    user_auth_objects = UserOAuth.objects.filter(email = user_email)
    user_auth_obj = None
    if len(user_auth_objects) > 0:
        user_auth_obj = user_auth_objects[0]

        up_objects = UserProfile.objects.filter(user_obj = user_auth_obj)
        if len(up_objects) == 0:
            up_object = UserProfile.objects.create(
                user_obj = user_auth_obj,
            )
            up_object.save()
            return redirect(request.build_absolute_uri(reverse("manage_file_path")))
        else:
            up_object = up_objects[0]

            user_profile_directory_objects = Directory.objects.filter(
                user_profile_obj = up_object
            )
            if len(user_profile_directory_objects) > 0:
                return redirect(request.build_absolute_uri(reverse("file_view")))
            else:
                return redirect(request.build_absolute_uri(reverse("manage_file_path")))

    else:
        user_auth_obj = UserOAuth.objects.create(
            auth_type = user_auth_type,
            email = user_email,
            email_verified = user_email_verified,
            name = user_name,
        )
        user_auth_obj.save()

        up_object = UserProfile.objects.create(
            user_obj = user_auth_obj,
        )
        up_object.save()

        return redirect(request.build_absolute_uri(reverse("file_view")))

def login(request):
    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(reverse("callback"))
    )

def logout(request):
    request.session.clear()

    return redirect(
        f"https://{settings.AUTH0_DOMAIN}/v2/logout?"
        + urlencode(
            {
                "returnTo": request.build_absolute_uri(reverse("landing")),
                "client_id": settings.AUTH0_CLIENT_ID,
            },
            quote_via=quote_plus,
        ),
    )


def get_user_profile(request):
    user_dict = request.session.get("user")
    user_auth_obj = None
    if user_dict is not None:
        user_auth_objects = UserOAuth.objects.filter(
            email = user_dict['userinfo']['email']
        )
        if len(user_auth_objects) == 0:
            raise Exception
        
        user_auth_obj = user_auth_objects[0]

    up_objects = UserProfile.objects.filter(
        user_obj = user_auth_obj
    )
    up_obj = None
    if len(up_objects) > 0:
        up_obj = up_objects[0]
        return up_obj
    else:
        return up_obj


def landing(request):
    up_obj = get_user_profile(request)
    return render(request, 'primary/landing.html', {
        'user_profile_object': up_obj
    })


def manage_file_path(request):
    up_obj = get_user_profile(request)
    directory_objects = Directory.objects.filter(
        user_profile_obj = up_obj
    ).order_by('-created_at')
    return render(request, 'dashboard/manage_file_path.html', {
        'user_profile_object': up_obj,
        'directory_objects': directory_objects
    })


def file_view(request):
    up_object = get_user_profile(request)
    directory_object_id = request.GET.get('directory', None)
    
    if directory_object_id is not None:
        directory_object = get_object_or_404(Directory, id = directory_object_id)
        if directory_object.user_profile_obj != up_object:
            return redirect('file_view')

        if up_object.user_view_preference == 'entity':
            final_entity_type_and_file_count = File.objects.filter(
                directory_object = directory_object,
                processed = True
            ).annotate(
                primary_text=F('entity_type')
            ).values('primary_text').annotate(file_count=Count('entity_type')).order_by('-file_count')
        
        elif up_object.user_view_preference == 'category':
            final_entity_type_and_file_count = File.objects.filter(
                directory_object = directory_object,
                processed = True
            ).annotate(
                primary_text=F('primary_category')
            ).values('primary_text').annotate(file_count=Count('primary_category')).order_by('-file_count')
  
        elif up_object.user_view_preference == 'sub_category':        
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
        """, [up_object.id])
        
                results = cursor.fetchall()
                # filtered_file_count = []
                final_entity_type_and_file_count = []
                for li in results:
                    # filtered_file_count.append({
                    final_entity_type_and_file_count.append({
                        'primary_text': li[0],
                        'file_count': li[1]
                    })

    else:
       # entity_type_and_file_count = File.objects.filter(
        #     processed = True,
        # ).values('entity_type').annotate(file_count=Count('entity_type')).order_by('-file_count')

        if up_object.user_view_preference == 'entity':
            final_entity_type_and_file_count = File.objects.filter(
                processed = True,
                directory_object__user_profile_obj = up_object
            ).annotate(
                primary_text=F('entity_type')
            ).values('primary_text').annotate(file_count=Count('entity_type')).order_by('-file_count')

        elif up_object.user_view_preference == 'category':
            final_entity_type_and_file_count = File.objects.filter(
                processed = True,
                directory_object__user_profile_obj = up_object
            ).annotate(
                primary_text=F('primary_category')
            ).values('primary_text').annotate(file_count=Count('primary_category')).order_by('-file_count')

        elif up_object.user_view_preference == 'sub_category':
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
        """, [up_object.id])
        
                results = cursor.fetchall()
                # filtered_file_count = []
                final_entity_type_and_file_count = []
                for li in results:
                    # filtered_file_count.append({
                    final_entity_type_and_file_count.append({
                        'primary_text': li[0],
                        'file_count': li[1]
                    })

        # user_dir_objects = Directory.objects.filter(
        #     user_profile_obj = up_object
        # )
        # final_entity_type_and_file_count = {}
        # for dobj in user_dir_objects:
        #     directory_entity_type_and_file_count = File.objects.filter(
        #         directory_object = dobj,
        #         processed = True
        #     ).values('entity_type').annotate(file_count=Count('entity_type')).order_by('-file_count')
        #     print('tmp:', directory_entity_type_and_file_count)
        #     for ky_dict in directory_entity_type_and_file_count:
        #         print(f"ky-dict: {ky_dict}")
        #         entity_type_ky = ky_dict['entity_type']
        #         entity_type_vl = ky_dict['file_count']
        #         if entity_type_ky in final_entity_type_and_file_count:
        #             final_entity_type_and_file_count[entity_type_ky] += entity_type_vl
        #         else:
        #             final_entity_type_and_file_count[entity_type_ky] = entity_type_vl
        #         # for ky in ky_dict:
        #         #     vl = ky_dict[ky]
        #         #     print(f"tmp-ky {ky} | vl: {vl}")
        #         #     if ky in final_entity_type_and_file_count:
        #         #         final_entity_type_and_file_count[ky] += vl
        #         #     else:
        #         #         final_entity_type_and_file_count[ky] = vl
                
        #         # # vl = directory_entity_type_and_file_count[ky]
        #         # # if ky in final_entity_type_and_file_count:
        #         # #     final_entity_type_and_file_count[ky] += vl
        #         # # else:
        #         # #     final_entity_type_and_file_count[ky] = vl
  
        # print('final-entity-type:', final_entity_type_and_file_count)


        # entity_type_and_file_count = File.objects.filter(
        #     processed = True,
        # ).values('entity_type').annotate(file_count=Count('entity_type')).order_by('-file_count')

    # distinct_user_directory_paths = File.objects.values(
    #     'user_directory_file_path'
    # ).distinct()
    # distinct_dir_names = []
    # for dobj in distinct_user_directory_paths:
    #     dpath = dobj['user_directory_file_path']
    #     directory_name = os.path.basename(dpath)
    #     distinct_dir_names.append([directory_name, dobj])


    directory_objects = Directory.objects.filter(
        user_profile_obj = up_object
    ).order_by('-created_at')

    # final_entity_type_rv_list = []
    # for k in final_entity_type_and_file_count:
    #     vl = final_entity_type_and_file_count[k]
    #     final_entity_type_rv_list.append({
    #         'entity_type': k,
    #         'file_count': vl
    #     })

    # print('entity_type_and_file_count', final_entity_type_rv_list)

    return render(request, 'dashboard/new_file_view.html', {
        # 'distinct_user_directory_list': distinct_dir_names,
        # 'entity_type_and_file_count': final_entity_type_rv_list,
        
        'user_profile_preference': up_object.user_view_preference,        
        'entity_type_and_file_count': final_entity_type_and_file_count,
        'directory_objects': directory_objects,
        'user_profile_object': up_object,
    })


def unprocessed_file_view(request): 
    up_obj = get_user_profile(request)
    directory_objects = Directory.objects.filter(
        user_profile_obj = up_obj
    ).order_by('-created_at')
    
    rv = []
    for dobj in directory_objects:
        file_objects = File.objects.filter(
            directory_object = dobj,
            processed = False
        )
        if len(file_objects) > 0:
            for fobj in file_objects:
                rv.append(fobj)

    return render(request, 'dashboard/unprocessed_file_list.html', {
        'unprocessed_file_objects': rv,
        'directory_objects': directory_objects,
        'user_profile_object': up_obj,
    })


def delete_user_file_path(request, uuid):
    print('uuid', uuid)
    Directory.objects.filter(id=uuid).delete()
    return redirect('manage_file_path')


from .tasks import process_user_directory

## AJAX
def handle_user_file_path_submit(request):
    if request.method == 'POST':

        user_profile_object = get_user_profile(request)
        # print('user-profile-object:', user_profile_object)

        # user_file_path = request.POST['user_file_path']
        user_directory_file_path = request.POST['user_file_path']
        print('user-fp:', user_directory_file_path)

        # rv_list = user_file_path_utils.main(
        #     user_directory_file_path = user_directory_file_path
        # )
        # rv_list = mp_main_two.main(
        #     user_directory_file_path = user_directory_file_path,
        #     user_profile_object = user_profile_object
        # )

        user_profile_object.files_under_process = True
        user_profile_object.save()
        
        task = process_user_directory.delay(
            user_directory_path = user_directory_file_path,
            user_profile_object_id = user_profile_object.id
        )

        print(f"Task ID: {task.id}")

        return JsonResponse({
            'success': True,
            'task_id': task.id  # Send task ID to the frontend
        })

        # user_dir_name = os.path.basename(user_directory_file_path)
        # d_object = Directory.objects.create(
        #     user_directory_name = user_dir_name,
        #     user_directory_path = user_directory_file_path
        # )
        # d_object.save()
        # for di in rv_list:
        #     print('json-di:', di)
        #     fobj = File.objects.create(
        #         file_path = di['file_path'],
        #         file_name = di['file_name'],

        #         entity_type = di['entity_type'],
        #         primary_category = di['primary_category'],
        #         sub_categories = di['sub_categories'],
    
        #         file_size_in_bytes = di['file_size_in_bytes'],
        #         file_last_access_time = di['file_last_access_time'],
        #         file_created_at_date_time = di['file_created_at_date_time'],
        #         file_modified_at_date_time = di['file_modified_at_date_time'],

        #         directory_object = d_object
        #     )
        #     fobj.save()


def handle_filtering_file_data(request):
    if request.method == 'POST':
        filter_data = json.loads(request.POST['filter_data'])
        print('filter_data:', filter_data, type(filter_data))
        current_filter_value = filter_data['current_filter_value']

        user_profile_object = get_user_profile(request)
        print('user-profile-object:', user_profile_object, user_profile_object.user_view_preference)

        if current_filter_value == 'Home':
            # filtered_file_objects = File.objects.all()
            filtered_file_objects = File.objects.filter(
                processed = True,
                directory_object__user_profile_obj = user_profile_object
            )

            if user_profile_object.user_view_preference == 'entity':
                # final_entity_type_and_file_count = File.objects.filter(
                filtered_file_count = File.objects.filter(
                    processed = True,
                    directory_object__user_profile_obj = user_profile_object
                ).annotate(
                    primary_text=F('entity_type')
                ).values('primary_text').annotate(file_count=Count('entity_type')).order_by('-file_count')
            
            elif user_profile_object.user_view_preference == 'category':
                # final_entity_type_and_file_count = File.objects.filter(
                filtered_file_count = File.objects.filter(
                    processed = True,
                    directory_object__user_profile_obj = user_profile_object
                ).annotate(
                    primary_text=F('primary_category')
                ).values('primary_text').annotate(file_count=Count('primary_category')).order_by('-file_count')

            elif user_profile_object.user_view_preference == 'sub_category':
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
            """, [user_profile_object.id])
            
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
            global_view_type = user_profile_object.user_view_preference

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
            breadcrumb_value_list = filter_data['breadcrumb_value_list'][1:]  # always skip the first value since it is home

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
            filters['directory_object__user_profile_obj'] = user_profile_object

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


def switch_filtered_file_data(request):
    if request.method == 'POST':
        print('post-data:', request.POST)

        filter_data = json.loads(request.POST['filter_data'])
        # print('filter_data:', filter_data, type(filter_data))
        current_filter_value = filter_data['current_filter_value']
        switch_view_to_value = filter_data['switch_view_to']
        
        user_profile_object = get_user_profile(request)
        print('user-profile-object:', user_profile_object)

        if current_filter_value == 'Home':
            # filtered_file_objects = File.objects.all()
            filtered_file_objects = File.objects.filter(
                processed = True,
                directory_object__user_profile_obj = user_profile_object
            )                

            if switch_view_to_value == 'entity':
                filtered_file_count = File.objects.filter(
                    processed = True,
                    directory_object__user_profile_obj = user_profile_object
                ).annotate(
                    primary_text=F('entity_type')
                ).values('primary_text').annotate(file_count=Count('entity_type')).order_by('-file_count')
                global_view_type = 'entity'

            # TODO: add sub-categories
            elif switch_view_to_value == 'Sub-Categories':
            #     with connection.cursor() as cursor:
            #         cursor.execute("""
            #             SELECT 
            #     sub_category as primary_text, COUNT(*) as file_count
            # FROM (
            #     SELECT jsonb_array_elements_text(sub_categories) as sub_category
            #     FROM public.backend_file 
            # ) AS subcategory_unnested
            # GROUP BY sub_category
            # ORDER BY file_count DESC
            #         """)
            #         results = cursor.fetchall()
            #         # filtered_file_count = results
            #         global_view_type = 'subcategory'

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
            """, [user_profile_object.id])
            
                    results = cursor.fetchall()
                    global_view_type = 'subcategory'
                            
                    filtered_file_count = []
                    for li in results:
                        filtered_file_count.append({
                            'primary_text': li[0],
                            'file_count': li[1]
                        })
                
            else:
                filtered_file_count = File.objects.filter(
                    processed = True,
                    directory_object__user_profile_obj = user_profile_object
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
            breadcrumb_value_list = filter_data['breadcrumb_value_list'][1:]  # always skip the first value since it is home

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
            filters['directory_object__user_profile_obj'] = user_profile_object
            
            filtered_file_objects = File.objects.filter(**filters)

            print(f"GLOBAL ORIGINAL FILTER VALUE: {original_filter_value}")

            # if len(filtered_entity_list_values) > 0 and len(filtered_category_list_values) > 0:
            #     filtered_file_count = None
            #     serialized_file_count = None
            # else:
            #     if original_filter_value == 'entity':
            #         filtered_file_count = File.objects.filter(
            #             **filters
            #         ).annotate(
            #             primary_text=F('primary_category')
            #         ).values('primary_text').annotate(file_count=Count('primary_category')).order_by('-file_count')
                
            #     elif original_filter_value == 'category':
            #         filtered_file_count = File.objects.filter(
            #             **filters
            #         ).annotate(
            #             primary_text=F('entity_type')
            #         ).values('primary_text').annotate(file_count=Count('entity_type')).order_by('-file_count')

            #     serialized_file_count = list(filtered_file_count)

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


import subprocess
import platform

def open_user_file(request):
    if request.method == 'POST':
        print("POST:", request.POST)

        file_id = request.POST['file_id']
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

    return JsonResponse({'success': False, 'error': 'Invalid request'})


def update_view_preference(request):    
    if request.method == 'POST':
        up_object = get_user_profile(request)
        if up_object is None:
            return JsonResponse({'success': False, 'message': 'Authentication Error.'})

        new_preference = request.POST.get('preference')
        print('usr-pref:', new_preference)
        up_object.user_view_preference = new_preference
        up_object.save()
        return JsonResponse({'success': True, 'message': 'Preference updated successfully.'})

    return JsonResponse({'success': False, 'message': 'Invalid request.'})



def check_processing_status(request):
    user_profile_object = get_user_profile(request)
    return JsonResponse({
        'files_under_process': user_profile_object.files_under_process
    })

