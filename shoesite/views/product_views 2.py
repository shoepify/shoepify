# views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from shoesite import models
from shoesite.models import  Product
import json
from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import status
from django.db.models import Q  # Add this to enable complex query filtering



from shoesite.serializers import CustomerSerializer, WishlistSerializer, RefundSerializer, WishlistItemSerializer, ShoppingCartSerializer, CartItemSerializer, ProductSerializer

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


#Search Product







@csrf_exempt
def search_products(request, search_input):
    try:
        # Perform a case-insensitive substring search in both model and description
        products = Product.objects.filter(
            Q(model__icontains=search_input) | Q(description__icontains=search_input)
        )

        # Check if there are no matching products
        if not products.exists():
            return JsonResponse({"message": "No products found matching the search criteria."}, status=404)

        # Manually convert the products to a list of dictionaries
        products_list = [
            {
                "product_id": product.product_id,
                "model": product.model,
                "serial_number": product.serial_number,
                "stock": product.stock,
                "inventory_to_stock": product.inventory_to_stock,
                "warranty_status": product.warranty_status,
                "distributor_info": product.distributor_info,
                "description": product.description,
                "base_price": float(product.base_price),
                "price": float(product.price),
                "popularity_score": float(product.popularity_score),
                
            }
            for product in products
        ]

        return JsonResponse({"products": products_list}, safe=False)

    except Exception as e:
        # Return the error message as a response to help with debugging
        return JsonResponse({"error": str(e)}, status=500)
