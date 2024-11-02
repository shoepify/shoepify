from django.db import models

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)  # AutoField for auto-increment
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)
    home_address = models.CharField(max_length=255)
    billing_address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return self.name

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    model = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100)
    stock = models.IntegerField()
    inventory_to_stock = models.IntegerField()
    warranty_status = models.CharField(max_length=50)
    distributor_info = models.CharField(max_length=100)

class Wishlist(models.Model):
    wishlist_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

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

class ShoppingCart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

class CartItem(models.Model):
    cart_item_id = models.AutoField(primary_key=True)
    cart = models.ForeignKey(ShoppingCart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

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
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    discount_name = models.CharField(max_length=100)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
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
