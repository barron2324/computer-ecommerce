# Generated by Django 4.2 on 2023-05-10 21:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0003_remove_cartitem_variations'),
        ('store', '0005_alter_variation_managers'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Variation',
        ),
    ]