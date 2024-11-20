from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from shoesite.models import Customer, Guest, ShoppingCart, CartItem, Product, Order, OrderItem  # Add Order and OrderItem
import json
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from shoesite.serializers import ShoppingCartSerializer
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication




# SHOPPING CART, CART ITEMS

# Add item to cart
@csrf_exempt
@permission_classes([AllowAny])
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
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

    # Ensure the product is saved before referencing in CartItem
    if product.pk is None:
        product.save()

    # Get or create a cart item for the product
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

    if item_created:
        cart_item.quantity = quantity
    else:
        cart_item.quantity += quantity

    cart_item.save()

    return JsonResponse({'status': 'Product added to cart'}, status=status.HTTP_201_CREATED)


# Remove item from cart
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

    # Ensure the product is saved before referencing in CartItem
    if product.pk is None:
        product.save()
        
    deleted, _ = CartItem.objects.filter(cart=cart, product=product).delete()

    if deleted:
        return HttpResponse(status=status.HTTP_204_NO_CONTENT)
    return JsonResponse({'status': 'Product not found in cart'}, status=status.HTTP_404_NOT_FOUND)


# Retrieve the cart
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


# Place order
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])  # Temporarily allow unauthenticated access
def place_order(request, user_id):
    """Place an order for the items in the user's shopping cart."""
    try:
        # Fetch the customer's cart
        customer = get_object_or_404(Customer, customer_id=user_id)
        cart = ShoppingCart.objects.get(customer=customer)
        cart_items = CartItem.objects.filter(cart=cart)

        if not cart_items.exists():
            return JsonResponse({"error": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        # Create an order and update stock levels
        order = Order.objects.create(customer=customer, status='Processing')
        order_items = []

        for item in cart_items:
            if item.product.stock < item.quantity:
                return JsonResponse({"error": f"Insufficient stock for {item.product.model}"}, status=400)

            # Decrease stock
            item.product.stock -= item.quantity
            item.product.save()

            # Add to order
            order_items.append(OrderItem(order=order, product=item.product, quantity=item.quantity, price=item.product.price))

        # Save all order items at once
        OrderItem.objects.bulk_create(order_items)

        # Clear the cart
        cart_items.delete()

        return JsonResponse({"message": "Order placed successfully.", "order_id": order.id}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['GET', 'PUT'])
def order_status(request, order_id):
    """Get or update the status of an order."""
    try:
        order = get_object_or_404(Order, pk=order_id)

        if request.method == 'GET':
            return JsonResponse({"status": order.status}, status=200)

        if request.method == 'PUT':
            new_status = request.data.get('status')
            if new_status not in ['Processing', 'In-Transit', 'Delivered']:
                return JsonResponse({"error": "Invalid status."}, status=400)

            order.status = new_status
            order.save()
            return JsonResponse({"message": "Order status updated successfully."}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
