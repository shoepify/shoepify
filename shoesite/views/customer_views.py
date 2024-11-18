# views.py
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from shoesite.models import Customer  # Update to absolute import
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password, check_password
from shoesite.serializers import CustomerSerializer, WishlistSerializer, RefundSerializer, WishlistItemSerializer, ShoppingCartSerializer, CartItemSerializer, ProductSerializer
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes, authentication_classes
import logging
logger = logging.getLogger(__name__)


# CUSTOMER

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
@permission_classes([AllowAny])
def signup_customer(request):
    if request.method == 'POST':
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            # Ensure password is hashed before saving
            password = request.data.get('password')
            if password:
                request.data['password'] = make_password(password)

            customer = serializer.save()

            # Generate tokens after successfully saving the user
            tokens = get_tokens_for_user(customer)

            return Response({
                'message': 'Customer created successfully',
                'customer_id': customer.id,
                'tokens': tokens  # Include tokens in the response
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# login
@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([]) 
def login_customer(request):
    email = request.data.get('email')
    password = request.data.get('password')


    if not email or not password:
        return Response({'error': 'Please provide both email and password'},
                         status=status.HTTP_400_BAD_REQUEST)

    # check whether customer with given email exists
    try:
        user = Customer.objects.get(email=email)
    except Customer.DoesNotExist:
        return Response({'error': 'Invalid email'}, status=status.HTTP_401_UNAUTHORIZED)

    # check if password is correct
    if password != user.password:
        # if wrong return error
        return Response({'error': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)

    # if all good, return tokens
    tokens = get_tokens_for_user(user)
    return Response({
        'tokens': tokens,
        'user': CustomerSerializer(user).data
    })


@csrf_exempt
def get_customer(request, customer_id):
    if request.method == 'GET':
        customer = get_object_or_404(Customer, id=customer_id)
        return JsonResponse({'customer_id': customer.id, 'name': customer.name})

@csrf_exempt
def create_customer(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        serializer = CustomerSerializer(data=data)
        if serializer.is_valid():
            customer = serializer.save()
            return JsonResponse({'message': 'Customer created successfully', 'customer_id': customer.id}, status=201)
        return JsonResponse(serializer.errors, status=400)