# Generated by Django 5.1.6 on 2025-02-21 12:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_followrequest'),
    ]

    operations = [
        migrations.DeleteModel(
            name='FollowRequest',
        ),
    ]
