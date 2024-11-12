from django.test import TestCase
from django.urls import reverse
import json
from django.http import JsonResponse
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

"""

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
        # Create another customer
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

        # Create  order for the customer2
        cls.order2 = Order.objects.create(
            customer=cls.customer2,
            order_date="2024-01-02",
            total_amount=75.00,
            discount_applied=True
        )
        cls.order3 = Order.objects.create(
            customer=cls.customer3,
            order_date="2024-02-01",
            total_amount=100.00,
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
            price_per_item=100.00
        )

        # Create three comments for the product
        cls.comment1 = Comment.objects.create(
            product=cls.product,
            customer=cls.customer,
            comment="Great product, very comfortable!",
            approval_status="Pending"
        )

        cls.comment2 = Comment.objects.create(
            product=cls.product,
            customer=cls.customer2,
            comment="Very stylish and durable!",
            approval_status="Approved"
        )
        '''
        cls.comment3 = Comment.objects.create(
            product=cls.product,
            customer=cls.customer3,
            comment="Love the fit and feel!",
            approval_status="Pending"
        )
        '''

    def test_comment_creation(self):
        # Test that the comment was created correctly
        self.assertEqual(self.comment2.comment, "Very stylish and durable!")
        self.assertEqual(self.comment2.approval_status, "Approved")

    def test_create_comment(self):
        # Test the API endpoint for creating a comment
        url = reverse('add_comment', kwargs={'product_id': "001"})  # Use correct product_id
        data = {
            'customer_id': "004",  # Use correct customer_id
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
        data_duplicate = {
        'customer_id': "003",  # Same customer_id
        'comment': "This is another comment."
        }
        response_duplicate = self.client.post(url, json.dumps(data_duplicate), content_type='application/json')

        # Assert that the second comment attempt fails
        self.assertEqual(response_duplicate.status_code, 400)
        self.assertIn("You have already commented on this product.", response_duplicate.json()['error'])

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
    
    def test_get_comments(self):
    # Test the API endpoint for getting comments for a product
        url = reverse('get_comments', kwargs={'product_id': "001"})  # Correct product_id (string type)
        response = self.client.get(url)

        # Ensure the response is OK (status code 200)
        self.assertEqual(response.status_code, 200)
        
        # Print the response content for debugging
        print("Response Data:", response.json())
        
        # Ensure the correct comments are returned
        comments = response.json().get('comments', [])
        print("Comments:", comments)  # Debugging the returned comments

        # Check if the correct number of comments are returned
        self.assertEqual(len(comments), 2)  # Should return two comments in this case

        # Ensure the correct content of the comments
        self.assertEqual(comments[0]['comment'], "Great product, very comfortable!")
        self.assertEqual(comments[1]['comment'], "Very stylish and durable!")

        # Ensure the approval statuses are correct
        self.assertEqual(comments[0]['approval_status'], "Pending")
        self.assertEqual(comments[1]['approval_status'], "Approved")
    
    def delete_comment(request, product_id, comment_id):
        if request.method == 'DELETE':
            try:
                # Get the comment for the given product and comment_id
                comment = Comment.objects.get(comment_id=comment_id, product__product_id=product_id)
                
                # Parse the JSON data from the body of the DELETE request
                data = json.loads(request.body)  # Request body contains the customer_id in JSON format
                
                customer_id = data.get('customer_id')

                # Check if the customer ID is valid
                try:
                    customer = Customer.objects.get(customer_id=customer_id)
                except Customer.DoesNotExist:
                    return JsonResponse({'error': 'Invalid customer ID'}, status=400)

                # Check if the customer is the one who made the comment
                if str(comment.customer.customer_id) != customer_id:
                    return JsonResponse({'error': 'You can only delete your own comments.'}, status=403)

                # Proceed to delete the comment
                comment.delete()

                return JsonResponse({}, status=204)  # No content on successful deletion

            except Comment.DoesNotExist:
                return JsonResponse({'error': 'Comment not found.'}, status=404)
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON.'}, status=400)

    def test_delete_comment_not_found(self):
        # Ensure the comment count is correct before deletion
        comment_count_before = Comment.objects.count()

        # Simulate the delete request for a non-existent comment
        url = reverse('delete_comment', kwargs={'product_id': "001", 'comment_id': 999})  # Non-existent comment ID
        data = {'customer_id': "002"}  # customer_id for the owner
        response = self.client.delete(url, data=json.dumps(data), content_type='application/json')

        # Ensure the response indicates that the comment was not found (status code 404)
        self.assertEqual(response.status_code, 404)
        self.assertIn('Comment not found.', response.json()['error'])
        
        # Ensure the comment count remains the same (not deleted)
        comment_count_after = Comment.objects.count()
        self.assertEqual(comment_count_after, comment_count_before)

    def test_delete_comment_invalid_customer_id(self):
        # Ensure the comment exists before deletion
        comment_count_before = Comment.objects.count()

        # Simulate the delete request with an invalid customer ID
        url = reverse('delete_comment', kwargs={'product_id': "001", 'comment_id': self.comment1.comment_id})
        data = {'customer_id': "invalid_customer_id"}  # Invalid customer ID
        response = self.client.delete(url, json.dumps(data), content_type='application/json')

        # Check for status code 403 for invalid customer ID
        self.assertEqual(response.status_code, 403)  # Check that it returns a 403
        self.assertIn('You can only delete your own comments.', response.json()['error'])

        # Ensure the comment count remains the same (not deleted)
        comment_count_after = Comment.objects.count()
        self.assertEqual(comment_count_after, comment_count_before)



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
        """
