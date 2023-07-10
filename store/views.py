from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Brand, ReviewRating, ProductGallery, ProductDetail, ProductSpec
from accounts.models import Userprofile
from category.models import Category
from carts.models import Cart, CartItem
from django.db.models import Q
from carts.views import _cart_id
from django.http import HttpResponse
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from .forms import ReviewForm
from django.contrib import messages
from orders.models import OrderProduct
# Create your views here.

def store(request, category_slug=None, brand_slug=None):
    categories = None
    products = None
    brands = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()

    if brand_slug != None:
        brands = get_object_or_404(Brand, slug=brand_slug)
        products = Product.objects.filter(brand=brands)
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()

    context = {
        'title':'สินค้า',
        'products':paged_products,
        'product_count':product_count,
        
    }
    return render(request, 'store/store.html', context)

def product_detail(request, category_slug, product_slug):
    
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e
    
    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None

    # รับรีวิว
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)
    userprofile = Userprofile.objects.filter(user_id=request.user.id)
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)
    product_details = ProductDetail.objects.filter(product_id=single_product.id)
    product_specs = ProductSpec.objects.filter(product_id=single_product.id)
    product_recommen = Product.objects.filter(is_available=True).order_by('brand')

    paginator = Paginator(product_recommen, 4)
    page = request.GET.get('page')
    try:
        product_recommen = paginator.page(page)
    except PageNotAnInteger:
        product_recommen = paginator.page(1)
    except EmptyPage:
        product_recommen = paginator.page(paginator.num_pages)

    context = {
        'single_product':single_product,
        'in_cart':in_cart,
        'orderproduct':orderproduct,
        'reviews':reviews,
        'product_gallery':product_gallery,
        'product_details':product_details,
        'product_specs':product_specs,
        'userprofile':userprofile,
        'product_recommen':product_recommen,
    }

    return render(request, 'store/product_detail.html', context)

def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(pd_description__icontains=keyword) | Q(pd_name__icontains=keyword))
            product_count = products.count()
    context = {
        'title':'ค้นหา',
        'products':products,
        'product_count':product_count,
    }
    return render(request, 'store/store.html', context)
        
def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'รีวิวของคุณได้รับการอัปเดตแล้ว')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'รีวิวของคุณถูกส่งแล้ว')
                return redirect(url)