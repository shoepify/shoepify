from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from shoesite.models import Category, Product
from django.forms.models import model_to_dict
import json
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.permissions import AllowAny


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

