from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

# Customer Model
class Customer(models.Model):
    customer_id = models.CharField(max_length=50, primary_key=True)  # CharField with primary key
    name = models.CharField(max_length=100)
    tax_id = models.CharField(max_length=20, unique=True)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)
    home_address = models.CharField(max_length=255)
    billing_address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return self.name

# Product Model
class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    model = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100)
    stock = models.IntegerField()
    inventory_to_stock = models.IntegerField()
    warranty_status = models.CharField(max_length=50)
    distributor_info = models.CharField(max_length=100)
    description = models.TextField(default="")
    category = models.TextField(default="")
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    discount = models.ForeignKey('Discount', on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    popularity_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

    def save(self, *args, **kwargs):
        if self.discount:
            self.price = self.base_price * (1 - self.discount.discount_rate)
        else:
            self.price = self.base_price
        super().save(*args, **kwargs)

    def update_popularity_score(self):
        sales_volume = self.get_sales_volume()
        average_rating = self.get_average_rating()
        wishlist_additions = self.get_wishlist_additions()
        w1, w2, w3 = 0.5, 0.3, 0.2
        self.popularity_score = (w1 * sales_volume) + (w2 * average_rating) + (w3 * wishlist_additions)
        self.save()

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

# Order Model
class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    order_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_applied = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=50)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

class OrderItem(models.Model):
    order_item_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2)

# ShoppingCart Model
class ShoppingCart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

class CartItem(models.Model):
    cart_item_id = models.AutoField(primary_key=True)
    cart = models.ForeignKey(ShoppingCart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

# Invoice Model
class Invoice(models.Model):
    invoice_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    invoice_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

# Delivery Model
class Delivery(models.Model):
    delivery_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    delivery_status = models.CharField(max_length=50)
    delivery_address = models.CharField(max_length=255)
    delivery_date = models.DateField()

# SalesManager Model
class SalesManager(models.Model):
    manager_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    phone_number = models.CharField(max_length=15)

# ProductManager Model
class ProductManager(models.Model):
    manager_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    phone_number = models.CharField(max_length=15)

# Discount Model (without direct reference to Product)
class Discount(models.Model):
    id = models.AutoField(primary_key=True)  # Explicit primary key
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='discounts')
    discount_name = models.CharField(max_length=100)
    discount_rate = models.DecimalField(max_digits=4, decimal_places=2)
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

# Refund Model
class Refund(models.Model):
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

    def __str__(self):
        return f"Refund {self.refund_id} for Order Item {self.order_item.order_item_id}"
