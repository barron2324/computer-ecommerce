# Generated by Django 4.2 on 2023-05-21 12:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_contactlist_action'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Action',
            new_name='ActionContact',
        ),
    ]