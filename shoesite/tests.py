from django.test import TestCase
from django.urls import reverse
import json
from rest_framework import status
from .models import Customer, Order, OrderItem, Product, Wishlist, WishlistItem, ShoppingCart, CartItem, Comment, Rating
"""
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


class CommentTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create a customer
        cls.customer = Customer.objects.create(
            customer_id="002",
            name="John Doe",
            tax_id="1234567890",
            email="john.doe@example.com",
            password="password123",
            home_address="123 Main St",
            billing_address="123 Main St",
            phone_number="5551234567"
        )

        # Create a product
        cls.product = Product.objects.create(
            product_id="001",
            model="Running Shoes",
            serial_number="SN123456",
            stock=100,
            inventory_to_stock=50,
            warranty_status="Valid",
            distributor_info="BestShoes Inc."
        )

        # Create an order for the customer
        cls.order = Order.objects.create(
            customer=cls.customer,
            order_date="2024-01-01",
            total_amount=50.00,
            discount_applied=False
        )

        # Link the product to the order via OrderItem
        cls.order_item = OrderItem.objects.create(
            order=cls.order,
            product=cls.product,
            quantity=1,
            price_per_item=50.00
        )

        # Create two comments for the product
        cls.comment1 = Comment.objects.create(
            product=cls.product,
            customer=cls.customer,
            comment="Great product, very comfortable!",
            approval_status="Pending"
        )

        cls.comment2 = Comment.objects.create(
            product=cls.product,
            customer=cls.customer,
            comment="Perfect",
            approval_status="Approved"
        )

    def test_comment_creation(self):
        # Test that the comment was created correctly
        self.assertEqual(self.comment2.comment, "Perfect")
        self.assertEqual(self.comment2.approval_status, "Approved")

    def test_create_comment(self):
        # Test the API endpoint for creating a comment
        url = reverse('add_comment', kwargs={'product_id': "001"})  # Use correct product_id
        data = {
            'customer_id': "002",  # Use correct customer_id
            'comment': "This is a new comment."
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')

         # Print the new count of comments after adding the comment
        new_count = Comment.objects.count()
        print("After adding comment:", new_count)
        
        # Ensure the comment was created correctly
        self.assertEqual(response.status_code, 201)  # Assuming 201 for created
        self.assertEqual(Comment.objects.count(), 3)  # Check if a new comment is created
        new_comment = Comment.objects.last()
        self.assertEqual(new_comment.comment, "This is a new comment.")
        self.assertEqual(new_comment.approval_status, "Pending")

    def test_comment_approval_status(self):
        # Test if comment approval status is correct
        self.comment2.approval_status = "Approved"
        self.comment2.save()
        
        self.assertEqual(self.comment2.approval_status, "Approved")

    def test_invalid_comment(self):
        # Test the case where an invalid comment is posted (e.g., invalid customer)
        url = reverse('add_comment', kwargs={'product_id': "001"})
        data = {
            'customer_id': "invalid_customer_id",  # Use a non-existent customer ID
            'comment': "This is an invalid comment."
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 400)  # Expecting 400 for invalid customer
        self.assertIn("Invalid customer ID", response.json()['error'])
"""""

class RatingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a customer
        cls.customer = Customer.objects.create(
            customer_id="002",
            name="John Doe",
            tax_id="1234567890",
            email="john.doe@example.com",
            password="password123",
            home_address="123 Main St",
            billing_address="123 Main St",
            phone_number="5551234567"
        )
        

        # Create a product
        cls.product = Product.objects.create(
            product_id="001",
            model="Running Shoes",
            serial_number="SN123456",
            stock=100,
            inventory_to_stock=50,
            warranty_status="Valid",
            distributor_info="BestShoes Inc.",
            description="Comfortable running shoes for all athletes."
        )

        # Create an order for the customer
        cls.order = Order.objects.create(
            customer=cls.customer,
            order_date="2024-01-01",
            total_amount=50.00,
            discount_applied=False
        )

        # Link the product to the order via OrderItem
        cls.order_item = OrderItem.objects.create(
            order=cls.order,
            product=cls.product,
            quantity=1,
            price_per_item=50.00
        )

        # Create ratings for the product
        cls.rating1 = Rating.objects.create(
            product=cls.product,
            customer=cls.customer,
            rating_value=4
        )

        cls.rating2 = Rating.objects.create(
            product=cls.product,
            customer=cls.customer,
            rating_value=5
        )

    def test_rating_creation(self):
        # Test that the rating was created correctly
        self.assertEqual(self.rating1.rating_value, 4)
        self.assertEqual(self.rating2.rating_value, 5)

    def test_create_rating(self):
        # Test the API endpoint for creating a rating
        url = reverse('add_rating', kwargs={'product_id': "001"})  # Use correct product_id
        data = {
            'customer_id': "002",  # Use correct customer_id
            'rating_value': 5
        }
        # Check the number of ratings before adding a new one
        before_count = Rating.objects.count()
        print(f"Before adding rating: {before_count}")
        
        response = self.client.post(url, json.dumps(data), content_type='application/json')

        # Print the new count of ratings after adding the rating
        new_count = Rating.objects.count()
        print("After adding rating:", new_count)
        
        # Ensure the rating was created correctly
        self.assertEqual(response.status_code, 201)  # Assuming 201 for created
        self.assertEqual(Rating.objects.count(), 3)  # Check if a new rating is created
        new_rating = Rating.objects.last()
        self.assertEqual(new_rating.rating_value, 5)

    def test_invalid_rating(self):
        # Test the case where an invalid rating is posted (e.g., invalid customer)
        url = reverse('add_rating', kwargs={'product_id': "001"})
        data = {
            'customer_id': "invalid_customer_id",  # Use a non-existent customer ID
            'rating_value': 3
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 400)  # Expecting 400 for invalid customer
        self.assertIn("Invalid customer ID", response.json()['error'])

    def test_rating_value_range(self):
        # Test if rating value is within the valid range (1-5)
        url = reverse('add_rating', kwargs={'product_id': "001"})
        
        # Test invalid rating value (outside range)
        data = {
            'customer_id': "002",
            'rating_value': 6  # Invalid rating value
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid rating value", response.json()['error'])

        # Test valid rating value
        data = {
            'customer_id': "002",
            'rating_value': 4  # Valid rating value
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_retrieve_ratings(self):
        # Test retrieving ratings for a specific product
        url = reverse('get_ratings', kwargs={'product_id': "001"})  # Use correct product_id
        response = self.client.get(url)

        # Ensure the response is successful
        self.assertEqual(response.status_code, 200)

        # Parse the JSON response
        data = response.json()

        # Check the number of ratings returned
        self.assertEqual(len(data['ratings']), 2)

        # Verify the rating values and customer IDs
        ratings_values = [rating['rating_value'] for rating in data['ratings']]
        customer_ids = [rating['customer_id'] for rating in data['ratings']]

        self.assertIn(4, ratings_values)
        self.assertIn(5, ratings_values)
        self.assertIn("002", customer_ids)