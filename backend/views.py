from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, F
from django.db import connection
from dotenv import load_dotenv
load_dotenv()
import os
import json
import datetime
from hurry.filesize import size
from .models import File, Directory
# from .scripts import user_file_path_utils
from .scripts.file_process import mp_main_two


# def home(request):
#     return render(request, 'home.html')


def manage_file_path(request):
    directory_objects = Directory.objects.all().order_by('-created_at')
    return render(request, 'dashboard/manage_file_path.html', {
        'directory_objects': directory_objects
    })


def file_view(request):

    # file_object_id = request.GET['directory']
    directory_object_id = request.GET.get('directory', None)

    if directory_object_id is not None:
        directory_object = get_object_or_404(Directory, id = directory_object_id)
    # else:
    #     directory_object = Directory.objects.all().order_by('-created_at').first()
        entity_type_and_file_count = File.objects.filter(
            directory_object = directory_object,
            processed = True
        ).values('entity_type').annotate(file_count=Count('entity_type')).order_by('-file_count')
  
    else:
        entity_type_and_file_count = File.objects.filter(
            processed = True
        ).values('entity_type').annotate(file_count=Count('entity_type')).order_by('-file_count')

    # distinct_user_directory_paths = File.objects.values(
    #     'user_directory_file_path'
    # ).distinct()
    # distinct_dir_names = []
    # for dobj in distinct_user_directory_paths:
    #     dpath = dobj['user_directory_file_path']
    #     directory_name = os.path.basename(dpath)
    #     distinct_dir_names.append([directory_name, dobj])

    directory_objects = Directory.objects.all().order_by('-created_at')

    return render(request, 'dashboard/new_file_view.html', {
        # 'distinct_user_directory_list': distinct_dir_names,
        'entity_type_and_file_count': entity_type_and_file_count,
        'directory_objects': directory_objects
    })


def unprocessed_file_view(request):
    file_objects = File.objects.filter(
        processed = False
    )

    directory_objects = Directory.objects.all().order_by('-created_at')
    return render(request, 'dashboard/unprocessed_file_list.html', {
        'file_objects': file_objects,
        'directory_objects': directory_objects
    })



def delete_user_file_path(request, uuid):
    print('uuid', uuid)
    Directory.objects.filter(id=uuid).delete()
    return redirect('manage_file_path')


## AJAX
def handle_user_file_path_submit(request):
    if request.method == 'POST':
        # user_file_path = request.POST['user_file_path']
        user_directory_file_path = request.POST['user_file_path']
        print('user-fp:', user_directory_file_path)

        # rv_list = user_file_path_utils.main(
        #     user_directory_file_path = user_directory_file_path
        # )
        rv_list = mp_main_two.main(
            user_directory_file_path = user_directory_file_path
        )

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

        return JsonResponse({
            'success': True
        })


def handle_filtering_file_data(request):
    if request.method == 'POST':
        filter_data = json.loads(request.POST['filter_data'])

        print('filter_data:', filter_data, type(filter_data))

        current_filter_value = filter_data['current_filter_value']

        if current_filter_value == 'Home':
            # filtered_file_objects = File.objects.all()
            filtered_file_objects = File.objects.filter(
                processed = True
            )

            # if 'switch_view_to' in filter_data:
            #     switch_view_to_value = filter_data['switch_view_to']
            #     if switch_view_to_value == 'entity':
            #         filtered_file_count = File.objects.annotate(
            #             primary_text=F('entity_type')
            #         ).values('primary_text').annotate(file_count=Count('entity_type')).order_by('-file_count')
            #         global_view_type = 'entity'

            #     else:
            #         filtered_file_count = File.objects.annotate(
            #             primary_text=F('primary_category')
            #         ).values('primary_text').annotate(file_count=Count('primary_category')).order_by('-file_count')
            #         global_view_type = 'category'

            # else:
            #     filtered_file_count = File.objects.annotate(
            #         primary_text=F('entity_type')
            #     ).values('primary_text').annotate(file_count=Count('entity_type')).order_by('-file_count')
            
            #     global_view_type = 'entity'


            filtered_file_count = File.objects.filter(processed = True).annotate(
                primary_text=F('entity_type')
            ).values('primary_text').annotate(file_count=Count('entity_type')).order_by('-file_count')
            global_view_type = 'entity'

            serialized_file_objects = []
            for fn_obj in filtered_file_objects:
                file_size_string = size(fn_obj.file_size_in_bytes)
                # current_file_name_clean = (fn_obj.file_name).capitalize()
                current_file_name_clean = (fn_obj.generated_file_name).capitalize()

                fn_last_access_time = datetime.datetime.strftime(fn_obj.file_last_access_time, "%Y-%m-%d")
                fn_created_at_time = datetime.datetime.strftime(fn_obj.file_created_at_date_time, "%Y-%m-%d")
                fn_modified_at_time = datetime.datetime.strftime(fn_obj.file_modified_at_date_time, "%Y-%m-%d")

                file_dict = {
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

        if current_filter_value == 'Home':
            # filtered_file_objects = File.objects.all()
            filtered_file_objects = File.objects.filter(
                processed = True
            )
                
            if switch_view_to_value == 'entity':
                filtered_file_count = File.objects.filter(
                    processed = True
                ).annotate(
                    primary_text=F('entity_type')
                ).values('primary_text').annotate(file_count=Count('entity_type')).order_by('-file_count')
                global_view_type = 'entity'

            # TODO: add sub-categories
            elif switch_view_to_value == 'Sub-Categories':
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT 
                sub_category as primary_text, COUNT(*) as file_count
            FROM (
                SELECT jsonb_array_elements_text(sub_categories) as sub_category
                FROM public.backend_file 
            ) AS subcategory_unnested
            GROUP BY sub_category
            ORDER BY file_count DESC
                    """)
                    results = cursor.fetchall()
                    # filtered_file_count = results
                    global_view_type = 'subcategory'
                    
                    filtered_file_count = []
                    for li in results:
                        filtered_file_count.append({
                            'primary_text': li[0],
                            'file_count': li[1]
                        })
                
            else:
                filtered_file_count = File.objects.filter(
                    processed = True
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
