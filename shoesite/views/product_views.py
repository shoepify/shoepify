# views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
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
        return JsonResponse({
            **serializer.data,
            "stock": product.stock  # Include stock information
        }, status=status.HTTP_200_OK)


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
    
#Search and Sort Products
def search_products(request):
    query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', '')  # Sort field (price or popularity_score)
    sort_order = request.GET.get('order', 'asc')  # Sort order (asc or desc)

    if not query:
        return JsonResponse({"error": "Search query parameter 'q' is required"}, status=400)

    # Perform case-insensitive search on 'model' and 'description'
    products = Product.objects.filter(
        Q(model__icontains=query) | Q(description__icontains=query)
    )

    # Handle sorting
    if sort_by:
        if sort_by not in ['price', 'popularity_score']:
            return JsonResponse({"error": f"Invalid sort field '{sort_by}'. Use 'price' or 'popularity_score'."},
                                status=400)
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'
        products = products.order_by(sort_by)

    # Serialize the results with stock information
    serializer = ProductSerializer(products, many=True)
    product_data = serializer.data

    # Add a flag indicating whether each product is in stock
    for product in product_data:
        product_obj = products.get(product_id=product['product_id'])
        product['in_stock'] = product_obj.stock > 0

    return JsonResponse(product_data, safe=False, status=200)
