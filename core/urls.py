from django.urls import include, path
from core.views import category_list_view, update_cart , category_product_list_view,delete_item_from_cart, index, product_detail_view, product_list_view, tag_list, vendor_detail_view, vendor_list_view,  search_view, add_to_cart,filter_product
from core import views
from .views import ajax_add_review, cart_view, checkout_view, customer_dashboard, make_default_address, order_detail, payment_completed_view, payment_failed_view, search_view
app_name = "core"

urlpatterns = [
    path("", index, name="index"),
    path("products/", product_list_view, name="product-list"),
    path("product/<pid>/", product_detail_view, name="product-detail"),
    
    #category
    path("category/", category_list_view, name="category-list"),
    path("category/<cid>/", category_product_list_view, name="category_product_list_view"),
    
    #vendor
    path("vendors/", vendor_list_view, name="vendor_list_view"),
    path("vendors/<vid>/", vendor_detail_view, name="vendor_detail"),
    
    
    #Tags
    path("products/tag/<slug:tag_slug>/",tag_list, name="tags" ),
    
    path('ajax-add-review/<int:pid>/', ajax_add_review, name='ajax-add-review'),
    
    #search
    path("search/", search_view, name="search"),
    
    #filter
    
    path("filter-products/", filter_product, name="filter-product"),
    
    #add to cart
    
    path("add-to-cart/", add_to_cart, name="add-to-cart"),
    
    #cart view
    path("cart/", cart_view, name="cart"),
    
    #delete item from cart
    path("delete-from-cart/", delete_item_from_cart, name="delete-from-cart"),
    
     #update item from cart
    path("update-cart/", update_cart, name="update-cart"),
    
    #checkout
    path("checkout/", checkout_view, name="checkout" ),
    
    #paypal url
    path('paypal/', include('paypal.standard.ipn.urls')),
    
     #paypal payment successful
    path("payment-completed/", payment_completed_view, name="payment-completed" ),
    
    
     #paypal payment failed
    path("payment-failed/", payment_failed_view, name="payment-failed" ),
    
    
    path("payment-failed/", payment_failed_view, name="payment-failed" ),
    
    path("dashboard/", customer_dashboard, name="dashboard"),
    
    #dashboard details
   path("dashboard/detail/<int:id>/", order_detail, name="order-detail"),
   
   #make default
   path("make-default-address/" , make_default_address, name="make-default-address"),
    
   

]