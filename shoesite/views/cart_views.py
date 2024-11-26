# views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from shoesite.models import Customer, Guest, ShoppingCart, CartItem, Product, Order, OrderItem, Invoice, Delivery
from shoesite.views.invoice_views import create_and_send_invoice, view_invoice
from shoesite.views.confirm_payment import confirm_payment # 
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
#command for merge
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


from django.test.client import RequestFactory  # Import RequestFactory to simulate requests




@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def start_order(request, user_id):
    """
    Start the order process for the items in the user's shopping cart.
    """
    try:
        # Check if the user is a customer
        try:
            customer = Customer.objects.get(customer_id=user_id)
            customer_content_type = ContentType.objects.get_for_model(Customer)
            cart = ShoppingCart.objects.filter(
                owner_content_type=customer_content_type,
                owner_object_id=customer.id
            ).first()
        except Customer.DoesNotExist:
            # Specific error handling for non-existent customer
            return JsonResponse({"error": "Customer does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user is a guest if not a customer
        if not cart:
            try:
                guest = get_object_or_404(Guest, guest_id=user_id)
                guest_content_type = ContentType.objects.get_for_model(Guest)
                cart = ShoppingCart.objects.filter(
                    owner_content_type=guest_content_type,
                    owner_object_id=guest.guest_id
                ).first()
            except Guest.DoesNotExist:
                return JsonResponse({"error": "Guest does not exist."}, status=status.HTTP_404_NOT_FOUND)

        if not cart:
            return JsonResponse({"error": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)

        cart_items = CartItem.objects.filter(cart=cart)

        if not cart_items.exists():
            return JsonResponse({"error": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        # If no errors, signal the frontend that the order process can proceed
        return JsonResponse({"success": True, "message": "Order process can proceed."}, status=status.HTTP_200_OK)

    except Exception as e:
        # Catch any unexpected errors
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])  # Allows unauthenticated access
def confirm_payment(request, user_id):
    """
    Confirm payment, create an order based on the user's cart and cart items,
    generate an invoice, and initiate delivery.
    """
    try:
        # Determine if the user is a customer or guest
        try:
            customer = Customer.objects.get(customer_id=user_id)
            customer_content_type = ContentType.objects.get_for_model(Customer)
            cart = ShoppingCart.objects.filter(
                owner_content_type=customer_content_type,
                owner_object_id=customer.id
            ).first()

        except Customer.DoesNotExist:
            guest = get_object_or_404(Guest, guest_id=user_id)
            cart = ShoppingCart.objects.filter(owner_object_id=guest.guest_id).first()

        if not cart:
            return JsonResponse({"error": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)

        cart_items = CartItem.objects.filter(cart=cart)

        if not cart_items.exists():
            return JsonResponse({"error": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        # Create an order
        order = Order.objects.create(
            customer=customer if 'customer' in locals() else None,
            order_date=timezone.now(),
            total_amount=0,  # Will calculate after adding items
            discount_applied=0,
            payment_status="Pending",
            status="Processing"  # Track order status
        )

        # Process cart items and calculate total amount
        total_amount = 0
        order_items = []

        for item in cart_items:
            if item.product.stock < item.quantity:
                return JsonResponse({"error": f"Insufficient stock for {item.product.model}"}, status=status.HTTP_400_BAD_REQUEST)

            # Reduce product stock
            item.product.stock -= item.quantity
            item.product.save()

            # Add order item
            total_amount += item.quantity * item.product.price
            order_items.append(OrderItem(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price_per_item=item.product.price
            ))

        # Save all order items and update the total amount
        OrderItem.objects.bulk_create(order_items)
        order.total_amount = total_amount
        order.payment_status = "Paid"  # Mark as paid after successful payment confirmation
        order.status = "Processing"
        order.save()

        # Clear the shopping cart
        cart_items.delete()

        # Generate and send an invoice
        factory = RequestFactory()
        invoice_request = factory.get(f'/create_invoice/{order.id}/')  # Order ID used here
        invoice_response = create_and_send_invoice(invoice_request, order.id)
        if invoice_response.status_code != 200:
            return JsonResponse({"error": "Invoice generation failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Display the invoice PDF
        invoice_pdf_response = view_invoice(invoice_request, order.id)
        if invoice_pdf_response.status_code != 200:
            return JsonResponse({"error": "Failed to display the invoice."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Initiate delivery process
        delivery_request = factory.post(f'/complete_delivery/{order.id}/')  # Order ID used here
        delivery_response = complete_delivery(delivery_request, order.id)
        if delivery_response.status_code != 200:
            return JsonResponse({"error": "Delivery process failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Respond with success
        return JsonResponse({
            "message": "Order placed successfully. Invoice generated and sent. Delivery initiated.",
            "order_id": order.id
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def complete_delivery(request, order_id):
    """
    Creates a delivery entry for the given order.
    """
    try:
        # Fetch the order
        order = get_object_or_404(Order, id=order_id)

        # Determine the delivery address
        if order.customer and order.customer.home_address:
            delivery_address = order.customer.home_address
        else:
            return JsonResponse({"error": "Customer address is missing for delivery."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the Delivery object
        delivery = Delivery.objects.create(
            order=order,
            delivery_status="Processing",
            delivery_address=delivery_address,
            delivery_date=timezone.now().date()  # Use today's date
        )

        return JsonResponse({
            "message": "Delivery created successfully.",
            "delivery_id": delivery.delivery_id,
            "order_id": order.id,
            "delivery_status": delivery.delivery_status,
            "delivery_address": delivery.delivery_address,
            "delivery_date": delivery.delivery_date.strftime('%Y-%m-%d'),
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)