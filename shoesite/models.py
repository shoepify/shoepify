from django.db import models
<<<<<<< HEAD

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
=======
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


class Customer(models.Model):
    customer_id = models.CharField(max_length=50, primary_key=True)  # Change to CharField and enforce uniqueness
    name = models.CharField(max_length=100)
    tax_id = models.CharField(max_length=20, unique=True)
>>>>>>> 2bfe36e365689b327fd756507b1d34be718c3dd4
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)
    home_address = models.CharField(max_length=255)
    billing_address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
<<<<<<< HEAD

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
=======
    

    def __str__(self):
        return self.name

class Product(models.Model):
    product_id = models.CharField(max_length = 50, primary_key=True)
>>>>>>> 2bfe36e365689b327fd756507b1d34be718c3dd4
    model = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100)
    stock = models.IntegerField()
    inventory_to_stock = models.IntegerField()
    warranty_status = models.CharField(max_length=50)
    distributor_info = models.CharField(max_length=100)
<<<<<<< HEAD

class Wishlist(models.Model):
    wishlist_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

class Order(models.Model):
=======
    description = models.TextField(default="")  # New description attribute (default = empty)
    category = models.TextField(default="")  # New category attribute (default = empty)

    # New size attribute
    #size = models.CharField(max_length=10)  # Adjust max_length as needed for shoe sizes
    base_price = models.DecimalField(max_digits=10, decimal_places=2) # new base price (without discount)
    price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)  # actual price with discount
    discount = models.ForeignKey('Discount', on_delete=models.SET_NULL, null=True, blank=True, related_name='products')  # ForeignKey to Discount

    def save(self, *args, **kwargs):
        # Calculate price based on discount, if any
        if self.discount:
            self.price = self.base_price * (1 - self.discount.discount_rate)
        else:
            self.price = self.base_price
        super().save(*args, **kwargs)

    
    
    # new attribute for popularity (for sorting)
    popularity_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

    def update_popularity_score(self):
        # assuming `sales_volume`, `average_rating`, `wishlist_additions` are dynamically calculated or available
        sales_volume = self.get_sales_volume()
        average_rating = self.get_average_rating()
        wishlist_additions = self.get_wishlist_additions()

        # weights for each metric 
        w1, w2, w3 = 0.5, 0.3, 0.2  # example weights (can change)
        
        # Calculate the score
        self.popularity_score = (w1 * sales_volume) + (w2 * average_rating) + (w3 * wishlist_additions)
        self.save()

    def get_sales_volume(self):
        # Calculate total sales from OrderItem
        return OrderItem.objects.filter(product=self).count()

    def get_average_rating(self):
        # Calculate average rating from Rating 
        ratings = Rating.objects.filter(product=self)
        if ratings.exists():
            return ratings.aggregate(models.Avg('rating_value'))['rating_value__avg']
        return 0

    def get_wishlist_additions(self):
        # Calculate number of times added to wishlists
        return WishlistItem.objects.filter(product=self).count()



class Wishlist(models.Model):
    wishlist_id = models.AutoField(primary_key=True)
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)  # customer has one wishlist
    #customer = models.ForeignKey(Customer, on_delete=models.CASCADE) # old customer FK

class WishlistItem(models.Model): # New  table (can be changed)
    wishlist_item_id = models.AutoField(primary_key=True)
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)




class Order(models.Model):  
>>>>>>> 2bfe36e365689b327fd756507b1d34be718c3dd4
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

class ShoppingCart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

class CartItem(models.Model):
    cart_item_id = models.AutoField(primary_key=True)
    cart = models.ForeignKey(ShoppingCart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
<<<<<<< HEAD
    quantity = models.IntegerField()
=======
    quantity = models.PositiveIntegerField(default=1) 
>>>>>>> 2bfe36e365689b327fd756507b1d34be718c3dd4

class Invoice(models.Model):
    invoice_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    invoice_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

class Delivery(models.Model):
    delivery_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    delivery_status = models.CharField(max_length=50)
    delivery_address = models.CharField(max_length=255)
    delivery_date = models.DateField()

class SalesManager(models.Model):
    manager_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    phone_number = models.CharField(max_length=15)

class ProductManager(models.Model):
    manager_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    phone_number = models.CharField(max_length=15)

class Discount(models.Model):
    discount_id = models.AutoField(primary_key=True)
<<<<<<< HEAD
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    discount_name = models.CharField(max_length=100)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
=======
    # NO need for product as foreign key since discount can be for many products
    #product = models.ForeignKey(Product, on_delete=models.CASCADE)
    discount_name = models.CharField(max_length=100)
    discount_rate = models.DecimalField(max_digits=4, decimal_places=2)
>>>>>>> 2bfe36e365689b327fd756507b1d34be718c3dd4
    start_date = models.DateField()
    end_date = models.DateField()

class Rating(models.Model):
    rating_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    rating_value = models.IntegerField()

class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    comment = models.TextField()
    approval_status = models.CharField(max_length=50)
<<<<<<< HEAD
=======

class Refund(models.Model): # new table for refund
    refund_id = models.AutoField(primary_key=True)
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    request_date = models.DateField(default=timezone.now)
    approval_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending')
    refunded_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def approve_refund(self):
        # Check if the refund is within 30 days of purchase
        if (timezone.now().date() - self.order_item.order.order_date).days <= 30:
            # Update status and approval date
            self.status = 'Approved'
            self.approval_date = timezone.now().date()
            
            # Calculate refunded amount:  price at time of purchase  x quantity (both attributes from OrderItem)
            self.refunded_amount = self.order_item.price_per_item * self.order_item.quantity
            
            # add refunded product back to stock according to its quantity
            self.order_item.product.stock += self.order_item.quantity
            self.order_item.product.save()
            
            # Save the refund record with calculated amount
            self.save()
        else:
            self.status = 'Rejected'
            self.save()
            
    def __str__(self):
        return f"Refund {self.refund_id} for Order Item {self.order_item.order_item_id}"
>>>>>>> 2bfe36e365689b327fd756507b1d34be718c3dd4
