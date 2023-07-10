# Generated by Django 4.2 on 2023-05-15 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_remove_product_brand_remove_product_brand_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('brand_name', models.CharField(max_length=150, null=True)),
                ('brand_image', models.ImageField(null=True, upload_to='photos/brands')),
                ('created_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
