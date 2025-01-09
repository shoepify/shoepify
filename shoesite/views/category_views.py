from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from shoesite.models import  Product
from django.forms.models import model_to_dict
import json
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from shoesite.models import Category
from django.core.exceptions import ValidationError


@api_view(['POST'])
@permission_classes([AllowAny])
def add_category(request):
    name = request.data.get('name')
    description = request.data.get('description', 'No description available')
    if Category.objects.filter(name=name).exists():
        return Response({"error": "Category with this name already exists."}, status=status.HTTP_400_BAD_REQUEST)
    category = Category.objects.create(name=name, description=description)
    return Response({"message": "Category created successfully.", "id": category.id}, status=status.HTTP_201_CREATED)

@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_category(request, name):
    try:
        category = Category.objects.get(name=name)
        category.delete()
        return Response({"message": "Category deleted successfully."}, status=status.HTTP_200_OK)
    except Category.DoesNotExist:
        return Response({"error": "Category not found."}, status=status.HTTP_404_NOT_FOUND)
    except ValidationError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_category(request, name):
    try:
        # Fetch the category by ID
        category = Category.objects.get(name=name)

        # Fetch all products related to this category
        products = category.products.all()

        # Create a list of product details to return in the response
        product_data = [
            {
                "product_id": product.product_id,
                "model": product.model,
                "serial_number": product.serial_number,
                "stock": product.stock,
                "price": str(product.price),  # Convert Decimal to string for the response
                "description": product.description,
            }
            for product in products
        ]

        # Return the category details along with its products
        return Response({
            "category": {
                "id": category.id,
                "name": category.name,
                "description": category.description,
            },
            "products": product_data
        }, status=status.HTTP_200_OK)

    except Category.DoesNotExist:
        return Response({"error": "Category not found."},status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_categories(request):
    try:
        # Fetch all categories from the database
        categories = Category.objects.all()

        # Create a list of category names and their corresponding IDs
        category_data = [
            {
                "id": category.id,
                "name": category.name
            }
            for category in categories
        ]

        # Return the list of categories
        return Response({
            "categories": category_data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

'''
@csrf_exempt
def add_category(request, *args, **kwargs):
    try:
        data = json.loads(request.body)
        name = data.get('name')
        description = data.get('description', 'No description available')

        if not name:
            return JsonResponse({'error': 'Name is required'}, status=400)

        # Create or get the category
        category, created = Category.objects.get_or_create(
            name=name,
            defaults={'description': description}
        )

        if not created:
            return JsonResponse({'error': 'Category with this name already exists'}, status=400)

        return JsonResponse(
            {'message': 'Category added successfully', 'category': {'name': category.name, 'description': category.description}},
            status=201
        )
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def remove_category(request, category_name, *args, **kwargs):
    try:
        # Retrieve the category by name
        category = Category.objects.get(name=category_name)

        # Check if the category has associated products
        products = Product.objects.filter(category=category)
        if products.exists():
            # Return an error if products exist in the category
            return JsonResponse({'error': 'Category has associated products. Remove the products first.'}, status=400)

        # Delete the category itself
        category.delete()
        return JsonResponse({'message': 'Category removed successfully'}, status=200)
    except Category.DoesNotExist:
        return JsonResponse({'error': 'Category not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

'''