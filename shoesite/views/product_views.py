# views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from shoesite.models import  Product
import json
import re
from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import status
from django.db.models import Q  # Add this to enable complex query filtering
from django.http import JsonResponse
from django.views import View
from django.core.exceptions import ValidationError
from django.db import transaction
from shoesite.models import Product, Category, Discount
from decimal import Decimal
from django.shortcuts import get_object_or_404
from shoesite.serializers import CustomerSerializer, WishlistSerializer, RefundSerializer, WishlistItemSerializer, ShoppingCartSerializer, CartItemSerializer, ProductSerializer
from rest_framework import status
from django.http import JsonResponse,Http404
# PRODUCT
# List all products
@csrf_exempt
def list_products(request):
    if request.method == 'GET':
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return JsonResponse(serializer.data, safe=False, status=200)
    

# Create a new products

@csrf_exempt
def ProductCreate(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests are allowed."}, status=405)

    try:
        import json
        from django.db import transaction

        # Parse JSON data from the request body
        data = json.loads(request.body)

        # Validate required fields
        required_fields = ["model", "serial_number", "stock", "base_price", "cost"]
        for field in required_fields:
            if field not in data:
                return JsonResponse({"error": f"'{field}' is required."}, status=400)

        # Handle category
        category_data = data.get("category")
        category = None
        if category_data:
            category, created = Category.objects.get_or_create(
                name=category_data.get("name"),
                defaults={"description": category_data.get("description", "No description available")},
            )

        # Handle discount
        discount_data = data.get("discount")
        discount = None
        if discount_data:
            discount_rate = Decimal(discount_data.get("discount_rate", "0.00"))  # Convert to Decimal
            discount, created = Discount.objects.get_or_create(
                discount_name=discount_data.get("discount_name"),
                defaults={
                    "discount_rate": discount_rate,
                    "start_date": discount_data.get("start_date"),
                    "end_date": discount_data.get("end_date"),
                },
            )
        
        base_price = Decimal(data["base_price"])
        # Convert price and cost to Decimal
        #price = Decimal(data["price"])
        cost = Decimal(data["cost"])
        #profit = price - cost  # Calculate profit

        # Create the product
        with transaction.atomic():
            product = Product.objects.create(
                model=data["model"],
                serial_number=data["serial_number"],
                stock=int(data.get("stock", 0)),  # Convert to int
                warranty_status=data.get("warranty_status", "Unknown"),
                distributor_info=data.get("distributor_info", "Unknown"),
                description=data.get("description", "No description available"),
                category=category,
                base_price=Decimal(data.get("base_price", "0.0")),  # Convert to Decimal
                price=base_price,
                cost=cost,
                #profit=profit,
                popularity_score=Decimal(data.get("popularity_score", "0.0")),  # Convert to Decimal
                avg_rating=Decimal(data.get("avg_rating", "0.0")),  # Convert to Decimal
                image_name=data.get("image_name", None),
                discount=discount,
            )

        # Return a success response
        return JsonResponse({"message": "Product created successfully", "product_id": product.product_id}, status=201)

    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data."}, status=400)
    except Exception as e:
        # Log error (not shown to client for security reasons)
        return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)




# Retrieve a product by ID
@csrf_exempt
def get_product(request, product_id):
    if request.method == 'GET':
        try:
            # Try to get the product by its ID
            product = get_object_or_404(Product, product_id=product_id)
            # Serialize the product data
            serializer = ProductSerializer(product)
            return JsonResponse({
                **serializer.data,
                "stock": product.stock  # Include stock information
            }, status=status.HTTP_200_OK)
        except Http404:
            return JsonResponse({
                "error": "Product not found"
            }, status=status.HTTP_404_NOT_FOUND)


@csrf_exempt
def update_base_price(request, product_id):
    if request.method == 'PUT':
        try:
            # Retrieve the product object
            product = get_object_or_404(Product, product_id=product_id)

            # Parse the request data
            data = json.loads(request.body)
            print(f"Received data: {data}")

            # Ensure 'base_price' is present in the request
            if 'base_price' not in data:
                return JsonResponse(
                    {'error': "The 'base_price' field is required."},
                    status=400
                )

            # Convert base_price to Decimal
            try:
                base_price = Decimal(data['base_price'])
                if base_price <= 0:
                    raise ValueError("Base price must be a positive number.")
            except (ValueError, TypeError, Decimal.InvalidOperation) as e:
                return JsonResponse(
                    {'error': f"Invalid base_price value: {str(e)}"},
                    status=400
                )

            # Update the product's base_price
            product.base_price = base_price
            product.save()
            print(f"Updated base_price for product {product_id} to {base_price}")

            return JsonResponse(
                {'message': 'Base price updated successfully', 'base_price': str(base_price)},
                status=200
            )

        except Exception as e:
            print(f"Error updating base_price: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse(
        {'error': 'Method not allowed. Use PUT for updating base_price.'},
        status=405
    )

# Update an existing product
@csrf_exempt  # Consider removing this if not needed
def update_product(request, product_id):
    if request.method == 'PUT':
        try:
            # Retrieve the product object
            product = get_object_or_404(Product, product_id=product_id)
            
            # Parse the request data
            data = json.loads(request.body)
            print(f"Updating product {product_id} with data: {data}")  # Debugging output

            # Allow the 'stock' field to be updated
            serializer = ProductSerializer(product, data=data, partial=True)  # Using partial=True to allow partial updates

            # Validate and save the updated product data
            if serializer.is_valid():
                serializer.save()
                return JsonResponse({'message': 'Product updated successfully'}, status=status.HTTP_200_OK)

            # If serializer is not valid, return errors
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

"""
#Search Product
def search_products(request):
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse({"error": "Search query parameter 'q' is required"}, status=400)

    # Perform case-insensitive search on 'model' and 'description'
    products = Product.objects.filter(
        Q(model__icontains=query) | Q(description__icontains=query)
    )

    # Serialize the results
    serializer = ProductSerializer(products, many=True)
    return JsonResponse(serializer.data, safe=False, status=200)
    """


def search_products(request):
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse({"error": "Search query parameter 'q' is required"}, status=400)

    # Split the query by spaces
    words = query.split()

    # Initialize an empty Q object to build the search query
    product_filter = Q()

    for word in words:
        # Use a case-insensitive regex to match words starting with the query
        product_filter &= (
            Q(model__iregex=r'\b' + re.escape(word)) | Q(description__iregex=r'\b' + re.escape(word))
        )

    # Perform the search using the combined filter
    products = Product.objects.filter(product_filter)

    # Serialize the results
    serializer = ProductSerializer(products, many=True)
    return JsonResponse(serializer.data, safe=False, status=200)