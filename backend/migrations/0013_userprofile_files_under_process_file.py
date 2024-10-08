# Generated by Django 5.1 on 2024-08-28 19:15

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0012_userprofile_directory'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='files_under_process',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('file_path', models.TextField()),
                ('file_name', models.TextField(blank=True, null=True)),
                ('generated_file_name', models.TextField(blank=True, null=True)),
                ('entity_type', models.TextField(blank=True, null=True)),
                ('primary_category', models.TextField(blank=True, null=True)),
                ('sub_categories', models.JSONField(blank=True, null=True)),
                ('file_size_in_bytes', models.IntegerField(blank=True, null=True)),
                ('file_last_access_time', models.DateTimeField(blank=True, null=True)),
                ('file_created_at_date_time', models.DateTimeField(blank=True, null=True)),
                ('file_modified_at_date_time', models.DateTimeField(blank=True, null=True)),
                ('processed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('directory_object', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='backend.directory')),
            ],
        ),
    ]
