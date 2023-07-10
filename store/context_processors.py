from .models import Brand

def brand_links(request):
    brand = Brand.objects.all()

    return dict(brand=brand)