# Generated by Django 5.1 on 2024-08-15 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0005_file_processed_file_screenshot_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='generated_file_name',
            field=models.TextField(blank=True, null=True),
        ),
    ]
