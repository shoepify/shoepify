# views.py

"""
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from .models import Customer, OrderItem, Refund, Product, Wishlist, WishlistItem, ShoppingCart, CartItem
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.parsers import JSONParser


from .serializers import CustomerSerializer, WishlistSerializer, RefundSerializer, WishlistItemSerializer, ShoppingCartSerializer, CartItemSerializer, ProductSerializer


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

# Make sure to define the URL patterns for these new views in your urls.py

"""
