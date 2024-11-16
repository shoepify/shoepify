# views.py


from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.http import JsonResponse, HttpResponse
from .models import Comment, Customer, OrderItem, Refund, Product, Wishlist, WishlistItem, ShoppingCart, CartItem, Rating, SalesManager, ProductManager
import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import CustomerSerializer, ShoppingCartSerializer, ProductSerializer, UserSerializer 
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password, check_password
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
#new rivar



def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    refresh['email'] = user.email

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
    
@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'error': 'Please provide both email and password'},
                      status=status.HTTP_400_BAD_REQUEST)
    user=User.objects.get(email=email)
    serializer=UserSerializer
    '''
    # Check user type based on email domain
    if email.endswith('@sm.com'):
        try:
            user = SalesManager.objects.get(email=email)
            serializer = SalesManagerSerializer
            user_type = 'sales_manager'
        except SalesManager.DoesNotExist:
            return Response({'error': 'Invalid credentials'},
                          status=status.HTTP_404_NOT_FOUND)
    elif email.endswith('@pm.com'):
        try:
            user = ProductManager.objects.get(email=email)
            serializer = ProductManagerSerializer
            user_type = 'product_manager'
        except ProductManager.DoesNotExist:
            return Response({'error': 'Invalid credentials'},
                          status=status.HTTP_404_NOT_FOUND)
    else:
        try:
            user = Customer.objects.get(email=email)
            serializer = CustomerSerializer
            user_type = 'customer'
        except Customer.DoesNotExist:
            return Response({'error': 'Invalid credentials'},
                          status=status.HTTP_404_NOT_FOUND)
    '''
    if not check_password(password, user.password):
        return Response({'error': 'Invalid credentials'},
                      status=status.HTTP_404_NOT_FOUND)

    tokens = get_tokens_for_user(user)
    return Response({
        'tokens': tokens,
        'user': serializer(user).data
    })


@api_view(['POST'])
def signup(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'error': 'Please provide both email and password'},
                      status=status.HTTP_400_BAD_REQUEST)
    model=User
    serializer=UserSerializer(data=request.data)
    '''#Determine user type and serializer based on email domain
    if email.endswith('@sm.com'):
        serializer = SalesManagerSerializer(data=request.data)
        model = SalesManager
        user_type = 'sales_manager'
    elif email.endswith('@pm.com'):
        serializer = ProductManagerSerializer(data=request.data)
        model = ProductManager
        user_type = 'product_manager'
    else:
        serializer = CustomerSerializer(data=request.data)
        model = Customer
        user_type = 'customer'
    '''
    if serializer.is_valid():
        if model.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists'},
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Hash password before saving
        user = serializer.save()
        user.password = make_password(password)
        user.save()

        tokens = get_tokens_for_user(user)
        return Response({
            'tokens': tokens,
            'user': serializer.data
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])

@permission_classes([IsAuthenticated])
def test_token(request):
    # Optionally print user and token data for debugging
    print(f"Authenticated User: {request.user}")
    print(f"Token: {request.auth}")

    return Response(f"Passed for {request.user.email}")
"""
#new rivar

# Sign-Up
@api_view(['POST'])
def sign_up(request):
    data = request.data
    data['password'] = make_password(data.get('password'))
    serializer = CustomerSerializer(data=data)
    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return JsonResponse({'message': 'User registered successfully', 'token': token.key}, status=201)
    return JsonResponse(serializer.errors, status=400)
# Login
@api_view(['POST'])
def login(request):
    data = request.data
    user = authenticate(username=data.get('email'), password=data.get('password'))
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return JsonResponse({'token': token.key}, status=200)
    return JsonResponse({'error': 'Invalid credentials'}, status=400)

# CUSTOMER
@csrf_exempt
def get_customer(request, customer_id):
    if request.method == 'GET':
        customer = get_object_or_404(Customer, customer_id=customer_id)
        return JsonResponse({'customer_id': customer.customer_id, 'name': customer.name})

@csrf_exempt
def create_customer(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        serializer = CustomerSerializer(data=data)
        if serializer.is_valid():
            customer = serializer.save()
            return JsonResponse({'message': 'Customer created successfully', 'customer_id': customer.customer_id}, status=201)
        return JsonResponse(serializer.errors, status=400)



# PRODUCT
# List all products
@csrf_exempt
def list_products(request):
    if request.method == 'GET':
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return JsonResponse(serializer.data, safe=False, status=200)

# Create a new product
@csrf_exempt
def create_product(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            product = serializer.save()
            return JsonResponse({'message': 'Product created successfully', 'product_id': product.product_id}, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Retrieve a product by ID
@csrf_exempt
def get_product(request, product_id):
    if request.method == 'GET':
        product = get_object_or_404(Product, product_id=product_id)
        serializer = ProductSerializer(product)
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)

# Update an existing product
@csrf_exempt  # Consider removing this if not needed
def update_product(request, product_id):
    if request.method == 'PUT':
        try:
            product = get_object_or_404(Product, product_id=product_id)
            data = json.loads(request.body)
            print(f"Updating product {product_id} with data: {data}")  # Debugging output

            serializer = ProductSerializer(product, data=data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse({'message': 'Product updated successfully'}, status=status.HTTP_200_OK)

            print(f"Serializer errors: {serializer.errors}")  # Debugging output
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Delete a product
@csrf_exempt
def delete_product(request, product_id):
    if request.method == 'DELETE':
        product = get_object_or_404(Product, product_id=product_id)
        product.delete()
        return JsonResponse({'message': 'Product deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


# SHOPPING CART, CART ITEMS
@csrf_exempt
def add_to_cart(request, customer_id, product_id):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        quantity = data.get('quantity', 1)  # Default quantity is 1 if not provided

        customer = get_object_or_404(Customer, customer_id=customer_id)
        cart, created = ShoppingCart.objects.get_or_create(customer=customer)
        product = get_object_or_404(Product, product_id=product_id)

        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

        if item_created:
            # Set the quantity for the new cart item
            cart_item.quantity = quantity
        else:
            # Increment quantity if the item already exists
            cart_item.quantity += quantity

        # Save the cart item regardless of whether it was created or updated
        cart_item.save()

        return JsonResponse({'status': 'Product added to cart'}, status=status.HTTP_201_CREATED)

@csrf_exempt
def remove_from_cart(request, customer_id, product_id):
    if request.method == 'DELETE':
        customer = get_object_or_404(Customer, customer_id=customer_id)
        cart = get_object_or_404(ShoppingCart, customer=customer)
        product = get_object_or_404(Product, product_id=product_id)

        deleted, _ = CartItem.objects.filter(cart=cart, product=product).delete()
        if deleted:
            return HttpResponse(status=status.HTTP_204_NO_CONTENT)  # Use HttpResponse for 204 No Content
        return JsonResponse({'status': 'Product not found in cart'}, status=status.HTTP_404_NOT_FOUND)

    # If the request method is not DELETE, you can return a method not allowed response
    return JsonResponse({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
@csrf_exempt
def get_cart(request, customer_id):
    if request.method == 'GET':
        customer = get_object_or_404(Customer, customer_id=customer_id)
        cart = ShoppingCart.objects.filter(customer=customer).first()

        if cart:
            serializer = ShoppingCartSerializer(cart)
            return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'status': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

# WISHLIST
@csrf_exempt
def add_to_wishlist(request, customer_id, product_id):
    if request.method == 'POST':
        customer = get_object_or_404(Customer, customer_id=customer_id)
        wishlist = customer.wishlist
        product = get_object_or_404(Product, product_id=product_id)

        if not WishlistItem.objects.filter(wishlist=wishlist, product=product).exists():
            WishlistItem.objects.create(wishlist=wishlist, product=product)
            return JsonResponse({'status': 'Product added to wishlist'}, status=201)
        return JsonResponse({'status': 'Product already in wishlist'}, status=200)

@csrf_exempt
def remove_from_wishlist(request, customer_id, product_id):
    if request.method == 'DELETE':
        customer = get_object_or_404(Customer, customer_id=customer_id)
        wishlist = customer.wishlist
        product = get_object_or_404(Product, product_id=product_id)

        deleted, _ = WishlistItem.objects.filter(wishlist=wishlist, product=product).delete()
        if deleted:
            return JsonResponse({'status': 'Product removed from wishlist'}, status=200)
        return JsonResponse({'status': 'Product not found in wishlist'}, status=404)

@csrf_exempt
def get_wishlist(request, customer_id):
    if request.method == 'GET':
        customer = get_object_or_404(Customer, customer_id=customer_id)
        wishlist = Wishlist.objects.filter(customer=customer).first()

        if wishlist:
            wishlist_items = wishlist.wishlistitem_set.all()
            items_data = [{'product_id': item.product.product_id, 'model': item.product.model} for item in wishlist_items]
            return JsonResponse({'customer_id': customer.customer_id, 'wishlist_items': items_data})
        else:
            return JsonResponse({'customer_id': customer.customer_id, 'wishlist_items': []})

# Traditional views for Refund
@csrf_exempt
def request_refund(request, order_item_id):
    if request.method == 'POST':
        order_item = get_object_or_404(OrderItem, pk=order_item_id)
        order_date = order_item.order.order_date

        if (timezone.now().date() - order_date).days > 30:
            return JsonResponse({'status': 'error', 'message': 'Refund request is past the 30-day period.'}, status=400)

        if Refund.objects.filter(order_item=order_item).exists():
            return JsonResponse({'status': 'error', 'message': 'Refund request already exists for this order item.'}, status=400)

        refund = Refund(order_item=order_item, status='Pending')
        refund.save()
        return JsonResponse({'status': 'success', 'message': 'Refund request submitted successfully.'}, status=201)

@csrf_exempt
def approve_refund(request, refund_id):
    if request.method == 'POST':
        refund = get_object_or_404(Refund, pk=refund_id)

        if refund.status != 'Pending':
            return JsonResponse({'status': 'error', 'message': 'Refund request has already been processed.'}, status=400)

        refund.approve_refund()  # Calls the approve_refund method in the Refund model
        return JsonResponse({'status': 'success', 'message': 'Refund approved successfully.', 'refunded_amount': refund.refunded_amount}, status=200)

@csrf_exempt
def add_comment(request, product_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        customer_id = data.get('customer_id')
        comment_text = data.get('comment')
        
        # Check if the customer exists
        if not Customer.objects.filter(customer_id=customer_id).exists():
            return JsonResponse({"error": "Invalid customer ID."}, status=400)
        
        # Check if the customer has purchased the product
        has_purchased = OrderItem.objects.filter(order__customer_id=customer_id, product__product_id=product_id).exists()
        
        if not has_purchased:
            return JsonResponse({"error": "You cannot give comment before buying it."}, status=403)
        
        # Check if the customer has already commented on this product
        if Comment.objects.filter(customer_id=customer_id, product_id=product_id).exists():
            return JsonResponse({"error": "You have already commented on this product."}, status=400)
        
        # If purchased, save the comment
        comment = Comment.objects.create(
            product_id=product_id,
            customer_id=customer_id,
            comment=comment_text,
            approval_status='Pending'  # Waiting for admin approval
        )
        
        return JsonResponse({"message": "Your comment is waiting for approval.", "comment_id": comment.comment_id}, status=201)
    
    return JsonResponse({"error": "Invalid request."}, status=400)

def get_comments(request, product_id):
    if request.method == 'GET':
        comments = Comment.objects.filter(product_id=product_id)
        #If we want just the approveed ones use this
        #comments = Comment.objects.filter(product_id=product_id, approval_status='Approved')
        comments_data = [
            {
                "comment_id": comment.comment_id,
                "customer_id": comment.customer.customer_id,
                "comment": comment.comment,
                "approval_status": comment.approval_status,
            }
            for comment in comments
        ]
        
        return JsonResponse({"comments": comments_data}, status=200)
    
    return JsonResponse({"error": "Invalid request."}, status=400)

def delete_comment(request, product_id, comment_id):
    if request.method == 'DELETE':
        try:
            # Get the comment for the given product and comment_id
            comment = Comment.objects.get(comment_id=comment_id, product__product_id=product_id)
            
            # Parse the JSON data from the body of the DELETE request
            data = json.loads(request.body)  # Request body contains the customer_id in JSON format
            
            customer_id = data.get('customer_id')

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

@csrf_exempt
def add_rating(request, product_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        customer_id = data.get('customer_id')
        rating_value = data.get('rating_value')
        
        # Validate rating value (ensure it's between 1 and 5)
        try:
            rating_value = int(rating_value)
            if rating_value < 1 or rating_value > 5:
                return JsonResponse({"error": "Invalid rating value. Must be between 1 and 5."}, status=400)
        except ValueError:
            return JsonResponse({"error": "Invalid rating value. Must be an integer."}, status=400)
        
        # Check if the customer exists
        customer = Customer.objects.filter(customer_id=customer_id).first()
        if not customer:
            return JsonResponse({"error": "Invalid customer ID."}, status=400)
        
        # Check if the customer has already rated this product
        if Rating.objects.filter(customer_id=customer_id, product_id=product_id).exists():
            return JsonResponse({"error": "You have already rated this product."}, status=400)
        
        # Check if the customer has purchased the product
        has_purchased = OrderItem.objects.filter(order__customer_id=customer_id, product__product_id=product_id).exists()
        
        if not has_purchased:
            return JsonResponse({"error": "You cannot rate a product before buying it."}, status=403)
        
        # Save the rating (no approval status needed for ratings)
        rating = Rating.objects.create(
            product_id=product_id,
            customer_id=customer_id,
            rating_value=rating_value
        )
        
        return JsonResponse({"message": "Your rating has been submitted.", "rating_id": rating.rating_id}, status=201)
    
    return JsonResponse({"error": "Invalid request."}, status=400)

def get_ratings(request, product_id):
    if request.method == 'GET':
        # Retrieve all ratings for the product
        ratings = Rating.objects.filter(product_id=product_id)
        ratings_data = [
            {
                "rating_value": rating.rating_value,
                "customer_id": rating.customer.customer_id,
                # If you have comments for ratings, you can include them here (e.g., for future use)
                "comment": rating.comment if hasattr(rating, 'comment') else None
            }
            for rating in ratings
        ]
        
        return JsonResponse({"ratings": ratings_data}, status=200)
    
    return JsonResponse({"error": "Invalid request."}, status=400)

def delete_rating(request, product_id, rating_id):
    if request.method == 'DELETE':
        try:
            # Get the rating for the given product and rating_id
            rating = Rating.objects.get(rating_id=rating_id, product__product_id=product_id)
            
            # Parse the JSON data from the body of the DELETE request
            data = json.loads(request.body)
            customer_id = data.get('customer_id')

            # Check if the customer is the one who made the rating
            if str(rating.customer.customer_id) != customer_id:
                return JsonResponse({'error': 'You can only delete your own ratings.'}, status=403)

            # Proceed to delete the rating
            rating.delete()

            return JsonResponse({}, status=204)  # No content on successful deletion

        except Rating.DoesNotExist:
            return JsonResponse({'error': 'Rating not found.'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)

# Make sure to define the URL patterns for these new views in your urls.py
"""


