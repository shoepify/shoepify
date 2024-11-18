from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from shoesite.models import ProductManager
from shoesite.serializers import ProductManagerSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password, check_password


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
def signup_product_manager(request):
    if request.method == 'POST':
        serializer = ProductManagerSerializer(data=request.data)
        if serializer.is_valid():
            # Ensure password is hashed before saving
            validated_data = serializer.validated_data
            validated_data['password'] = make_password(validated_data['password'])

            # Save the product manager with hashed password
            product_manager = ProductManager.objects.create(**validated_data)

            # Generate tokens after successfully saving the user
            tokens = get_tokens_for_user(product_manager)

            return Response({
                'message': 'Product Manager created successfully',
                'manager_id': product_manager.manager_id,
                'tokens': tokens  # Include tokens in the response
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# login
@api_view(['POST'])
@permission_classes([AllowAny])

def login_product_manager(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'error': 'Please provide both email and password'},
                         status=status.HTTP_400_BAD_REQUEST)

    try:
        user = ProductManager.objects.get(email=email)
    except ProductManager.DoesNotExist:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    if not check_password(password, user.password):
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    tokens = get_tokens_for_user(user)
    return Response({
        'message': 'Login successful',
        'tokens': tokens,
        'user': ProductManagerSerializer(user).data
    }, status=status.HTTP_200_OK)

