# ratings_views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from shoesite.models import Customer, OrderItem, Rating
import json



@csrf_exempt
def add_rating(request, product_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        customer_id = data.get('customer_id')
        rating_value = data.get('rating_value')
        
        # Validate rating value (ensure it's between 1 and 5)
        try:
            rating_value = int(rating_value)
            if rating_value < 1 or rating_value > 5:
                return JsonResponse({"error": "Invalid rating value. Must be between 1 and 5."}, status=400)
        except ValueError:
            return JsonResponse({"error": "Invalid rating value. Must be an integer."}, status=400)
        
        # Check if the customer exists
        customer = Customer.objects.filter(customer_id=customer_id).first()
        if not customer:
            return JsonResponse({"error": "Invalid customer ID."}, status=400)
        
        # Check if the customer has already rated this product
        if Rating.objects.filter(customer_id=customer_id, product_id=product_id).exists():
            return JsonResponse({"error": "You have already rated this product."}, status=400)
        
        # Check if the customer has purchased the product
        has_purchased = OrderItem.objects.filter(order__customer_id=customer_id, product__product_id=product_id).exists()
        
        if not has_purchased:
            return JsonResponse({"error": "You cannot rate a product before buying it."}, status=403)
        
        # Save the rating (no approval status needed for ratings)
        rating = Rating.objects.create(
            product_id=product_id,
            customer_id=customer_id,
            rating_value=rating_value
        )
        
        return JsonResponse({"message": "Your rating has been submitted.", "rating_id": rating.rating_id}, status=201)
    
    return JsonResponse({"error": "Invalid request."}, status=400)

def get_ratings(request, product_id):
    if request.method == 'GET':
        # Retrieve all ratings for the product
        ratings = Rating.objects.filter(product_id=product_id)
        ratings_data = [
            {
                "rating_value": rating.rating_value,
                "customer_id": rating.customer.customer_id,
                # If you have comments for ratings, you can include them here (e.g., for future use)
                "comment": rating.comment if hasattr(rating, 'comment') else None
            }
            for rating in ratings
        ]
        
        return JsonResponse({"ratings": ratings_data}, status=200)
    
    return JsonResponse({"error": "Invalid request."}, status=400)

def delete_rating(request, product_id, rating_id):
    if request.method == 'DELETE':
        try:
            # Get the rating for the given product and rating_id
            rating = Rating.objects.get(rating_id=rating_id, product__product_id=product_id)
            
            # Parse the JSON data from the body of the DELETE request
            data = json.loads(request.body)
            customer_id = data.get('customer_id')

            # Check if the customer is the one who made the rating
            if str(rating.customer.customer_id) != customer_id:
                return JsonResponse({'error': 'You can only delete your own ratings.'}, status=403)

            # Proceed to delete the rating
            rating.delete()

            return JsonResponse({}, status=204)  # No content on successful deletion

        except Rating.DoesNotExist:
            return JsonResponse({'error': 'Rating not found.'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)

# Make sure to define the URL patterns for these new views in your urls.py