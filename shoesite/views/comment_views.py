# comment_views.py
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from shoesite.models import  Comment, Product, Customer, OrderItem, ProductManager
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
        
        # returns comment id and comment itself
        return JsonResponse({"message": "Your comment is waiting for approval.", "comment_id": comment.comment_id, "comment": comment.comment}, status=201)
    
    return JsonResponse({"error": "Invalid request."}, status=400)


def get_comments(request, product_id):
    if request.method == 'GET':
        # Check if the 'approved' query parameter is passed
        approved_only = request.GET.get('approved', None)

        # Build the base query
        comments_query = Comment.objects.filter(product_id=product_id)
        
        # If the 'approved' query parameter is set to true, filter by approval_status
        if approved_only == 'true':
            comments_query = comments_query.filter(approval_status='Approved')

        # Fetch the comments
        comments = comments_query
        
        # If no comments are found, return a message
        if not comments.exists():
            return JsonResponse({"message": "No comments found for this product."}, status=404)

        # Prepare the response data
        comments_data = [
            {
                "comment_id": comment.comment_id,
                "customer_id": comment.customer.customer_id,
                "name": comment.customer.name,
                "comment": comment.comment,
                "approval_status": comment.approval_status,
            }
            for comment in comments
        ]
        
        return JsonResponse({"comments": comments_data}, status=200)
    
    return JsonResponse({"error": "Invalid request."}, status=400)
@csrf_exempt
def delete_comment(request, product_id, comment_id):
    if request.method == 'DELETE':
        try:
            # Get the comment for the given product and comment_id
            comment = Comment.objects.get(comment_id=comment_id, product__product_id=product_id)
            
            # Parse the JSON data from the body of the DELETE request
            data = json.loads(request.body)  # Request body contains the customer_id in JSON format
            
            customer_id = data.get('customer_id')

            # Ensure customer_id is an integer before comparing
            if int(comment.customer.customer_id) != int(customer_id):
                return JsonResponse({'error': 'You can only delete your own comments.'}, status=403)

            # Proceed to delete the comment
            comment.delete()

            return JsonResponse({}, status=204)  # No content on successful deletion

        except Comment.DoesNotExist:
            return JsonResponse({'error': 'Comment not found.'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)
        except ValueError:
            return JsonResponse({'error': 'Invalid customer_id. It should be an integer.'}, status=400)
        
def get_pending_comments(request):

# Fetch pending comments from the database
    comments = Comment.objects.filter(approval_status='Pending')
    comments_data = [
        {
            "comment_id": comment.id,
            "customer_name": comment.customer.name,
            "comment": comment.comment,
        }
        for comment in comments
    ]
    return JsonResponse({"comments": comments_data}, status=200)

    """
    if request.user.is_authenticated and isinstance(request.user, ProductManager):
        # Fetch pending comments from the database
        comments = Comment.objects.filter(approval_status='Pending')
        comments_data = [
            {
                "comment_id": comment.id,
                "customer_name": comment.customer.name,
                "comment": comment.comment,
            }
            for comment in comments
        ]
        return JsonResponse({"comments": comments_data}, status=200)
    else:
        return JsonResponse({"error": "Unauthorized access."}, status=403)
     """

@csrf_exempt
def update_approval(request, comment_id):
    if request.method == 'PUT':  # Only allow PUT method for approval
        try:
            # Ensure the comment_id is an integer
            comment_id = int(comment_id)

            # Fetch the comment to be approved using 'comment_id' instead of 'id'
            comment = get_object_or_404(Comment, comment_id=comment_id)  # Correct field name here

            # Check the current approval status
            if comment.approval_status == 'Pending':
                # Approve the comment
                comment.approval_status = 'Approved'
                comment.save()
                return JsonResponse({"message": "Comment approved successfully."}, status=200)
            else:
                return JsonResponse({"error": "Comment is already approved or rejected."}, status=400)
        except ValueError:
            return JsonResponse({"error": "Invalid comment_id, must be an integer."}, status=400)
    
    return JsonResponse({"error": "Invalid request method. Please use PUT."}, status=405)  # Handle incorrect methods
    """
    if request.user.is_authenticated and isinstance(request.user, ProductManager):
        try:
            # Ensure the comment_id is an integer
            comment_id = int(comment_id)

            # Fetch the comment to be approved
            comment = get_object_or_404(Comment, id=comment_id)
            
            # Check the current approval status
            if comment.approval_status == 'Pending':
                # Approve the comment
                comment.approval_status = 'Approved'
                comment.save()
                return JsonResponse({"message": "Comment approved successfully."}, status=200)
            else:
                return JsonResponse({"error": "Comment is already approved or rejected."}, status=400)
        except ValueError:
            return JsonResponse({"error": "Invalid comment_id, must be an integer."}, status=400)
    else:
        return JsonResponse({"error": "Unauthorized access."}, status=403)
    """