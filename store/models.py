from django.db import models
from category.models import Category
from accounts.models import Account
from django.urls import reverse
from django.db.models import Avg, Count
# Create your models here.

class Brand(models.Model):
    brand_name = models.CharField(max_length=150, null=True)
    slug = models.SlugField(max_length=150, unique=True, null=True)
    brand_image = models.ImageField(upload_to='photos/brands', null=True)
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'brand'
        verbose_name_plural = 'brands'

    def get_url(self):
            return reverse('products_by_brand', args=[self.slug])

    def __str__(self):
        return self.brand_name

class Product(models.Model):
    pd_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, null=True)
    pd_description = models.TextField(null=True, blank=True,)
    pd_price = models.IntegerField(null=True)
    pd_image = models.ImageField(upload_to='photos/products', null=True)
    pd_stock = models.IntegerField(null=True)
    is_available = models.BooleanField(default=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,null=True)
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    modified_date = models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.pd_name
    
    def averageReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg
    
    def countReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count

class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_category='color', is_active=True)

variation_category_choice = (
    ('color', 'color'),
)

class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100, choices=variation_category_choice)
    variation_value     = models.CharField(max_length=100)
    is_active           = models.BooleanField(default=True)
    created_date        = models.DateTimeField(auto_now=True)

    objects = VariationManager()

    def __str__(self):
        return self.variation_value
    
class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=150, blank=True)
    review = models.TextField(max_length=1000, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject

class ProductGallery(models.Model):
    product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='photos/products/', max_length=255)

    def __str__(self):
        return self.product.pd_name
    
    class Meta:
        verbose_name = 'productgallery'
        verbose_name = 'product gallery'

class ProductDetail(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    detail_line = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.product.pd_name
    
class ProductSpec(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    spec_line = models.CharField(max_length=100, blank=True)


    def __str__(self):
        return self.product.pd_name