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

class EmailSubscriber(models.Model):
    """
    Landing Page Email Submission
    """
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

class UserOAuth(models.Model):
    """
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    auth_zero_id = models.TextField()
    name = models.TextField()
    email = models.EmailField()
    email_verified = models.BooleanField()
    profile_picture_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class UserProfile(models.Model):
    """
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_auth_obj = models.ForeignKey(UserOAuth, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Directory(models.Model):
    """
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_directory_name = models.TextField()
    user_directory_path = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user_profile_obj = models.ForeignKey(UserProfile, on_delete=models.CASCADE)






# class UserOAuth(models.Model):
#     """
#     User has signed up using Auth0.
#     """
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     auth_type = models.CharField(max_length=500)
#     email = models.EmailField()
#     email_verified = models.BooleanField()
#     name = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)


# class UserProfile(models.Model):
#     """
#     User Profile object containing topic information for each user
#     """
#     # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     user_view_preference = models.TextField(default='entity')
#     files_under_process = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     user_obj = models.ForeignKey(UserOAuth, on_delete=models.CASCADE)


# class Directory(models.Model):
#     """
#     """
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     user_directory_name = models.TextField()
#     user_directory_path = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     user_profile_obj = models.ForeignKey(UserProfile, on_delete=models.CASCADE, blank=True, null=True)


# class File(models.Model):
#     """
#     Model to store file information, screenshots, and processing status.
#     """
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
#     file_path = models.TextField()
#     file_name = models.TextField(blank=True, null=True)
    
#     generated_file_name = models.TextField(blank=True, null=True)
#     entity_type = models.TextField(blank=True, null=True)
#     primary_category = models.TextField(blank=True, null=True)
#     sub_categories = models.JSONField(blank=True, null=True)
    
#     file_size_in_bytes = models.IntegerField(blank=True, null=True)
#     file_last_access_time = models.DateTimeField(blank=True, null=True)
#     file_created_at_date_time = models.DateTimeField(blank=True, null=True)
#     file_modified_at_date_time = models.DateTimeField(blank=True, null=True)
    
#     screenshot_image = models.ImageField(upload_to='screenshots/', blank=True, null=True)
#     processed = models.BooleanField(default=False)

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     directory_object = models.ForeignKey('Directory', on_delete=models.CASCADE, blank=True, null=True)