from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from userauths.models import User 
from .validators import validate_image_size
from taggit.managers import TaggableManager
from ckeditor_uploader.fields import RichTextUploadingField

STATUS_CHOICE = (
    ("processing", "Processing"),
    ("shipped", "Shipped"),
    ("Derivered","Derivered")
)


STATUS = (
    ("draft", "Draft"),
    ("disabled", "Disabled"),
    ("rejected", "Rejected"),
    ("in_review", "In Review"),
    ("published", "Published"),
)



RATING = (
    (1,  "★☆☆☆☆"),
    (2,  "★★☆☆☆"),
    (3,  "★★★☆☆"),
    (4,  "★★★★☆"),
    (5,  "★★★★★"),
)




def user_directory_path(instance, filename):
    return "user_{0}/{1}".format(instance.user.id, filename)





class Category(models.Model):
    cid = ShortUUIDField(unique=True, length=10, prefix="cat", alphabet="abcdefgh123456")  
    title = models.CharField(max_length=100, default="Food")  
    image = models.ImageField(upload_to="category", default="category.jpg")  

    class Meta:
        verbose_name_plural = "Categories"
        
    def category_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))
    
    def __str__(self):
        return self.title
    
    
class Tag(models.Model):
    pass
    
class Vendor(models.Model):
    vid = ShortUUIDField(unique=True, length=10, prefix="ven", alphabet="abcdefgh12345")
    title = models.CharField(max_length=100, default="Nestify")  # Corrected maxl_length to max_length
    image = models.ImageField(upload_to=user_directory_path, default="Vendor.jpg")
    cover_image = models.ImageField(upload_to=user_directory_path, default="Vendor.jpg")
    description = RichTextUploadingField(null=True, blank=True, default="I am an amazing vendor")
    
    address = models.CharField(max_length=100, default="123 Main Street.")  # Corrected maxl_length to max_length
    contact = models.CharField(max_length=100, default="+123 (456) (789)")  # Corrected maxl_length to max_length
    chat_resp_time = models.CharField(max_length=100, default="100")  # Corrected maxl_length to max_length
    shipping_on_time = models.CharField(max_length=100, default="100")  # Corrected maxl_length to max_length
    authentic_rating = models.CharField(max_length=100, default="100")  # Corrected maxl_length to max_length
    days_return = models.CharField(max_length=100, default="100")  # Corrected maxl_length to max_length
    warranty_period = models.CharField(max_length=100, default="100")  # Corrected maxl_length to max_length
    
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name_plural = "Vendors"
    
    def vendor_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def __str__(self):
        return self.title

    
class Product(models.Model):  # Class name should be capitalized
    
    pid = ShortUUIDField(unique=True, length=10, alphabet="abcdefgh12345")  # Removed max_length
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, related_name="category")
    vendor = models.ForeignKey('Vendor', on_delete=models.SET_NULL, null=True, related_name="product")
    
    title = models.CharField(max_length=100, default="Fresh Pear")  # Corrected maxl_length to max_length
    image = models.ImageField(upload_to=user_directory_path, default="Product.jpg", validators=[validate_image_size])
    description = RichTextUploadingField(null=True, blank=True, default="This is the product")
    
    price = models.DecimalField(max_digits=20, decimal_places=2, default=0.99)  # Adjusted max_digits for practical use
    old_price = models.DecimalField(max_digits=20, decimal_places=2, default=1.99)  # Adjusted max_digits
    specifications = RichTextUploadingField(null=True, blank=True)
    type = models.CharField(max_length=100, )
    
    
    
    #tags = models.ManyToManyField('Tag', blank=True)  # Changed to ManyToManyField for tags if it references a Tag model
    tags = TaggableManager(blank=True,)
    
    product_status = models.CharField(choices=STATUS, max_length=10, default="in_review")
    
    status = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    digital = models.BooleanField(default=False)
    
    sku = ShortUUIDField(unique=True, length=4, prefix="sku", alphabet="1234567890")  # Removed max_length
    
    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "Products"
    
    def product_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))

    def __str__(self):
        return self.title
    
    def get_percentage(self):
        new_price = (self.price / self.old_price) * 100
        return new_price
    
    
class ProductImages(models.Model):
    image = models.ImageField(upload_to="product-images",default="product.jpg", validators=[validate_image_size])
    product = models.ForeignKey(Product,related_name="p_images", on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)
    product_status =models.CharField(choices=STATUS, max_length=10, default="in_review")
    
    class Meta:
        verbose_name_plural = "Product_Images"
    
####Cart, Order, OrderItems  ###########
####Cart, Order, OrderItems ###########
####Cart, Order, OrderItems ###########


    

class CartOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, default="0.99")
    paid_status = models.BooleanField(default=False)  
    order_date = models.DateTimeField(auto_now_add=True)
    product_status = models.CharField(choices=STATUS_CHOICE, max_length=30, default="processing")

    
    class Meta:
        verbose_name_plural = "Cart Orders"

class CartOrderItems(models.Model):
    order = models.ForeignKey(CartOrder, on_delete=models.CASCADE)
    invoice_no = models.CharField(max_length=200)
    product_status = models.CharField(max_length=200)
    item = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    qty = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default="0.99")
    total = models.DecimalField(max_digits=10, decimal_places=2, default="0.99")

    
    class Meta:
        verbose_name_plural = "Cart Order Items"
        
    def product_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))
        
    def order_img(self):
        return mark_safe ('<img src ="/media/%s" width="50" height="50" />' % (self.image))
    
    
    
### Product review, wishlists, address  ###########
### Product review, wishlists, address  ###########
### Product review, wishlists, address  ###########

        
        
class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, related_name="reviews")
    review = models.TextField()
    rating = models.IntegerField(choices=RATING, default=None)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Product Reviews"

    def __str__(self):
        return self.product.title

    def get_rating(self):
        return self.rating



        
        
        
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)
    
    
    class Meta:
        verbose_name_plural = "Wishlists"
    

    def __str__(self):
        return self.product.title
    
   
   
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=100)
    mobile_no = models.CharField(max_length=20, default="none")
    date = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)
    
    
    class Meta:
        verbose_name_plural = "Address"
        
        




        
        
        
        
    
        
        
        
        
 
    
    
