from collections import defaultdict

# # Example File model representation for demonstration
# class File:
#     def __init__(self, entity_type, primary_category, sub_categories):
#         self.entity_type = entity_type
#         self.primary_category = primary_category
#         self.sub_categories = sub_categories
#         self.file_name = "example.txt"  # Add more attributes as needed

# # Sample files
# files = [
#     File("Entity1", "Category1", ["Sub1", "Sub2"]),
#     File("Entity1", "Category1", ["Sub1", "Sub3"]),
#     File("Entity1", "Category2", ["Sub4"]),
#     File("Entity2", "Category1", []),
#     File("Entity2", "Category2", ["Sub5"]),
# ]


from pathlib import Path
import os
import sys
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
parent_path = os.path.join(BASE_DIR, 'ai_file_manager')
print(parent_path)
sys.path.append(parent_path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ai_file_manager.settings")

from datetime import datetime, timedelta
import django
django.setup()

from backend.models import *

# Function to build the category tree
def build_category_tree(files):
    category_tree = defaultdict(lambda: {'files': [], 'sub_categories': defaultdict()})
    
    for file in files:
        # Initialize the root node for the entity type if it doesn't exist
        node = category_tree[file.entity_type]
        
        # If primary category exists, initialize if necessary and move into it
        if file.primary_category:
            if file.primary_category not in node['sub_categories']:
                node['sub_categories'][file.primary_category] = {'files': [], 'sub_categories': defaultdict()}
            node = node['sub_categories'][file.primary_category]

        # Traverse the sub-categories
        for sub_category in file.sub_categories:
            if sub_category not in node['sub_categories']:
                node['sub_categories'][sub_category] = {'files': [], 'sub_categories': defaultdict()}
            node = node['sub_categories'][sub_category]

        # Append the file to the current node's files list
        node['files'].append(file.current_file_name)  

    return category_tree


# # # Build the tree
# # category_tree = build_category_tree(files)

# # # Print the tree for visualization
# # import pprint
# # pprint.pprint(category_tree, width=80, sort_dicts=False)

file_objects = File.objects.all()
print(f"Number of file objects: {len(file_objects)}")

entity_tree = build_category_tree(
    file_objects
)
# # Print the tree for visualization
# import pprint
# # pprint.pprint(category_tree, width=80, sort_dicts=False)
# for k in entity_category_tree:
#     print(k)

# primary_category_tree = build_category_tree()

# TODO: 
    # build the primary category and entity trees
        # integrate in frontned and finalize the functionaltiy with the breadcrumbs (back/forward, view-switching, etc.)