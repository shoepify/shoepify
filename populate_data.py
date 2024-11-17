import os
import django
from random import randint, choice, uniform
from decimal import Decimal
from datetime import datetime, timedelta

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shoesite.settings")
django.setup()

# Import your models
from shoesite.models import (
    Customer, Product, Wishlist, WishlistItem, Order, OrderItem, 
    ShoppingCart, CartItem, Invoice, Delivery, SalesManager, 
    ProductManager, Discount, Rating, Comment, Refund
)

# Function to create dummy data
def create_dummy_data():
    # Create Customers
    customers = []
    for i in range(10):
        customer = Customer.objects.create(
            name=f"Customer {i+1}",
            tax_id=f"TAX{i+1:05}",  # Ensures a unique tax ID for each customer
            email=f"customer{i+1}@example.com",
            password="password123",
            home_address=f"Home Address {i+1}",
            billing_address=f"Billing Address {i+1}",
            phone_number=f"+12345678{i+1:02}"
        )
        customers.append(customer)

    # Create Products
    products = []
    for i in range(20):
        base_price = Decimal(str(round(uniform(10, 9999.99), 2)))  # Ensure values fit the constraints
        price = Decimal(str(round(uniform(10, 9999.99), 2)))
        product = Product.objects.create(
            model=f"Model {i+1}",
            serial_number=f"SN{i+1:05}",
            stock=randint(10, 100),
            inventory_to_stock=randint(5, 50),
            warranty_status=choice(['Valid', 'Expired']),
            distributor_info=f"Distributor {i+1}",
            description=f"Description for Product {i+1}",
            category=choice(['Category A', 'Category B', 'Category C']),
            base_price=base_price,
            price=price,
            popularity_score=Decimal(str(round(uniform(0, 5), 2))),
            avg_rating=Decimal(str(round(uniform(0, 5), 2)))
        )
        products.append(product)

    # Continue populating the rest of your data...
    # (The rest of your code remains unchanged)

    print("Dummy data successfully created!")

# Run the function
create_dummy_data()
