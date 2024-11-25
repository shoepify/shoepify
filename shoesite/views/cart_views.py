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
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes, api_view
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import authentication_classes
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    refresh['email'] = user.email
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
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
def add_to_cart_guest(request, user_id, product_id,quantity):
    """
    Add a product to a customer's or guest's shopping cart.
    
    """
    try:
      
        
    
        # If not a customer, check if it's a guest
        guest = Guest.objects.filter(guest_id=user_id).first()
        if guest:
            owner_content_type = ContentType.objects.get_for_model(Guest)
            owner_object_id = guest.guest_id
        else:
            return JsonResponse({'error': 'Invalid user ID'}, status=status.HTTP_404_NOT_FOUND)

        # Retrieve or create a shopping cart for the owner
        cart, created = ShoppingCart.objects.get_or_create(
            owner_content_type=owner_content_type,
            owner_object_id=owner_object_id
        )

        # Get the product to add
        product = get_object_or_404(Product, product_id=product_id)

        # Check if the product already exists in the cart
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        
        if not created:
            # If the product exists, increment the quantity
            if quantity<product.stock and cart_item.quantity+quantity<product.stock:
                cart_item.quantity += quantity
                cart_item.save()
            else:
                return JsonResponse({'error': 'Not enough in stock'}, status=status.HTTP_404_NOT_FOUND)
        else:
            cart_item.quantity=quantity
            cart_item.save()
             

        return JsonResponse({
            'status': 'Product added to cart',
            'cart_item_id': cart_item.cart_item_id,
            'quantity': cart_item.quantity
        }, status=status.HTTP_200_OK)

    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
def add_to_cart_customer(request, user_id, product_id,quantity):
    """
    Add a product to a customer's or guest's shopping cart.
    
    """
    try:
        # Check if the user is a customer
        customer = Customer.objects.filter(customer_id=user_id).first()
        
        if customer:
            owner_content_type = ContentType.objects.get_for_model(Customer)
            owner_object_id = customer.customer_id
        else:
                return JsonResponse({'error': 'Invalid user ID'}, status=status.HTTP_404_NOT_FOUND)

        # Retrieve or create a shopping cart for the owner
        cart, created = ShoppingCart.objects.get_or_create(
            owner_content_type=owner_content_type,
            owner_object_id=owner_object_id
        )

        # Get the product to add
        product = get_object_or_404(Product, product_id=product_id)

        # Check if the product already exists in the cart
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            # If the product exists, increment the quantity
            if quantity<product.stock and cart_item.quantity+quantity<product.stock:
                cart_item.quantity += quantity
                cart_item.save()
            else:
                return JsonResponse({'error': 'Not enough in stock'}, status=status.HTTP_404_NOT_FOUND)
        else:
            cart_item.quantity=quantity
            cart_item.save()       

        return JsonResponse({
            'status': 'Product added to cart',
            'cart_item_id': cart_item.cart_item_id,
            'quantity': cart_item.quantity
        }, status=status.HTTP_200_OK)

    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# remove item from cart
@csrf_exempt
def remove_from_cart_customer(request, user_id, product_id):
    """Remove product from a user's (customer or guest) shopping cart."""
    try:
        #customer = Customer.objects.filter(customer_id=user_id).first()
        #cart = get_object_or_404(ShoppingCart, customer_id=user_id)
        customer = Customer.objects.filter(customer_id=user_id).first()
     
        if customer:
            owner_content_type = ContentType.objects.get_for_model(Customer)
            owner_object_id = customer.customer_id
            cart = get_object_or_404(ShoppingCart,owner_content_type=owner_content_type,
            owner_object_id=owner_object_id)               
        else:
                return JsonResponse({'error': 'Invalid user ID'}, status=status.HTTP_404_NOT_FOUND)
    except Customer.DoesNotExist: 
        return JsonResponse({'error': 'Invalid user ID'}, status=status.HTTP_404_NOT_FOUND)
    product = get_object_or_404(Product, product_id=product_id)
    deleted, _ = CartItem.objects.filter(cart=cart, product=product).delete()

    if deleted:
        return HttpResponse(status=status.HTTP_204_NO_CONTENT)

    return JsonResponse({'status': 'Product not found in cart'}, status=status.HTTP_404_NOT_FOUND)

@csrf_exempt
def remove_from_cart_guest(request, user_id, product_id):
    """Remove product from a user's (customer or guest) shopping cart."""
    try:
        #customer = Customer.objects.filter(customer_id=user_id).first()
        #cart = get_object_or_404(ShoppingCart, customer_id=user_id)
        guest = Guest.objects.filter(guest_id=user_id).first()
        
        if guest:
            owner_content_type = ContentType.objects.get_for_model(Guest)
            owner_object_id = guest.guest_id
            cart = get_object_or_404(ShoppingCart,owner_content_type=owner_content_type,
            owner_object_id=owner_object_id)                  
        else:
                return JsonResponse({'error': 'Invalid user ID'}, status=status.HTTP_404_NOT_FOUND)
    except Guest.DoesNotExist: 
        return JsonResponse({'error': 'Invalid user ID'}, status=status.HTTP_404_NOT_FOUND)
    product = get_object_or_404(Product, product_id=product_id)
    deleted, _ = CartItem.objects.filter(cart=cart, product=product).delete()

    if deleted:
        return HttpResponse(status=status.HTTP_204_NO_CONTENT)

    return JsonResponse({'status': 'Product not found in cart'}, status=status.HTTP_404_NOT_FOUND)

# retrieve the cart
@api_view(['GET'])
@permission_classes([AllowAny])
def get_cart_customer(request, user_id):
    """Retrieve a user's (customer or guest) shopping cart."""
    customer = None
    
    cart = None

    
    # Attempt to retrieve the customer by user_id
    try:
        customer = Customer.objects.get(pk=user_id)
        customer_content_type = ContentType.objects.get_for_model(Customer)
        cart = ShoppingCart.objects.filter(
            owner_content_type=customer_content_type,
            owner_object_id=customer.id
        ).first()
        
    
    except Customer.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)   
      
    if cart:
        cart_serializer = ShoppingCartSerializer(cart)
        return Response(cart_serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_cart_guest(request, user_id):
    """Retrieve a user's (customer or guest) shopping cart."""
    guest = None
    cart = None
    try:
        guest = Guest.objects.get(pk=user_id)
        guest_content_type = ContentType.objects.get_for_model(Guest)
        cart = ShoppingCart.objects.filter(
            owner_content_type=guest_content_type,
            owner_object_id=guest.guest_id
        ).first()
    except Guest.DoesNotExist:
        # Neither customer nor guest exists
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
      
    if cart:
        cart_serializer = ShoppingCartSerializer(cart)
        return Response(cart_serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
