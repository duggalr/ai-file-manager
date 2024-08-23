# Generated by Django 5.1 on 2024-08-22 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0009_userprofile_files_under_process'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailSubscriber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('subscribed_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='file',
            name='directory_object',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='user_obj',
        ),
        migrations.DeleteModel(
            name='Directory',
        ),
        migrations.DeleteModel(
            name='File',
        ),
        migrations.DeleteModel(
            name='UserOAuth',
        ),
        migrations.DeleteModel(
            name='UserProfile',
        ),
    ]