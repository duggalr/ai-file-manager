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

class File(models.Model):
    """
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_directory_file_path = models.TextField()
    current_file_path = models.TextField()
    entity_type = models.TextField()
    primary_category = models.TextField()
    sub_categories = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
