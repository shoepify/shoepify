# views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from shoesite.models import Customer, Guest, ShoppingCart, CartItem, Product, Order, OrderItem, Invoice, Delivery
from shoesite.views.invoice_views import create_and_send_invoice
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
from django.urls import reverse
import requests



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


from django.test.client import RequestFactory  # Import RequestFactory to simulate requests

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def place_order(request, user_id):
    """Place an order for the items in the user's shopping cart, confirm payment, and handle delivery."""
    try:
        # Determine if the user is a customer or guest and retrieve their cart
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

        # Create an order and add items to it
        order = Order.objects.create(
            customer=customer if 'customer' in locals() else None,
            order_date=timezone.now(),
            total_amount=0,  # Will calculate after adding items
            discount_applied=0,
            payment_status="Paid",
            status="Processing"  # New field to track order status
        )

        total_amount = 0
        order_items = []

        for item in cart_items:
            if item.product.stock < item.quantity:
                return JsonResponse({"error": f"Insufficient stock for {item.product.model}"}, status=status.HTTP_400_BAD_REQUEST)

            # Reduce product stock
            item.product.stock -= item.quantity
            item.product.save()

            # Calculate total and prepare order items
            total_amount += item.quantity * item.product.price
            order_items.append(OrderItem(order=order, product=item.product, quantity=item.quantity, price_per_item=item.product.price))

        # Save all order items and update total amount in the order
        OrderItem.objects.bulk_create(order_items)
        order.total_amount = total_amount

        # Confirm Payment
        factory = RequestFactory()
        payment_request = factory.post('/confirm_payment/', {'payment_status': 'Success'})
        payment_response = confirm_payment(payment_request, order.order_id)  # Use order.order_id here
        if payment_response.status_code != 200:
            payment_response.render()  # Ensure the response is rendered
            print(f"Debug: Payment Response - {payment_response.content}")  # Debugging
            return JsonResponse({"error": "Payment failed. Order not completed."}, status=status.HTTP_400_BAD_REQUEST)

        # Save the order
        order.save()

        # Clear the shopping cart
        cart_items.delete()

        # Create and Send Invoice by making a request to the corresponding URL
        invoice_url = reverse('create_and_send_invoice', kwargs={'order_id': order.order_id})

        # Use the RequestFactory to simulate a GET request to the invoice creation view
        invoice_request = factory.get(invoice_url)  # Use the GET method here
        invoice_response = create_and_send_invoice(invoice_request, order.order_id)
        if invoice_response.status_code != 200:
            return JsonResponse({"error": "Invoice generation failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        print("invoice created and sent")

        invoice_id = Invoice.objects.get(order=order).invoice_id  # Adjust based on how you store the invoice
        print(invoice_id)

        # Move to Delivery Phase
        print("delivery phase")
        delivery_request = factory.post(f'/complete_delivery/{order.order_id}/')
        complete_delivery_response = complete_delivery(delivery_request, order.order_id)
        print("delivery process yazdırılacak")
        if complete_delivery_response.status_code != 201:
            return JsonResponse({"error": "Delivery process failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        print("delivery done")
        
        return JsonResponse({
            "message": "Order placed successfully. Invoice generated and sent. Delivery initiated.",
            "order_id": order.order_id, # Return the correct order ID
            "invoice_id": invoice_id,  # Return the generated invoice ID
            "total amount": order.total_amount
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def complete_delivery(request, order_id):    
    try:
        # Fetch the order
        order = get_object_or_404(Order, pk=order_id)

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
        print("delivery created")
        print(delivery.delivery_status)

        return JsonResponse({
            "message": "Delivery created successfully.",
            "delivery_id": delivery.delivery_id,
            "delivery_status": delivery.delivery_status,
            "delivery_address": delivery.delivery_address
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def get_orders_by_customer(request, customer_id):
    """
    Get all orders placed by a specific customer along with their order items using customer_id.
    """
    try:
        # Retrieve the customer by customer_id or return a 404 if not found
        customer = get_object_or_404(Customer, customer_id=customer_id)
        
        # Retrieve all orders for the customer
        orders = Order.objects.filter(customer=customer)
        
        if not orders.exists():
            return JsonResponse({"error": "No orders found for this customer."}, status=status.HTTP_404_NOT_FOUND)
        
        # Serialize the orders with their respective order items
        orders_data = []
        for order in orders:
            # Retrieve all order items for the current order
            order_items = OrderItem.objects.filter(order=order).select_related('product')
            order_items_data = [
                {
                    "order_item_id": item.order_item_id,
                    "product_id": item.product.product_id,
                    "product_model": item.product.model,
                    "quantity": item.quantity,
                    "price_per_item": item.price_per_item,
                    "refunded": item.refunded,
                }
                for item in order_items
            ]
            orders_data.append({
                "order_id": order.order_id,
                "order_date": order.order_date,
                "total_amount": order.total_amount,
                "discount_applied": order.discount_applied,
                "payment_status": order.payment_status,
                "status": order.status,
                "order_items": order_items_data,  # Include order items here
            })
        
        return JsonResponse({"orders": orders_data}, status=status.HTTP_200_OK)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def check_cart(request, user_id):
    """
    Check the validity of the cart: existence, non-emptiness, and sufficient stock.
    """
    try:
        # Determine if the user is a customer or guest and retrieve their cart
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

        # Check stock for each item in the cart
        for item in cart_items:
            if item.product.stock < item.quantity:
                return JsonResponse({"error": f"Insufficient stock for {item.product.model}"}, status=status.HTTP_400_BAD_REQUEST)

        # If all checks pass, return success
        return JsonResponse({"message": "Cart is valid."}, status=status.HTTP_200_OK)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
def update_order_status(request, order_id):
    """
    Update the status of an order:
    - If 'Processing', change to 'In Transit'.
    - If 'In Transit', change to 'Delivered'.
    - Otherwise, do nothing.
    """
    if request.method == 'PUT':  # Only allow PUT method for status updates
        try:
            # Ensure the order_id is an integer
            order_id = int(order_id)

            # Fetch the order using 'order_id'
            order = get_object_or_404(Order, pk=order_id)

            # Update the status based on current value
            if order.status == 'Processing':
                order.status = 'In Transit'
                order.save()
                return JsonResponse({"message": f"Order #{order_id} status updated to 'In Transit'."}, status=200)
            elif order.status == 'In Transit':
                order.status = 'Delivered'
                order.save()
                return JsonResponse({"message": f"Order #{order_id} status updated to 'Delivered'."}, status=200)
            else:
                return JsonResponse({
                    "error": f"Order status is '{order.status}', no update performed."
                }, status=400)
        except ValueError:
            return JsonResponse({"error": "Invalid order_id, must be an integer."}, status=400)

    return JsonResponse({"error": "Invalid request method. Please use PUT."}, status=405)  # Handle incorrect methods


def get_all_orders(request):
    """
    Fetch all orders from the database and return their details.
    """
    try:
        # Fetch all orders
        orders = Order.objects.all()

        # Structure the data for response
        orders_data = [
            {
                "order_id": order.order_id,
                "customer_name": order.customer.name if order.customer else "Guest",
                "order_date": order.order_date.strftime("%Y-%m-%d"),
                "total_amount": order.total_amount,
                "status": order.status,
            }
            for order in orders
        ]

        return JsonResponse({"orders": orders_data}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def cancel_order(request, order_id):
    """
    Cancel an existing order if it has not been delivered yet.
    This will increase the stock of ordered items and refund the customer.
    """
    try:
        # Fetch the order by ID
        order = Order.objects.get(order_id=order_id)

        # Check if the order is already delivered
        if order.status == "Delivered":
            return JsonResponse({"error": "Order has already been delivered and cannot be cancelled."}, status=400)

        # Fetch all order items related to this order
        order_items = OrderItem.objects.filter(order=order)

        # Increase the stock of each ordered item
        for item in order_items:
            product = item.product
            product.stock += item.quantity
            product.save()

        # Add the total order amount back to the customer's balance
        customer = order.customer
        customer.balance += order.total_amount
        customer.save()

        # Change the order status to cancelled
        order.status = "Cancelled"
        order.payment_status = "Cancelled"
        order.save()

        # Update the delivery status to 'Cancelled'
        delivery = Delivery.objects.filter(order=order).first()
        if delivery:
            delivery.delivery_status = "Cancelled"
            delivery.save()

        return JsonResponse({"message": "Order successfully cancelled, stock and balance updated."}, status=200)

    except Order.DoesNotExist:
        return JsonResponse({"error": "Order not found."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def get_order_items_by_order(request, order_id):
    """
    Get all OrderItems for a specific Order using the order_id.
    """
    try:
        # Retrieve the order by order_id or return a 404 if not found
        order = get_object_or_404(Order, order_id=order_id)

        # Retrieve all OrderItems for the given order
        order_items = OrderItem.objects.filter(order=order).select_related('product')

        if not order_items.exists():
            return JsonResponse({"error": "No order items found for this order."}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the OrderItems with details
        order_items_data = [
            {
                "order_item_id": item.order_item_id,
                "product_id": item.product.product_id,
                "product_model": item.product.model,
                "quantity": item.quantity,
                "price_per_item": item.price_per_item,
                "refunded": item.refunded,
            }
            for item in order_items
        ]

        # Include order details in the response
        response_data = {
            "order_id": order.order_id,
            "order_date": order.order_date,
            "total_amount": order.total_amount,
            "discount_applied": order.discount_applied,
            "payment_status": order.payment_status,
            "status": order.status,
            "order_items": order_items_data,
        }

        return JsonResponse(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
