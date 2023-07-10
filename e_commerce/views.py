from django.shortcuts import render
from store.models import Product, ReviewRating
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

def home(request):
    products = Product.objects.all().filter(is_available=True).order_by('created_date')
    
    paginator = Paginator(products, 4)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    for product in products:
        reviews = ReviewRating.objects.filter(product_id=product.id, status=True)

    context = {
        'products':products,
        'reviews':reviews,
    }

    return render(request,'home.html',context)


