# comment_views.py
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from shoesite.models import  Comment, Product, Customer, OrderItem
import json
from django.db.models import Q  # Add this to enable complex query filtering


from shoesite.models import Comment
#from .serializers import CommentSerializer


@csrf_exempt
def add_comment(request, product_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        customer_id = data.get('customer_id')
        comment_text = data.get('comment')
        
        # Check if the customer exists
        if not Customer.objects.filter(customer_id=customer_id).exists():
            return JsonResponse({"error": "Invalid customer ID."}, status=400)
        
        # Check if the customer has purchased the product
        has_purchased = OrderItem.objects.filter(order__customer_id=customer_id, product__product_id=product_id).exists()
        
        if not has_purchased:
            return JsonResponse({"error": "You cannot give comment before buying it."}, status=403)
        
        # Check if the customer has already commented on this product
        if Comment.objects.filter(customer_id=customer_id, product_id=product_id).exists():
            return JsonResponse({"error": "You have already commented on this product."}, status=400)
        
        # If purchased, save the comment
        comment = Comment.objects.create(
            product_id=product_id,
            customer_id=customer_id,
            comment=comment_text,
            approval_status='Pending'  # Waiting for admin approval
        )
        
        return JsonResponse({"message": "Your comment is waiting for approval.", "comment_id": comment.comment_id}, status=201)
    
    return JsonResponse({"error": "Invalid request."}, status=400)

def get_comments(request, product_id):
    if request.method == 'GET':
        comments = Comment.objects.filter(product_id=product_id)
        #If we want just the approveed ones use this
        #comments = Comment.objects.filter(product_id=product_id, approval_status='Approved')
        comments_data = [
            {
                "comment_id": comment.comment_id,
                "customer_id": comment.customer.customer_id,
                "comment": comment.comment,
                "approval_status": comment.approval_status,
            }
            for comment in comments
        ]
        
        return JsonResponse({"comments": comments_data}, status=200)
    
    return JsonResponse({"error": "Invalid request."}, status=400)

def delete_comment(request, product_id, comment_id):
    if request.method == 'DELETE':
        try:
            # Get the comment for the given product and comment_id
            comment = Comment.objects.get(comment_id=comment_id, product__product_id=product_id)
            
            # Parse the JSON data from the body of the DELETE request
            data = json.loads(request.body)  # Request body contains the customer_id in JSON format
            
            customer_id = data.get('customer_id')

            # Check if the customer is the one who made the comment
            if str(comment.customer.customer_id) != customer_id:
                return JsonResponse({'error': 'You can only delete your own comments.'}, status=403)

            # Proceed to delete the comment
            comment.delete()

            return JsonResponse({}, status=204)  # No content on successful deletion

        except Comment.DoesNotExist:
            return JsonResponse({'error': 'Comment not found.'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)