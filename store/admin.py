from django.contrib import admin
from .models import Product, Variation, Brand, ReviewRating, ProductGallery, ProductDetail, ProductSpec
import admin_thumbnails

# Register your models here.
@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1

class ProductDetailInline(admin.TabularInline):
    model = ProductDetail
    extra = 1

class ProductSpecInline(admin.TabularInline):
    model = ProductSpec
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ('pd_name', 'pd_price', 'pd_stock', 'category', 'created_date', 'modified_date')
    prepopulated_fields = {'slug': ('pd_name',)}
    inlines = [ProductGalleryInline, ProductDetailInline, ProductSpecInline]

class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active')
    # list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value')

class BrandAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('brand_name',)}
    list_display = ('brand_name', 'created_date', 'slug')

admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(Brand,BrandAdmin)
admin.site.register(ReviewRating)
admin.site.register(ProductGallery)
admin.site.register(ProductDetail)
admin.site.register(ProductSpec)