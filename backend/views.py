from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, F
from dotenv import load_dotenv
load_dotenv()

import json
import datetime
from hurry.filesize import size
from .models import File
from .scripts import user_file_path_utils


# AJAX
def handle_user_file_path_submit(request):
    if request.method == 'POST':
        user_file_path = request.POST['user_file_path']
        print('user-fp:', user_file_path)

        rv_list = user_file_path_utils.main(
            user_file_path = user_file_path
        )

        for di in rv_list:

            print('json-di:', di)

            fobj = File.objects.create(
                user_directory_file_path = user_file_path,
                current_file_path = di['current_image_file_path'],
                current_file_name = di['current_image_file_name'],

                entity_type = di['entity_type'],
                primary_category = di['primary_category'],
                sub_categories = di['sub_categories'],
    
                file_size_in_bytes = di['file_size'],
                file_last_access_time = di['last_access_time'],
                file_created_at_date_time = di['creation_time'],
                file_modified_at_date_time = di['last_modified_time'],
            )
            fobj.save()

        return JsonResponse({
            'success': True
        })


def home(request):
    return render(request, 'home.html')


def file_view(request):
    # file_objects = File.objects.all()
    # category_dict = {}
    # entity_type_dict = {}
    # for fn_obj in file_objects:

    #     file_size_string = size(fn_obj.file_size_in_bytes)
    #     current_file_name_clean = (fn_obj.current_file_name).capitalize()
    #     fn_last_access_time = datetime.datetime.strftime(fn_obj.file_last_access_time, "%Y-%m-%d")
    #     fn_created_at_time = datetime.datetime.strftime(fn_obj.file_created_at_date_time, "%Y-%m-%d")
    #     fn_modified_at_time = datetime.datetime.strftime(fn_obj.file_modified_at_date_time, "%Y-%m-%d")

    #     file_dict = {
    #         'user_directory_file_path': fn_obj.user_directory_file_path,
    #         'current_file_path': fn_obj.current_file_path,
    #         'current_file_name': current_file_name_clean,

    #         'entity_type': fn_obj.entity_type,
    #         'primary_category': fn_obj.primary_category,
    #         'sub_categories': fn_obj.sub_categories,
    #         'file_size_in_bytes': file_size_string,

    #         'file_size_string': file_size_string,
    #         'file_last_access_time': fn_last_access_time,
    #         'file_created_at_date_time': fn_created_at_time,
    #         'file_modified_at_date_time': fn_modified_at_time,
    #     }

    #     if fn_obj.entity_type in entity_type_dict:
    #         entity_type_dict[fn_obj.entity_type].append(file_dict)
    #     else:
    #         entity_type_dict[fn_obj.entity_type] = [file_dict]

    #     if fn_obj.primary_category in category_dict:
    #         category_dict[fn_obj.primary_category].append(file_dict)
    #     else:
    #         category_dict[fn_obj.primary_category] = [file_dict]
  
    # category_rv = []
    # for ctg in category_dict:
    #     category_rv.append([ctg, category_dict[ctg]])

    # sorted_category_list = sorted(category_rv, key=lambda x: len(x[1]), reverse=True)
    # sorted_category_list_json = json.dumps(sorted_category_list)

    # entity_type_rv = []
    # for et in entity_type_dict:
    #     entity_type_rv.append([et, entity_type_dict[et]])
    
    # sorted_entity_type_list = sorted(entity_type_rv, key=lambda x: len(x[1]), reverse=True)
    # sorted_entity_type_list_json = json.dumps(sorted_entity_type_list)
    # # print(sorted_category_list_json)

    # # TODO: make efficent data structure to manage all breadcrumb navigation

    # file_objects = File.objects.all()
    entity_type_and_file_count = File.objects.values('entity_type').annotate(file_count=Count('entity_type')).order_by('-file_count')
    print(entity_type_and_file_count)

    return render(request, 'new_file_view.html', {
        # 'file_objects': file_objects
        # 'categorized_files': sorted_list,
        # 'sorted_list_json': sorted_list_json
        
        # 'entity_type_list': sorted_entity_type_list,
        # 'category_list': sorted_category_list,
        # 'sorted_entity_type_list_json': sorted_entity_type_list_json,
        # 'sorted_category_list_json': sorted_category_list_json

        'entity_type_and_file_count': entity_type_and_file_count
    })



from django.core import serializers


def handle_filtering_file_data(request):
    if request.method == 'POST':
        filter_data = json.loads(request.POST['filter_data'])

        print('filter_data:', filter_data, type(filter_data))

        current_filter_value = filter_data['current_filter_value']

        if current_filter_value == 'home':
            filtered_file_objects = File.objects.all()
            filtered_file_count = File.objects.annotate(
                primary_text=F('entity_type')
            ).values('primary_text').annotate(file_count=Count('entity_type')).order_by('-file_count')
        
            global_view_type = 'entity'

            serialized_file_objects = []
            for fn_obj in filtered_file_objects:
                file_size_string = size(fn_obj.file_size_in_bytes)
                current_file_name_clean = (fn_obj.current_file_name).capitalize()
                fn_last_access_time = datetime.datetime.strftime(fn_obj.file_last_access_time, "%Y-%m-%d")
                fn_created_at_time = datetime.datetime.strftime(fn_obj.file_created_at_date_time, "%Y-%m-%d")
                fn_modified_at_time = datetime.datetime.strftime(fn_obj.file_modified_at_date_time, "%Y-%m-%d")

                file_dict = {
                    'user_directory_file_path': fn_obj.user_directory_file_path,
                    'current_file_path': fn_obj.current_file_path,
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
            
            if 'entity' in current_filter_value:
                global_filter_type_value = 'category'
                filter_value_string = current_filter_value.split('entity-')[1]
                filtered_entity_list_values.append(filter_value_string)
            elif 'category' in current_filter_value:
                global_filter_type_value = 'entity'
                filter_value_string = current_filter_value.split('category-')[1]
                filtered_category_list_values.append(filter_value_string)

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

            filtered_file_objects = File.objects.filter(**filters)

            print(f"GLOBAL ORIGINAL FILTER VALUE: {original_filter_value}")

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

                serialized_file_count = list(filtered_file_count)

            serialized_file_objects = []
            for fn_obj in filtered_file_objects:
                file_size_string = size(fn_obj.file_size_in_bytes)
                current_file_name_clean = (fn_obj.current_file_name).capitalize()
                fn_last_access_time = datetime.datetime.strftime(fn_obj.file_last_access_time, "%Y-%m-%d")
                fn_created_at_time = datetime.datetime.strftime(fn_obj.file_created_at_date_time, "%Y-%m-%d")
                fn_modified_at_time = datetime.datetime.strftime(fn_obj.file_modified_at_date_time, "%Y-%m-%d")

                file_dict = {
                    'user_directory_file_path': fn_obj.user_directory_file_path,
                    'current_file_path': fn_obj.current_file_path,
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



        # if len(filtered_entity_list_values) > 0 and len(filtered_category_list_values) > 0:
        #     filtered_file_objects = File.objects.filter(
        #         entity_type__in = filtered_entity_list_values,
        #         primary_category__in = filtered_category_list_values
        #     )            

        #     if gloabL_filter_type_value == 'entity':
        #         filtered_file_count = File.objects.filter(
        #             entity_type__in = filtered_entity_list_values,
        #             primary_category__in = filtered_category_list_values
        #         ).annotate(
        #             primary_text = F('primary_category')
        #         ).values('primary_text').annotate(file_count=Count('primary_category')).order_by('-file_count')
        #     else:
        #         pass



        # filter_value = request.POST['filter_value'].strip()
        # view_type = request.POST['view_type'].strip()
        # # print('category:', filter_value, view_type)
        # print(f"Filter: {filter_value} | {filter_value == ""} , View Type: {view_type}")

        # if view_type == 'home':
        #     filtered_file_objects = File.objects.all()
        #     filtered_file_count = File.objects.annotate(
        #         primary_text=F('entity_type')
        #     ).values('primary_text').annotate(file_count=Count('entity_type')).order_by('-file_count')
        
        #     global_view_type = 'entity'

        # elif view_type == 'entity':
        #     filtered_file_objects = File.objects.filter(
        #         entity_type = filter_value
        #     )
        #     filtered_file_count = File.objects.filter(
        #         entity_type = filter_value).annotate(
        #         primary_text=F('primary_category')).values('primary_text').annotate(file_count=Count('primary_category')).order_by('-file_count')
        
        #     global_view_type = 'category'

        # else:
        #     filtered_file_objects = File.objects.filter(
        #         primary_category = filter_value
        #     )
        #     # filtered_file_count = File.objects.filter(
        #     #     primary_category = filter_value).values('entity_type').annotate(file_count=Count('entity_type')).order_by('-file_count')
        #     filtered_file_count = File.objects.filter(
        #         primary_category = filter_value).annotate(
        #         primary_text=F('entity_type')).values('primary_text').annotate(file_count=Count('entity_type')).order_by('-file_count')
            
        #     global_view_type = 'entity'

        # serialized_file_objects = []
        # for fn_obj in filtered_file_objects:
        #     file_size_string = size(fn_obj.file_size_in_bytes)
        #     current_file_name_clean = (fn_obj.current_file_name).capitalize()
        #     fn_last_access_time = datetime.datetime.strftime(fn_obj.file_last_access_time, "%Y-%m-%d")
        #     fn_created_at_time = datetime.datetime.strftime(fn_obj.file_created_at_date_time, "%Y-%m-%d")
        #     fn_modified_at_time = datetime.datetime.strftime(fn_obj.file_modified_at_date_time, "%Y-%m-%d")

        #     file_dict = {
        #         'user_directory_file_path': fn_obj.user_directory_file_path,
        #         'current_file_path': fn_obj.current_file_path,
        #         'current_file_name': current_file_name_clean,

        #         'entity_type': fn_obj.entity_type,
        #         'primary_category': fn_obj.primary_category,
        #         'sub_categories': fn_obj.sub_categories,
        #         'file_size_in_bytes': file_size_string,

        #         'file_size_string': file_size_string,
        #         'file_last_access_time': fn_last_access_time,
        #         'file_created_at_date_time': fn_created_at_time,
        #         'file_modified_at_date_time': fn_modified_at_time,
        #     }
        #     serialized_file_objects.append(file_dict)

        # serialized_file_count = list(filtered_file_count)

        # return JsonResponse({
        #     'success': True,
        #     'filtered_file_objects': serialized_file_objects,
        #     'filtered_file_count': serialized_file_count,
        #     'global_view_type': global_view_type
        # })
