from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from shoesite.models import SalesManager
from shoesite.serializers import SalesManagerSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password


# generate tokens
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    refresh['email'] = user.email
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


# sign up 
@api_view(['POST'])
def signup_sales_manager(request):
    if request.method == 'POST':
        serializer = SalesManagerSerializer(data=request.data)
        if serializer.is_valid():
            # Ensure password is hashed before saving
            password = request.data.get('password')
            if password:
                request.data['password'] = make_password(password)

            sales_manager = serializer.save()

            # Generate tokens after successfully saving the user
            tokens = get_tokens_for_user(sales_manager)

            return Response({
                'message': 'Sales Manager created successfully',
                'manager_id': sales_manager.manager_id,
                'tokens': tokens  # Include tokens in the response
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# login
@api_view(['POST'])
def login_sales_manager(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'error': 'Please provide both email and password'},
                         status=status.HTTP_400_BAD_REQUEST)

    try:
        user = SalesManager.objects.get(email=email)
    except SalesManager.DoesNotExist:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_404_NOT_FOUND)

    if not check_password(password, user.password):
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_404_NOT_FOUND)

    tokens = get_tokens_for_user(user)
    return Response({
        'tokens': tokens,
        'user': SalesManagerSerializer(user).data
    })
