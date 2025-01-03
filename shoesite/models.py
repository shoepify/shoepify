from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP
from django.core.exceptions import ValidationError

# Customer Model
class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)  
    name = models.CharField(max_length=100)
    tax_id = models.CharField(max_length=50, unique=True)  # Now a required field
    email = models.EmailField(max_length=100, unique = True) # now email is supposed to be unique
    password = models.CharField(max_length=100)
    home_address = models.CharField(max_length=255)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    # Override the default 'id' to refer to 'customer_id'
    id = property(lambda self: self.customer_id)

    
    def __str__(self):
        return self.name


# SalesManager Model
class SalesManager(models.Model):
    manager_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    #phone_number = models.CharField(max_length=15)
    password = models.CharField(max_length=100)
    id = property(lambda self: self.manager_id)

    def __str__(self):
        return self.name
    

# ProductManager Model
class ProductManager(models.Model):
    manager_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    #phone_number = models.CharField(max_length=15)
    password = models.CharField(max_length=100)
    id = property(lambda self: self.manager_id)

    def __str__(self):
        return self.name

# Guest User Model
class Guest(models.Model):
    guest_id = models.AutoField(primary_key=True)
    session_id = models.CharField(max_length=255, unique=True)  # To identify the guest uniquely
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Guest {self.guest_id}"

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(default='No description available')

    def clean(self):
        if self.products.exists():
            raise ValidationError(f"Cannot delete category '{self.name}' as it still has associated products.")

    def delete(self, *args, **kwargs):
        if self.products.exists():
            raise ValidationError(f"Cannot delete category '{self.name}' as it still has associated products.")
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.name

# Product Model
class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    model = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100)
    stock = models.IntegerField()
    warranty_status = models.CharField(max_length=50)
    distributor_info = models.CharField(max_length=100)
    description = models.TextField(default='No description available')
    category = models.ForeignKey('Category', on_delete=models.PROTECT, related_name='products', null=True, blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  # New cost column
    profit = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, editable=False)  # Add profit field
    discount = models.ForeignKey('Discount', on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    popularity_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    avg_rating = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    image_name = models.CharField(max_length=255, blank=True, null=True)  # Store the image name

    def save(self, *args, **kwargs):
        if self.discount:
            # Ensure both operands are Decimal
            discount_rate = Decimal(self.discount.discount_rate)
            # Calculate price and round it to 2 decimal places to match field precision
            self.price = (self.base_price * (Decimal('1') - discount_rate)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        else:
            self.price = self.base_price

        # Automatically calculate the profit
        self.profit = self.price - self.cost

        super().save(*args, **kwargs)
        self.update_avg_rating()
        super().save(update_fields=['avg_rating'])

    def update_avg_rating(self):
        """
        Calculate and update the average rating for the product.
        """
        ratings = self.rating_set.all()  # Fetch all related ratings
        if ratings.exists():
            avg_rating = ratings.aggregate(models.Avg('rating_value'))['rating_value__avg']
            self.avg_rating = round(avg_rating, 2)
        else:
            self.avg_rating = 0.0

    def update_popularity_score(self):
        """
        Calculate and update the popularity score for the product.
        Example formula combines ratings, orders, and wishlist additions.
        """
        # Count order items
        order_items_count = self.orderitem_set.count()

        # Count ratings and calculate the average rating
        ratings_count = self.rating_set.count()
        average_rating = self.rating_set.aggregate(models.Avg('rating_value'))['rating_value__avg'] or 0

        # Count wishlist additions
        wishlist_count = self.wishlistitem_set.count()

        # Calculate popularity score
        self.popularity_score = (
            (order_items_count * 0.4) +
            (ratings_count * average_rating * 0.4) +
            (wishlist_count * 0.2)
        )

        # Save the updated popularity score
        self.save()

        @property
        def profit(self):
            """
            Calculate the profit as the difference between price and cost.
            """
            return self.price - self.cost if self.price and self.cost else None

        def get_sales_volume(self):
            return OrderItem.objects.filter(product=self).count()

        def get_average_rating(self):
            ratings = Rating.objects.filter(product=self)
            return ratings.aggregate(models.Avg('rating_value'))['rating_value__avg'] if ratings.exists() else 0

        def get_wishlist_additions(self):
            return WishlistItem.objects.filter(product=self).count()


# Wishlist Model
class Wishlist(models.Model):
    wishlist_id = models.AutoField(primary_key=True)
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)

class WishlistItem(models.Model):
    wishlist_item_id = models.AutoField(primary_key=True)
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


class Order(models.Model):  

    order_id = models.AutoField(primary_key=True)
    order_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_applied = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=50)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[('Processing', 'Processing'),
                            ('In-Transit', 'In-Transit'),
                            ('Delivered', 'Delivered'),
                            ('Cancelled', 'Cancelled')],
                            null=True,  # Allow null values
                            blank=True,  # Allow blank values in forms
                            default="NULL"  # Set default to None (interpreted as NULL in the database)
                            )
    #created_at = models.DateTimeField(auto_now_add=True)
    #id = property(lambda self: self.order_id)

    

class OrderItem(models.Model):
    order_item_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2)
    refunded = models.BooleanField(default=False)



# ShoppingCart Model
class ShoppingCart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    #customer = models.OneToOneField(Customer, on_delete=models.CASCADE)

    # owner of shopping cart is Customer or Guest
    owner_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    owner_object_id = models.PositiveIntegerField()
    owner = GenericForeignKey('owner_content_type', 'owner_object_id')

class CartItem(models.Model):
    cart_item_id = models.AutoField(primary_key=True)
    cart = models.ForeignKey(ShoppingCart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.model} (Cart: {self.cart.cart_id})"

class Invoice(models.Model):
    invoice_id = models.AutoField(primary_key=True)
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    invoice_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return f"Invoice for Order #{self.order.id}"


    
# Delivery Model
class Delivery(models.Model):
    delivery_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    delivery_status = models.CharField(max_length=50)
    delivery_address = models.CharField(max_length=255)
    delivery_date = models.DateField()

# Discount Model (without direct reference to Product)
class Discount(models.Model):
    discount_id = models.AutoField(primary_key=True)
    # NO need for product as foreign key since discount can be for many products
    #product = models.ForeignKey(Product, on_delete=models.CASCADE)
    discount_name = models.CharField(max_length=100)
    discount_rate = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    start_date = models.DateField()
    end_date = models.DateField()

# Rating Model
class Rating(models.Model):
    rating_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    rating_value = models.IntegerField()

# Comment Model
class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    comment = models.TextField()
    approval_status = models.CharField(max_length=50)
    id = property(lambda self: self.comment_id)


# Refund Model
class Refund(models.Model):
    refund_id = models.AutoField(primary_key=True)
    order_item = models.OneToOneField(OrderItem, on_delete=models.CASCADE)  # One refund per order item
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')],
        default='Pending'
    )
    refunded_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # ID property
    id = property(lambda self: self.refund_id)
    
    def __str__(self):
        return f"Refund {self.refund_id} for Order Item {self.order_item.order_item_id}"

'''
class Refund(models.Model): # new table for refund

    refund_id = models.AutoField(primary_key=True)
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    request_date = models.DateField(default=timezone.now)
    approval_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending')
    refunded_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def approve_refund(self):
        if (timezone.now().date() - self.order_item.order.order_date).days <= 30:
            self.status = 'Approved'
            self.approval_date = timezone.now().date()
            self.refunded_amount = self.order_item.price_per_item * self.order_item.quantity
            self.order_item.product.stock += self.order_item.quantity
            self.order_item.product.save()
            self.save()
        else:
            self.status = 'Rejected'
            self.save()
'''