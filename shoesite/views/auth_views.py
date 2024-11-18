# login_views.py


from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.http import JsonResponse, HttpResponse
from shoesite.models import Comment, Customer, OrderItem, Refund, Product, Wishlist, WishlistItem, ShoppingCart, CartItem, Rating, SalesManager, ProductManager
import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from shoesite.serializers import CustomerSerializer, UserSerializer 
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password, check_password
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    refresh['email'] = user.email

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
    
@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'error': 'Please provide both email and password'},
                      status=status.HTTP_400_BAD_REQUEST)
    user=User.objects.get(email=email)
    serializer=UserSerializer
    
    '''
    # Check user type based on email domain
    if email.endswith('@sm.com'):
        try:
            user = SalesManager.objects.get(email=email)
            serializer = SalesManagerSerializer
            user_type = 'sales_manager'
        except SalesManager.DoesNotExist:
            return Response({'error': 'Invalid credentials'},
                          status=status.HTTP_404_NOT_FOUND)
    elif email.endswith('@pm.com'):
        try:
            user = ProductManager.objects.get(email=email)
            serializer = ProductManagerSerializer
            user_type = 'product_manager'
        except ProductManager.DoesNotExist:
            return Response({'error': 'Invalid credentials'},
                          status=status.HTTP_404_NOT_FOUND)
    else:
        try:
            user = Customer.objects.get(email=email)
            serializer = CustomerSerializer
            user_type = 'customer'
        except Customer.DoesNotExist:
            return Response({'error': 'Invalid credentials'},
                          status=status.HTTP_404_NOT_FOUND)
    '''
    if not check_password(password, user.password):
        return Response({'error': 'Invalid credentials'},
                      status=status.HTTP_404_NOT_FOUND)

    tokens = get_tokens_for_user(user)
    return Response({
        'tokens': tokens,
        'user': serializer(user).data
    })

@api_view(['POST'])
def signup(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'error': 'Please provide both email and password'},
                      status=status.HTTP_400_BAD_REQUEST)
    model=User
    serializer=UserSerializer(data=request.data)
    '''#Determine user type and serializer based on email domain
    if email.endswith('@sm.com'):
        serializer = SalesManagerSerializer(data=request.data)
        model = SalesManager
        user_type = 'sales_manager'
    elif email.endswith('@pm.com'):
        serializer = ProductManagerSerializer(data=request.data)
        model = ProductManager
        user_type = 'product_manager'
    else:
        serializer = CustomerSerializer(data=request.data)
        model = Customer
        user_type = 'customer'
    '''
    if serializer.is_valid():
        if model.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists'},
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Hash password before saving
        user = serializer.save()
        user.password = make_password(password)
        user.save()

        tokens = get_tokens_for_user(user)
        return Response({
            'tokens': tokens,
            'user': serializer.data
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])

@permission_classes([IsAuthenticated])
def test_token(request):
    # Optionally print user and token data for debugging
    print(f"Authenticated User: {request.user}")
    print(f"Token: {request.auth}")

    return Response(f"Passed for {request.user.email}")