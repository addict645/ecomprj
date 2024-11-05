from core.models import (
    Product,
    Category,
    Vendor,
    CartOrder,
    CartOrderItems,
    ProductImages,
    ProductReview,
    Wishlist,
    Address,
)
from django.db.models import Min, Max
def default(request):
    Categories = Category.objects.all()
    vendors = Vendor.objects.all()
    
    min_max_price = Product.objects.aggregate(Min("price"), Max("price"))
    
    address = Address.objects.filter(user=request.user) if request.user.is_authenticated else None

    return {
        "categories": Categories,
        "address": address,
        "vendor": vendors,
        "min_max_price": min_max_price,
    }

