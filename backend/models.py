from django.db import models
import uuid

# {
#     "entity_type": "Paper",
#     "primary_category": "Research Study",
#     "sub_categories": [
#         "Business",
#         "Entrepreneurship",
#         "Finance",
#         "Investment Analysis"
#     ]
# }


# TODO: 
    # start by modifying the save method and then all other code to handle this new modal change; go from there

class Directory(models.Model):
    """
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_directory_name = models.TextField()
    user_directory_path = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class File(models.Model):
    """
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # user_directory_file_path = models.TextField()    
    
    file_path = models.TextField()
    file_name = models.TextField(blank=True, null=True)
    
    entity_type = models.TextField()
    primary_category = models.TextField()
    sub_categories = models.JSONField()
    
    file_size_in_bytes = models.IntegerField(blank=True, null=True)
    file_last_access_time = models.DateTimeField(blank=True, null=True)
    file_created_at_date_time = models.DateTimeField(blank=True, null=True)
    file_modified_at_date_time = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    directory_object = models.ForeignKey(Directory, on_delete=models.CASCADE, blank=True, null=True)
