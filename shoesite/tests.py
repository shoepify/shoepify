from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
import json
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from rest_framework import status
from .models import Customer, Discount, Order, OrderItem, Product, Wishlist, WishlistItem, ShoppingCart, CartItem, Comment, Rating, Guest
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

"""
"""
class ShoppingCartCreationTests(TestCase):
    def test_shopping_cart_created_on_customer_creation(self):
        # Create a new customer
        customer = Customer.objects.create(
            name='Test Customer',
            email='test@example.com',
            password='testpassword',  # Ensure this is hashed when using in production
            tax_id='123456789',
            home_address='123 Test St',
        )

        # Get the ContentType for the Customer model
        customer_content_type = ContentType.objects.get_for_model(Customer)

        # Check if a shopping cart is automatically created for this customer
        cart = ShoppingCart.objects.filter(owner_content_type=customer_content_type, owner_object_id=customer.id)

        self.assertEqual(cart.count(), 1)  # Ensure only one cart is created
        self.assertEqual(cart.first().owner_object_id, customer.id)  # Ensure the cart belongs to the correct customer
    
    def test_shopping_cart_created_on_guest_creation(self):
        # Create a new guest
        guest = Guest.objects.create(session_id='test_session_123')

        # Get the ContentType for the Guest model
        guest_content_type = ContentType.objects.get_for_model(Guest)

        # Check if a shopping cart is automatically created for this guest
        cart = ShoppingCart.objects.filter(owner_content_type=guest_content_type, owner_object_id=guest.guest_id)

        self.assertEqual(cart.count(), 1)  # Ensure only one cart is created
        self.assertEqual(cart.first().owner_object_id, guest.guest_id)  # Ensure the cart belongs to the correct guest



class ShoppingCartItemTests(TestCase):

    def test_adding_item_to_cart(self):
        # Create a new customer
        customer = Customer.objects.create(
            name='Test Customer',
            email='test@example.com',
            password='testpassword',
            tax_id='123456789',
            home_address='123 Test St',
        )

        # Get the ContentType for the Customer model
        customer_content_type = ContentType.objects.get_for_model(Customer)

        # Create a shopping cart for the customer
        cart = ShoppingCart.objects.create(owner_content_type=customer_content_type, owner_object_id=customer.id)

        # Create a new product
        product = Product.objects.create(
            model='Test Product',
            serial_number='SN12345',
            stock=10,
            inventory_to_stock=10,
            warranty_status='Valid',
            distributor_info='Distributor 1',
            description='A sample product',
            category='Category 1',
            base_price=100.00,
            price=100.00
        )

        # Add the product to the shopping cart
        cart_item = CartItem.objects.create(cart=cart, product=product, quantity=2)

        # Verify that the cart now has the correct item
        self.assertEqual(cart.cartitem_set.count(), 1)  # Only one item should be in the cart
        self.assertEqual(cart_item.quantity, 2)  # The quantity should be 2
        self.assertEqual(cart_item.product, product)  # Ensure the correct product is in the cart

    def test_deleting_item_from_cart(self):
        # Create a new guest
        guest = Guest.objects.create(session_id='test_session_123')

        # Get the ContentType for the Guest model
        guest_content_type = ContentType.objects.get_for_model(Guest)

        # Create a shopping cart for the guest
        cart = ShoppingCart.objects.create(owner_content_type=guest_content_type, owner_object_id=guest.guest_id)

        # Create a new product
        product = Product.objects.create(
            model='Test Product',
            serial_number='SN12345',
            stock=10,
            inventory_to_stock=10,
            warranty_status='Valid',
            distributor_info='Distributor 1',
            description='A sample product',
            category='Category 1',
            base_price=100.00,
            price=100.00
        )

        # Add the product to the shopping cart
        cart_item = CartItem.objects.create(cart=cart, product=product, quantity=2)

        # Delete the item from the cart
        cart_item.delete()

        # Verify that the cart is now empty
        self.assertEqual(cart.cartitem_set.count(), 0)  # The cart should be empty after deletion
"""
class ShoppingCartTests(TestCase):

    def setUp(self):
        # Create and save the discount instance first
        self.discount = Discount.objects.create(
            discount_name="Test Discount",
            discount_rate=10.0,
            start_date="2024-11-01",
            end_date="2024-12-01"
        )

        # Create and save a customer instance for later testing
        self.customer = Customer.objects.create(
            name="Test Customer",
            email="test@example.com",
            password="password123",
            home_address="123 Test St."
        )

        # Create and save a guest instance
        self.guest = Guest.objects.create(
            session_id="test_session_123"
        )

        # Create and save a product instance
        self.product = Product(
            model="Test Model",
            serial_number="12345",
            stock=10,
            inventory_to_stock=10,
            warranty_status="Active",
            distributor_info="Test Distributor",
            description="Test Product",
            category="Electronics",
            base_price=100.0,
            price=90.0,
            discount=self.discount
        )

        # Temporarily bypass update_avg_rating for testing
        original_update_avg_rating = Product.update_avg_rating
        Product.update_avg_rating = lambda self: None

        # Save the Product instance explicitly
        self.product.save()  # Ensure the product is saved to the database

        # Restore the original method after saving
        Product.update_avg_rating = original_update_avg_rating
    
        # Temporarily bypass update_avg_rating for testing
        original_update_avg_rating = Product.update_avg_rating
        Product.update_avg_rating = lambda self: None
        
        # Save the Product instance explicitly
        self.product.save()  # Ensure the product is saved to the database
        
        # Restore the original method after saving
        Product.update_avg_rating = original_update_avg_rating

    def test_add_to_cart_customer(self):
        # Get the content type for the Customer model
        customer_content_type = ContentType.objects.get_for_model(Customer)

        # Create the shopping cart for the customer
        shopping_cart = ShoppingCart.objects.create(
            owner_content_type=customer_content_type,
            owner_object_id=self.customer.customer_id  # Use the customer's ID here
        )

        # Add the product to the cart
        cart_item = shopping_cart.cartitem_set.create(
            product=self.product,
            quantity=2
        )

        # Assert the cart item was added
        self.assertEqual(cart_item.product, self.product)
        self.assertEqual(cart_item.quantity, 2)

    def test_add_to_cart_guest(self):
        # Get the content type for the Guest model
        guest_content_type = ContentType.objects.get_for_model(Guest)

        # Create the shopping cart for the guest
        guest_cart = ShoppingCart.objects.create(
            owner_content_type=guest_content_type,
            owner_object_id=self.guest.guest_id  # Use the guest's ID here
        )

        # Add the product to the guest's cart
        cart_item = guest_cart.cartitem_set.create(
            product=self.product,
            quantity=1
        )

        # Assert the cart item was added
        self.assertEqual(cart_item.product, self.product)
        self.assertEqual(cart_item.quantity, 1)











"""
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


"""


class CommentTests(TestCase):

    def setUp(self):
        # Create some test data
        self.customer = Customer.objects.create(
            name="John Doe",
            tax_id="TAX123456",  # Added tax_id
            email="johndoe@example.com",
            password="securepassword",
            home_address="123 Test St",
        )
        
        # Create a Discount instance
        discount_instance = Discount.objects.create(discount_name="Seasonal Sale", discount_rate=0.10, start_date="2024-01-01", end_date="2024-12-31")
        
        # Create the product with the Discount instance
        self.product = Product.objects.create(
            model="ShoeModel",
            serial_number="SN123",
            stock=100,
            inventory_to_stock=50,
            warranty_status="Active",
            distributor_info="Distributor XYZ",
            description="A great shoe.",
            category="Footwear",
            base_price=100.00,
            price=90.00,
            discount=discount_instance,  # Assign the Discount instance here
        )
        
        # Create an order with the product
        self.order = Order.objects.create(
            order_date="2024-11-19",
            total_amount=108.00,
            discount_applied=10.00,
            payment_status="Paid",
            customer=self.customer
        )

        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            price_per_item=120.00
        )
        
        # Create a valid comment for testing
        self.comment = Comment.objects.create(
            customer=self.customer,
            product=self.product,
            comment="Great shoes, would buy again.",
            approval_status="pending"
        )

    def test_add_comment(self):
        """Test adding a comment by a customer who has purchased the product."""
        url = reverse('add_comment', kwargs={'product_id': self.product.product_id})
        data = {'customer_id': self.customer.customer_id, 'comment': 'Nice product!'}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 2)  # One existing comment + the new one
        self.assertEqual(Comment.objects.last().comment, 'Nice product!')

    def test_add_comment_duplicate(self):
        """Test adding a duplicate comment for the same product by the same customer."""
        url = reverse('add_comment', kwargs={'product_id': self.product.product_id})
        data = {'customer_id': self.customer.customer_id, 'comment': 'Great shoes, would buy again.'}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("duplicate", response.data["detail"])

    def test_add_comment_invalid_customer(self):
        """Test adding a comment by a customer who has not purchased the product."""
        invalid_customer = Customer.objects.create(
            name="Jane Doe",
            tax_id="TAX654321",
            email="janedoe@example.com",
            password="securepassword",
            home_address="456 Test St",
        )
        url = reverse('add_comment', kwargs={'product_id': self.product.product_id})
        data = {'customer_id': invalid_customer.customer_id, 'comment': 'Nice product!'}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("purchase", response.data["detail"])

    def test_delete_comment(self):
        """Test deleting a comment by the customer who made the comment."""
        url = reverse('delete_comment', kwargs={'comment_id': self.comment.comment_id})
        self.client.force_login(self.customer)
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 0)

    def test_delete_comment_invalid_customer(self):
        """Test that a comment cannot be deleted by someone who is not the author."""
        another_customer = Customer.objects.create(
            name="Mike Smith",
            tax_id="TAX789012",
            email="mikesmith@example.com",
            password="securepassword",
            home_address="789 Test St",
        )
        url = reverse('delete_comment', kwargs={'comment_id': self.comment.comment_id})
        self.client.force_login(another_customer)
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_comments(self):
        """Test that comments can be retrieved for a product."""
        url = reverse('get_comments', kwargs={'product_id': self.product.product_id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['comment'], 'Great shoes, would buy again.')

    def test_get_pending_comments(self):
        """Test that a ProductManager can retrieve pending comments."""
        url = reverse('get_pending_comments')
        self.client.force_login(self.product.productmanager)  # Assuming the ProductManager is already created
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['approval_status'], 'pending')

    def test_update_approval(self):
        """Test that a ProductManager can approve a pending comment."""
        url = reverse('update_approval', kwargs={'comment_id': self.comment.comment_id})
        self.client.force_login(self.product.productmanager)  # Assuming the ProductManager is already created
        response = self.client.patch(url, {'approval_status': 'approved'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Comment.objects.last().approval_status, 'approved')

    def test_update_approval_invalid_comment(self):
        """Test that attempting to approve a non-existent comment returns an error."""
        url = reverse('update_approval', kwargs={'comment_id': 999})
        self.client.force_login(self.product.productmanager)
        response = self.client.patch(url, {'approval_status': 'approved'})
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_approval_invalid_comment_id(self):
        """Test that providing an invalid comment ID returns an error."""
        url = reverse('update_approval', kwargs={'comment_id': 999})
        self.client.force_login(self.product.productmanager)
        response = self.client.patch(url, {'approval_status': 'approved'})
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
  
"""
class RatingTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create customers
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
        
        cls.customer2 = Customer.objects.create(
            customer_id="003",
            name="Jane Doe",
            tax_id="9876543210",
            email="jane.doe@example.com",
            password="password456",
            home_address="456 Another St",
            billing_address="456 Another St",
            phone_number="5559876543"
        )

        cls.customer3 = Customer.objects.create(
            customer_id="004",
            name="Sam Smith",
            tax_id="1122334455",
            email="sam.smith@example.com",
            password="password789",
            home_address="789 Elm St",
            billing_address="789 Elm St",
            phone_number="5552468101"
        )

        # Create product
        cls.product = Product.objects.create(
            product_id="001",
            model="Running Shoes",
            serial_number="SN123456",
            stock=100,
            inventory_to_stock=50,
            warranty_status="Valid",
            distributor_info="BestShoes Inc."
        )

        # Create orders and link them to customers
        cls.order = Order.objects.create(
            customer=cls.customer,
            order_date="2024-01-01",
            total_amount=50.00,
            discount_applied=False
        )

        cls.order2 = Order.objects.create(
            customer=cls.customer2,
            order_date="2024-01-02",
            total_amount=75.00,
            discount_applied=True
        )
        cls.order3 = Order.objects.create(
            customer=cls.customer3,
            order_date="2024-01-02",
            total_amount=75.00,
            discount_applied=True
        )

        # Link the product to the order via OrderItem
        cls.order_item = OrderItem.objects.create(
            order=cls.order,
            product=cls.product,
            quantity=1,
            price_per_item=50.00
        )

        cls.order_item2 = OrderItem.objects.create(
            order=cls.order2,
            product=cls.product,
            quantity=1,
            price_per_item=75.00
        )
        cls.order_item3 = OrderItem.objects.create(
            order=cls.order3,
            product=cls.product,
            quantity=1,
            price_per_item=75.00
        )
        
        # Create ratings for the product
        cls.rating1 = Rating.objects.create(
            product=cls.product,
            customer=cls.customer,
            rating_value=4
        )

        cls.rating2 = Rating.objects.create(
            product=cls.product,
            customer=cls.customer2,
            rating_value=5
        )

    
    
    def test_create_rating(self):
    
        url = reverse('add_rating', kwargs={'product_id': self.product.product_id})
        data = {
            'customer_id': "004",
            'rating_value': 5 }
        
        
        response = self.client.post(url, json.dumps(data), content_type='application/json')

        # Debugging the response content
        print("Response Content:", response.content)

        # Verify status code and content
        self.assertEqual(response.status_code, 201)

        new_rating = Rating.objects.filter(product=self.product, customer=self.customer3).first()
        self.assertIsNotNone(new_rating)
        self.assertEqual(new_rating.rating_value, 5) 

    def test_retrieve_ratings(self):
    
        url = reverse('get_ratings', kwargs={'product_id': self.product.product_id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Verify retrieved ratings count and content
        data = response.json()
        self.assertEqual(len(data['ratings']), 2)
        ratings_values = [rating['rating_value'] for rating in data['ratings']]
        customer_ids = [rating['customer_id'] for rating in data['ratings']]
        
        self.assertIn(4, ratings_values)
        self.assertIn(5, ratings_values)
        self.assertIn(self.customer.customer_id, customer_ids)
        self.assertIn(self.customer2.customer_id, customer_ids)

    def test_invalid_customer_rating(self):
    
        url = reverse('add_rating', kwargs={'product_id': self.product.product_id})
        data = {
            'customer_id': "invalid_customer_id",
            'rating_value': 4
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid customer ID", response.json()['error'])

    def test_rating_already_given(self):
    
        url = reverse('add_rating', kwargs={'product_id': self.product.product_id})
        data = {
            'customer_id': self.customer.customer_id,
            'rating_value': 3
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("You have already rated this product.", response.json()['error'])

    def test_delete_rating(self):
        # Ensure the rating exists before deletion
        rating_count_before = Rating.objects.count()

        # Simulate the delete request for the rating by the owner
        url = reverse('delete_rating', kwargs={'product_id': self.product.product_id, 'rating_id': self.rating1.rating_id})
        data = {'customer_id': "002"}  # customer_id for the owner of the rating
        response = self.client.delete(url, json.dumps(data), content_type='application/json')

        # Ensure the response is successful (status code 204 for no content)
        self.assertEqual(response.status_code, 204)

        # Check if the rating was deleted
        rating_count_after = Rating.objects.count()
        self.assertEqual(rating_count_after, rating_count_before - 1)  # One less rating

    def test_delete_rating_not_found(self):
        # Ensure the rating count is correct before deletion
        rating_count_before = Rating.objects.count()

        # Simulate the delete request for a non-existent rating
        url = reverse('delete_rating', kwargs={'product_id': self.product.product_id, 'rating_id': 999})  # Non-existent rating ID
        data = {'customer_id': "002"}  # customer_id for the owner
        response = self.client.delete(url, json.dumps(data), content_type='application/json')

        # Ensure the response indicates that the rating was not found (status code 404)
        self.assertEqual(response.status_code, 404)
        self.assertIn('Rating not found.', response.json()['error'])

        # Ensure the rating count remains the same (not deleted)
        rating_count_after = Rating.objects.count()
        self.assertEqual(rating_count_after, rating_count_before)

    def test_delete_rating_invalid_customer_id(self):
        # Ensure the rating exists before deletion
        rating_count_before = Rating.objects.count()

        # Simulate the delete request with an invalid customer ID
        url = reverse('delete_rating', kwargs={'product_id': self.product.product_id, 'rating_id': self.rating1.rating_id})
        data = {'customer_id': "invalid_customer_id"}  # Invalid customer ID
        response = self.client.delete(url, json.dumps(data), content_type='application/json')

        # Ensure the response indicates invalid customer ID (status code 403)
        self.assertEqual(response.status_code, 403)
        self.assertIn('You can only delete your own ratings.', response.json()['error'])

        # Ensure the rating count remains the same (not deleted)
        rating_count_after = Rating.objects.count()
        self.assertEqual(rating_count_after, rating_count_before)    
"""