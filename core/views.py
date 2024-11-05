from itertools import product
from multiprocessing import context
from django.db.models import Avg  # Make sure to import Avg
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from taggit.models import Tag
from .forms import ProductReviewForm
from django.template.loader import render_to_string
from .models import Product
from django.contrib import messages
from decimal import Decimal
from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm
from django.contrib.auth.decorators import login_required
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

def index(request):
    products = Product.objects.filter(product_status='published', featured=True).order_by("-id")
    
    context = {
        "products": products
    }
    return render(request, 'core/index.html', context)

def product_list_view(request):
    # Fetch products along with their vendor data
    products = Product.objects.filter(product_status='published').select_related('vendor').order_by("-id")
    
    context = {
        "products": products,
    }
    return render(request, 'core/product-list.html', context)


def category_list_view(request):
    categories = Category.objects.all()  # Corrected here
        
    context = {
        "categories": categories
    }
    return render(request, 'core/category-list.html', context)


def category_product_list_view(request, cid):
    category = Category.objects.get(cid=cid)
    products = Product.objects.filter(product_status="published", category=category)
    
    context = {
        "category":category,
        "products":products,
    }
    return render(request, "core/category-product-list.html", context)

def vendor_list_view(request):
    vendors = Vendor.objects.all()
    context = {
            "vendors":vendors,
        }
    
    return render(request, "core/vendor-list.html", context) 

def vendor_detail_view(request, vid):
    vendor = Vendor.objects.get(vid=vid)
    products = Product.objects.filter(product_status="published", vendor=vendor)
    context = {
            "vendor":vendor,
            "products":products,
        }
    
    return render(request, "core/vendor-detail.html", context) 


def product_detail_view(request, pid):
    # Fetch the product or return a 404 if it doesn't exist
    product = get_object_or_404(Product, pid=pid)
    products = Product.objects.filter(category=product.category).exclude(pid=pid)
    
    
    # Getting all reviews related to a product
    reviews = ProductReview.objects.filter(product=product).order_by("-date")
    
    
    # Getting average review
    average_rating = ProductReview.objects.filter(product=product).aggregate(rating=Avg('rating'))
    
     # Product Review form
    review_form = ProductReviewForm()
    
    make_review = request.user.is_authenticated
    
    make_review = True 

    if request.user.is_authenticated:
        address = Address.objects.get(status=True, user=request.user)
        user_review_count = ProductReview.objects.filter(user=request.user, product=product).count()

        if user_review_count > 0:
            make_review = False
    
    address = "Login To Continue"

    
    p_images = product.p_images.all()
    
    context = {
        "p": product,
        "p_images": p_images,
        "products": products,
        "reviews": reviews,
        "average_rating": average_rating,
        'review_form': review_form,
        'make_review': True,
    }
    return render(request, "core/product_detail.html", context)

def tag_list(request, tag_slug=None):
    # Fetch all products with 'published' status and order by descending 'id'
    products = Product.objects.filter(product_status="published").order_by('-id')
    
    tag = None
    if tag_slug:
        # Fetch the tag by slug, or return 404 if not found
        tag = get_object_or_404(Tag, slug=tag_slug)
        # Filter products by the selected tag
        products = products.filter(tags__in=[tag])
        
    # Context to pass to the template
    context = {
        "products": products,
        "tag": tag,
    }
    
    # Render the template with the filtered products
    return render(request, "core/tag.html", context)

def ajax_add_review(request, pid):
    if request.method == "POST":
        product_instance = Product.objects.get(id=pid)
        user = request.user

        # Safely get review and rating data from the POST request
        review = request.POST.get('review', None)
        rating = request.POST.get('rating', None)

        if review and rating:
            review_instance = ProductReview.objects.create(
                user=user,
                product=product_instance,
                review=review,
                rating=rating,
            )

            context = {
                'user': user.username,
                'review': review,
                'rating': rating,
            }

            average_reviews = ProductReview.objects.filter(product=product_instance).aggregate(rating=Avg("rating"))

            return JsonResponse({
                'bool': True,
                'context': context,
                'average_reviews': average_reviews
            })

        return JsonResponse({'bool': False, 'error': 'Review or rating missing'})

    return JsonResponse({'bool': False, 'error': 'Invalid request method'})

def search_view(request):
    query = request.GET.get("q", "")  # Default to an empty string if 'q' is not in GET parameters
     
    # Check if query exists; if not, return an empty queryset
    if query:
        products = Product.objects.filter(title__icontains=query).order_by("-date")
    else:
        products = Product.objects.none()  # or Product.objects.all() if you want to display all products

    context = {
        "products": products,
        "query": query,
    }

    return render(request, "core/search.html", context)

def filter_product(request):
    categories = request.GET.getlist('category[]')
    vendors = request.GET.getlist('vendor[]')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    # Start with all published products
    products = Product.objects.filter(product_status="published").order_by("-id").distinct()

    # Filter by categories if provided
    if categories:
        products = products.filter(category__id__in=categories)

    # Filter by vendors if provided
    if vendors:
        products = products.filter(vendor__id__in=vendors)

    # Filter by price range if both min_price and max_price are provided
    if min_price and max_price:
        products = products.filter(price__gte=min_price, price__lte=max_price)

    # Render the filtered products to the HTML template
    data = render_to_string("core/async/product-list.html", {"products": products})
    return JsonResponse({"data": data})



def add_to_cart(request):
    if request.method == 'GET':
        cart_product = {}
        
        # Use request.GET instead of request.Get
        cart_product[str(request.GET['id'])] = {
            'title': request.GET['title'],
            'qty': request.GET['qty'],
            'price': request.GET['price'],
            'image': request.GET['image'],  # Corrected here
            'pid': request.GET['pid'],       # Corrected here
        }
        
        # Check if 'cart_data_obj' exists in the session
        if 'cart_data_obj' in request.session:
            cart_data = request.session['cart_data_obj']
            
            if str(request.GET['id']) in cart_data:
                # Update quantity if product already in cart
                cart_data[str(request.GET['id'])]['qty'] += int(cart_product[str(request.GET['id'])]['qty'])
            else:
                # Add new product to cart
                cart_data.update(cart_product)
                
            request.session['cart_data_obj'] = cart_data
        else:
            # Initialize cart if it doesn't exist
            request.session['cart_data_obj'] = cart_product
        
        return JsonResponse({
            "data": request.session['cart_data_obj'],
            'totalcartitems': len(request.session['cart_data_obj'])
        })
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    
    
    
def cart_view(request):
    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            qty = int(item['qty'])
            price = float(item['price'])
            print(f"Item ID: {p_id}, Qty: {qty}, Price: {price}, Subtotal: {qty * price}")  # Debugging line
            cart_total_amount += qty * price
        print(f"Total Cart Amount: {cart_total_amount}")  # Debugging line
        return render(request, "core/cart.html", {
            "cart_data": request.session['cart_data_obj'],
            'totalcartitems': len(request.session['cart_data_obj']),
            'cart_total_amount': cart_total_amount
        })
    else:
        messages.warning(request, 'Your cart is empty')
        return render(request, "core/index.html")

    
def delete_item_from_cart(request):
    product_id = str(request.GET['id'])  # Corrected 'Get' to 'GET'
    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            del cart_data[product_id]  # Simplified deletion
            request.session['cart_data_obj'] = cart_data
        
    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])
            
    context = render_to_string("core/async/cart-list.html", {
        "cart_data": request.session['cart_data_obj'],
        'totalcartitems': len(request.session['cart_data_obj']),
        'cart_total_amount': cart_total_amount
    })
    return JsonResponse({
        "data": context,
        'totalcartitems': len(request.session['cart_data_obj']),
        'cart_total_amount': cart_total_amount
    })



def update_cart(request):
    product_id = str(request.GET['id'])  # Changed from request.Get to request.GET
    product_qty = request.GET['qty']     # Changed from request.Get to request.GET
    if 'cart_data_obj' in request.session:
        if product_id in request.session['cart_data_obj']:
            cart_data = request.session['cart_data_obj']
            cart_data[product_id]['qty'] = product_qty  # Correct usage of product_id
            request.session['cart_data_obj'] = cart_data

    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])

    context = render_to_string("core/async/cart-list.html", {
        "cart_data": request.session['cart_data_obj'],
        'totalcartitems': len(request.session['cart_data_obj']),
        'cart_total_amount': cart_total_amount
    })
    return JsonResponse({
        "data": context,
        'totalcartitems': len(request.session['cart_data_obj']),
        'cart_total_amount': cart_total_amount
    })



@login_required
def checkout_view(request):
    cart_total_amount = 0
    total_amount = 0
    cart_amount = 0  # Initialize cart_amount here

    # Checking if cart_data_obj session exists
    if 'cart_data_obj' in request.session:
        # Getting total amount for PayPal
        for p_id, item in request.session['cart_data_obj'].items():
            total_amount += int(item['qty']) * float(item['price'])

        # Creating order object   
        order = CartOrder.objects.create(
            user=request.user,
            price=total_amount
        )

        # Getting total amount for the cart and creating CartOrderItems
        for p_id, item in request.session['cart_data_obj'].items():
            cart_amount += int(item['qty']) * float(item['price'])

            # Creating order items
            cart_order_items = CartOrderItems.objects.create(
                order=order,
                invoice_no="INVOICE_NO-" + str(order.id),
                item=item['title'],
                image=item['image'],
                qty=item['qty'],
                price=item['price'],
                total=float(item['qty']) * float(item['price']),
            )
            
        # Update cart_total_amount to reflect the actual cart total
        cart_total_amount = cart_amount

        # PayPal parameters
        host = request.get_host()
        paypal_dict = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': cart_total_amount,  # This now reflects the actual cart total
            'item_name': "Order-Item-No-" + str(order.id),
            'invoice': "INVOICE-NO-" + str(order.id),
            'currency_code': 'USD',
            'notify_url': 'http://{}{}'.format(host, reverse('core:paypal-ipn')),
            'return_url': 'http://{}{}'.format(host, reverse('core:payment-completed')),
            'cancel_return': 'http://{}{}'.format(host, reverse('core:payment-failed')),
        }

        # Initialize PayPalPaymentsForm
        paypal_payment_button = PayPalPaymentsForm(initial=paypal_dict)
        
        try:
            active_address = Address.objects.get(user=request.user, status=True)
        except:
            messages.warning(request, "There are multiple addresses, Only one should be activated")
            active_address =None

        # Render checkout template with the necessary context
        return render(request, "core/checkout.html", {
            "cart_data": request.session['cart_data_obj'],
            'totalcartitems': len(request.session['cart_data_obj']),
            'cart_total_amount': cart_total_amount,
            'paypal_payment_button': paypal_payment_button,
            'active_address':active_address,
        })

    else:
        # Optional: Handle empty cart case
        messages.warning(request, 'Your cart is empty')
        return render(request, "core/index.html")


def payment_completed_view(request):
    cart_total_amount = 0

    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])
        
        return render(request, 'core/payment-completed.html', {
            'cart_data': request.session['cart_data_obj'],
            'totalcartitems': len(request.session['cart_data_obj']),
            'cart_total_amount': cart_total_amount
        })
    else:
        # Redirect to a relevant page if the cart is empty
        messages.warning(request, "No items in the cart.")
        return redirect('core:index')  # Redirect to the home page or another page

def payment_failed_view(request):
     return render(request, 'core/payment-failed.html',)


@login_required
def customer_dashboard(request):
    orders = CartOrder.objects.filter(user=request.user).order_by("-id")
    address = Address.objects.filter(user=request.user)
    
    if request.method == "POST":
        address = request.POST.get("address")
        mobile_no = request.POST.get("mobile_no")
        
        new_address = Address.objects.create(
            user=request.user,
            address = address,
            mobile_no = mobile_no,
        )
        messages.success(request, "Address Added Successfuly")
        return redirect("/dashboard")
    
    context = {
        "orders": orders,
        'address':address,
        
    }
    return render(request, 'core/dashboard.html', context)

def order_detail(request, id):
    order = CartOrder.objects.get(user=request.user, id=id)
    order_items = CartOrderItems.objects.filter(order=order)
    
    context = {
        'order_items': order_items,  # Corrected context key
        'order':order,
        
    }
    return render(request, 'core/order-detail.html', context)


def make_default_address(request):
    id = request.GET['id']
    Address.objects.update(status=False)
    Address.objects.filter(id=id).update(status=True)
    return JsonResponse({"boolean":True})
   


    
    
        




        
