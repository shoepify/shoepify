# views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Customer, OrderItem, Refund, Product, Wishlist, WishlistItem
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

def get_customer(request, customer_id):
    try:
        customer = Customer.objects.get(customer_id=customer_id)
        data = {
            'customer_id': customer.customer_id,
            'password': customer.password,
            'name': customer.name,
            'tax_id': customer.tax_id,
            'email': customer.email,
            'home_address': customer.home_address,
            'billing_address': customer.billing_address,
            'phone_number': customer.phone_number,
        }
        return JsonResponse(data)
    except Customer.DoesNotExist:
        return JsonResponse({'error': 'Customer not found'}, status=404)


@csrf_exempt
def create_customer(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Parse JSON payload

            # Extract data from  request
            customer_id = data.get('customer_id')
            name = data.get('name')
            tax_id = data.get('tax_id')
            email = data.get('email')
            password = data.get('password')
            home_address = data.get('home_address')
            billing_address = data.get('billing_address')
            phone_number = data.get('phone_number')

            # Create new customer
            customer = Customer.objects.create(
                customer_id=customer_id,
                name=name,
                tax_id=tax_id,
                email=email,
                password=password,
                home_address=home_address,
                billing_address=billing_address,
                phone_number=phone_number
            )
            
            return JsonResponse({'message': 'Customer created successfully', 'customer_id': customer.customer_id}, status=201)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)



# wishlist related parts

# add wishlist item (from product) to wishlist
def add_to_wishlist(request, customer_id, product_id):
    customer = get_object_or_404(Customer, customer_id=customer_id)
    wishlist = customer.wishlist  # Access the wishlist directly due to OneToOne relationship
    product = get_object_or_404(Product, product_id=product_id)

    # Check if item already exists in wishlist
    if not WishlistItem.objects.filter(wishlist=wishlist, product=product).exists():
        WishlistItem.objects.create(wishlist=wishlist, product=product)
        return JsonResponse({'status': 'Product added to wishlist'}, status=201)
    return JsonResponse({'status': 'Product already in wishlist'}, status=200)

# remove wishlist item from wishlist
def remove_from_wishlist(request, customer_id, product_id):
    customer = get_object_or_404(Customer, customer_id=customer_id)
    wishlist = customer.wishlist
    product = get_object_or_404(Product, product_id=product_id)

    # Remove item from wishlist if it exists
    WishlistItem.objects.filter(wishlist=wishlist, product=product).delete()
    return JsonResponse({'status': 'Product removed from wishlist'}, status=200)

# view the wishlist

def get_wishlist_json(request, customer_id):
    customer = get_object_or_404(Customer, customer_id=customer_id)
    wishlist = Wishlist.objects.filter(customer=customer).first()
    
    if wishlist:
        wishlist_items = wishlist.wishlistitem_set.all()
        items_data = [{'product_id': item.product.product_id, 'model': item.product.model} for item in wishlist_items]
        return JsonResponse({'customer_id': customer.customer_id, 'wishlist_items': items_data})
    else:
        return JsonResponse({'customer_id': customer.customer_id, 'wishlist_items': []})

        
def view_wishlist(request, customer_id):
    customer = get_object_or_404(Customer, customer_id=customer_id)
    wishlist_items = WishlistItem.objects.filter(wishlist=customer.wishlist)
    data = [{'product_id': item.product.product_id, 'model': item.product.model} for item in wishlist_items]
    return JsonResponse({'wishlist': data}, status=200)


# refund request (for customers)
def request_refund(request, order_item_id):
    order_item = get_object_or_404(OrderItem, pk=order_item_id)
    order_date = order_item.order.order_date
    
    # Check if order is eligible for refund (within 30 days)
    if (timezone.now().date() - order_date).days > 30:
        return JsonResponse({'status': 'error', 'message': 'Refund request is past the 30-day period.'})

    # Check if refund request already exists for this order item
    if Refund.objects.filter(order_item=order_item).exists():
        return JsonResponse({'status': 'error', 'message': 'Refund request already exists for this order item.'})
    
    # Create and save refund request
    refund = Refund(order_item=order_item, status='Pending')
    refund.save()

    return JsonResponse({'status': 'success', 'message': 'Refund request submitted successfully.'})

# approve refund (for sales managers)
def approve_refund(request, refund_id):
    refund = get_object_or_404(Refund, pk=refund_id)

    if refund.status != 'Pending':
        return JsonResponse({'status': 'error', 'message': 'Refund request has already been processed.'})

    # Approve and process refund
    refund.approve_refund()  # Calls the approve_refund method in the Refund model

    return JsonResponse({'status': 'success', 'message': 'Refund approved successfully.', 'refunded_amount': refund.refunded_amount})




