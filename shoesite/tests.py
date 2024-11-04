from django.test import TestCase
from django.urls import reverse
import json
from rest_framework import status
from .models import Customer, Product, Wishlist, WishlistItem, ShoppingCart, CartItem

# customer 
class CustomerModelTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            customer_id="CUST001",
            name="John Doe",
            tax_id="TAX12345",
            email="john@example.com",
            password="password123",
            home_address="123 Main St",
            billing_address="123 Main St",
            phone_number="555-1234"
        )

    def tearDown(self):
        # Clean up the customer instance after each test
        self.customer.delete()

    def test_customer_creation(self):
        self.assertEqual(self.customer.name, "John Doe")
        self.assertEqual(self.customer.tax_id, "TAX12345")
        self.assertEqual(self.customer.email, "john@example.com")



class ProductAPITests(TestCase):
    def setUp(self):
        # Create a sample product for testing
        self.product_data = {
            'product_id': 'P001',
            'model': 'Model X',
            'serial_number': 'SN12345',
            'stock': 10,
            'inventory_to_stock': 5,
            'warranty_status': '1 year',
            'distributor_info': 'Distributor ABC',
            'description': 'A great product',
            'category': 'Shoes',
            'base_price': 99.99
        }
        self.client.post(reverse('create_product'), data=json.dumps(self.product_data), content_type='application/json')

    def test_list_products(self):
        response = self.client.get(reverse('list_products'))
        product_ids = [product['product_id'] for product in response.json()]
        self.assertIn('P001', product_ids)  # Check if P001 is in the list

    def test_create_product(self):
        new_product_data = {
            'product_id': 'P002',
            'model': 'Model Y',
            'serial_number': 'SN54321',
            'stock': 20,
            'inventory_to_stock': 10,
            'warranty_status': '2 years',
            'distributor_info': 'Distributor XYZ',
            'description': 'Another great product',
            'category': 'Shoes',
            'base_price': 149.99
        }
        response = self.client.post(reverse('create_product'), data=json.dumps(new_product_data), content_type='application/json')
        self.assertEqual(response.status_code, 201)  # Check if the product was created successfully

    def test_update_product(self):
        # First, create a product to update
        initial_product_data = {
            'product_id': 'P001',
            'model': 'Model X',
            'serial_number': 'SN12345',
            'stock': 10,
            'inventory_to_stock': 5,
            'warranty_status': '1 Year',
            'distributor_info': 'Distributor A',
            'base_price': 100.00
        }
        
        # Create the initial product
        self.client.post(reverse('create_product'), data=json.dumps(initial_product_data), content_type='application/json')

        # Now prepare the updated product data
        updated_product_data = {
            'product_id': 'P001',  # Ensure this is included if required
            'model': 'Model X Updated',
            'serial_number': 'SN12345',  # Use the same serial number or a valid one
            'stock': 15,
            'inventory_to_stock': 10,  # Adjust this value based on your needs
            'warranty_status': '1 Year',  # Example value, can be updated if needed
            'distributor_info': 'Distributor A',  # Use the same or change if needed
            'base_price': 100.00  # Base price can be updated as necessary
        }
        
        # Make the PUT request to update the product
        response = self.client.put(reverse('update_product', kwargs={'product_id': 'P001'}), 
                                data=json.dumps(updated_product_data), 
                                content_type='application/json')

        # Check if the product was updated successfully
        self.assertEqual(response.status_code, 200)

        # Fetch the updated product from the database
        updated_product = Product.objects.get(product_id='P001')

        # Print the details of the updated product
        print(f"Updated Product Details: "
            f"ID: {updated_product.product_id}, "
            f"Model: {updated_product.model}, "
            f"Stock: {updated_product.stock}, "
            f"Inventory to Stock: {updated_product.inventory_to_stock}, "
            f"Warranty Status: {updated_product.warranty_status}, "
            f"Distributor Info: {updated_product.distributor_info}, "
            f"Base Price: {updated_product.base_price}")

        # Optionally, assert to verify the updated values
        self.assertEqual(updated_product.model, 'Model X Updated')
        self.assertEqual(updated_product.stock, 15)


# shopping cart creation (when customer is created)
class ShoppingCartCreationTests(TestCase):
    def test_shopping_cart_created_on_customer_creation(self):
        # Create a new customer
        customer = Customer.objects.create(
            name='Test Customer',
            email='test@example.com',
            password='testpassword',  # Ensure this is handled securely in real applications
            tax_id='123456789',
            home_address='123 Test St',
            billing_address='123 Test St',
            phone_number='555-1234'
        )
        
        # Check if a shopping cart is automatically created for this customer
        cart = ShoppingCart.objects.filter(customer=customer)
        self.assertEqual(cart.count(), 1)  # Ensure only one cart is created
        self.assertEqual(cart.first().customer, customer)  # Ensure the cart belongs to the correct customer

# shopping cart 
class ShoppingCartTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.customer = Customer.objects.create(
            customer_id="CUST001", name="John Doe", tax_id="TAX12345",
            email="john@example.com", password="password123", home_address="123 Main St",
            billing_address="123 Main St", phone_number="555-1234"
        )
        cls.product = Product.objects.create(
            product_id="PROD001",
            model="Sneaker",
            base_price=100.0,
            stock=10,  # Provide a stock value to avoid null error
            inventory_to_stock=10,
            warranty_status="1 Year",
            distributor_info="Distributor XYZ",
            description="Comfortable running sneakers",
        )

    def setUp(self):
        super().setUp()
        # Ensure a clean state by deleting any existing carts for the customer
        ShoppingCart.objects.filter(customer=self.customer).delete()

        # Create a new ShoppingCart for testing
        self.cart = ShoppingCart.objects.create(customer=self.customer)

    def test_add_to_cart(self):
        # First, add the product to the cart with a quantity of 2
        response = self.client.post(
            reverse('add_to_cart', args=[self.customer.customer_id, self.product.product_id]),
            data=json.dumps({'quantity': 2}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        
        # Verify that the cart item was created with the correct quantity
        cart = ShoppingCart.objects.get(customer=self.customer)
        cart_item = CartItem.objects.get(cart=cart, product=self.product)
        self.assertEqual(cart_item.quantity, 2)

        # Now, add the same product to the cart again with a quantity of 3
        response = self.client.post(
            reverse('add_to_cart', args=[self.customer.customer_id, self.product.product_id]),
            data=json.dumps({'quantity': 3}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        
        # Verify that the cart item quantity is updated correctly
        cart_item.refresh_from_db()  # Refresh the cart item from the database
        self.assertEqual(cart_item.quantity, 5)  # Should now be 5 (2 + 3)

    def test_remove_from_cart(self):
        # First, add a product to the cart to ensure it exists
        # First, add a product to the cart to ensure it exists
        self.client.post(
            reverse('add_to_cart', args=[self.customer.customer_id, self.product.product_id]),
            data=json.dumps({'quantity': 5}),
            content_type='application/json'
        )

        response = self.client.delete(reverse('remove_from_cart', args=[self.customer.customer_id, self.product.product_id]))
        self.assertEqual(response.status_code, 204)  # Expect successful deletion to return 204

        # Check that the cart is now empty
        cart = ShoppingCart.objects.get(customer=self.customer)
        cart_items = CartItem.objects.filter(cart=cart)
        self.assertEqual(cart_items.count(), 0)  # Ensure cart is empty after removal

    def test_get_cart(self):
        # First, add a product to the cart to ensure there are items to retrieve
        self.client.post(
            reverse('add_to_cart', args=[self.customer.customer_id, self.product.product_id]),
            data=json.dumps({'quantity': 2}),
            content_type='application/json'
        )

        response = self.client.get(reverse('get_cart', args=[self.customer.customer_id]))
        self.assertEqual(response.status_code, 200)

        # Ensure the cart_items list is not empty
        self.assertGreater(len(response.json()['cart_items']), 0)

        # Now check the product_id
        self.assertEqual(response.json()['cart_items'][0]['product_id'], self.product.product_id)

    

'''
# wishlist tests 
class WishlistTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a customer for the wishlist tests
        cls.customer = Customer.objects.create(
            customer_id="CUST002",  # Make sure to adjust according to your model's requirements
            name="Jane Doe",
            tax_id="TAX67890",
            email="jane@example.com",
            password="password456",
            home_address="456 Another St",
            billing_address="456 Another St",
            phone_number="555-5678"
        )

    def setUp(self):
        # Clear any existing wishlist for the customer before each test
        Wishlist.objects.filter(customer=self.customer).delete()

    def test_add_to_wishlist(self):
        self.wishlist = Wishlist.objects.create(customer=self.customer)
        self.assertIsNotNone(self.wishlist)

    def test_remove_from_wishlist(self):
        self.wishlist = Wishlist.objects.create(customer=self.customer)
        self.wishlist.delete()
        with self.assertRaises(Wishlist.DoesNotExist):
            Wishlist.objects.get(customer=self.customer)
'''

