# views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from shoesite.models import Customer, Guest, ShoppingCart, CartItem, Product  # 
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from shoesite.serializers import CustomerSerializer, GuestSerializer, WishlistSerializer, RefundSerializer, WishlistItemSerializer, ShoppingCartSerializer, CartItemSerializer, ProductSerializer
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import NotFound
from django.contrib.contenttypes.models import ContentType

def merge_cart_items(source_cart, target_cart):
    """
    Merge items from source cart into target cart
    """
    # Get all items from source cart
    source_items = CartItem.objects.filter(cart=source_cart)
    
    for source_item in source_items:
        # Try to find matching item in target cart
        try:
            target_item = CartItem.objects.get(
                cart=target_cart,
                product=source_item.product
            )
            # If found, add quantities
            target_item.quantity += source_item.quantity
            target_item.save()
        except CartItem.DoesNotExist:
            # If not found, create new item in target cart
            CartItem.objects.create(
                cart=target_cart,
                product=source_item.product,
                quantity=source_item.quantity
            )
        
        # Delete the source item
        source_item.delete()
@csrf_exempt
@api_view(['POST'])
def add_to_cart(request, user_id, product_id):
    """Add product to a user's (customer or guest) shopping cart."""
    data = JSONParser().parse(request)
    quantity = data.get('quantity', 1)  # Default quantity is 1 if not provided

    # Check if the user is a customer or guest and fetch accordingly
    try:
        customer = get_object_or_404(Customer, customer_id=user_id)
        cart, created = ShoppingCart.objects.get_or_create(customer=customer)
    except Customer.DoesNotExist:
        try:
            guest = get_object_or_404(Guest, guest_id=user_id)
            cart, created = ShoppingCart.objects.get_or_create(guest=guest)
        except Guest.DoesNotExist:
            return JsonResponse({'status': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    product = get_object_or_404(Product, product_id=product_id)

    # Get or create a cart item for the product
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

    if item_created:
        cart_item.quantity = quantity
    else:
        cart_item.quantity += quantity

    cart_item.save()

    return JsonResponse({'status': 'Product added to cart'}, status=status.HTTP_201_CREATED)

# remove item from cart
@csrf_exempt
@api_view(['DELETE'])
def remove_from_cart(request, user_id, product_id):
    """Remove product from a user's (customer or guest) shopping cart."""
    try:
        customer = get_object_or_404(Customer, customer_id=user_id)
        cart = get_object_or_404(ShoppingCart, customer=customer)
    except Customer.DoesNotExist:
        guest = get_object_or_404(Guest, guest_id=user_id)
        cart = get_object_or_404(ShoppingCart, guest=guest)

    product = get_object_or_404(Product, product_id=product_id)
    deleted, _ = CartItem.objects.filter(cart=cart, product=product).delete()

    if deleted:
        return HttpResponse(status=status.HTTP_204_NO_CONTENT)
    return JsonResponse({'status': 'Product not found in cart'}, status=status.HTTP_404_NOT_FOUND)

# retrieve the cart
@api_view(['GET'])
@permission_classes([AllowAny])
def get_cart(request, user_id):
    """Retrieve a user's (customer or guest) shopping cart."""
    customer = None
    guest = None
    cart = None

    try:
        # Attempt to retrieve the customer by user_id
        customer = Customer.objects.get(pk=user_id)
        cart = ShoppingCart.objects.filter(owner_object_id=customer.id).first()
    except Customer.DoesNotExist:
        try:
            # If customer doesn't exist, check for a guest
            guest = Guest.objects.get(guest_id=user_id)
            cart = ShoppingCart.objects.filter(owner_object_id=guest.guest_id).first()
        except Guest.DoesNotExist:
            # Neither customer nor guest exists
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    if cart:
        cart_serializer = ShoppingCartSerializer(cart)
        return Response(cart_serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)