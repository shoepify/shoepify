# serializers.py
from rest_framework import serializers
from .models import Customer, OrderItem, Refund, Product, Wishlist, WishlistItem, ShoppingCart, CartItem,SalesManager,ProductManager,Comment, Guest
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

 #new rivar
class UserSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

 #new rivar

class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = ['id']

    
# User Serializers
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'tax_id', 'email', 'password', 'home_address']
    
    extra_kwargs = {
        'password': {'write_only': True},  # Ensure password is only used for write operations
        'email': {'required': True},  # Ensure email is required
    }



class SalesManagerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)  # Include 'id' as a read-only field
    
    class Meta:
        model = ProductManager
        fields = ['id', 'manager_id', 'password', 'name', 'email']

class ProductManagerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)  # Include 'id' as a read-only field
    
    class Meta:
        model = ProductManager
        fields = ['id', 'manager_id', 'password', 'name', 'email']

class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = ['guest_id', 'session_id', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['product_id', 'model', 'serial_number', 'stock', 
                  'warranty_status', 'distributor_info', 'description', 'base_price', 
                  'price', 'popularity_score', 'category', 'avg_rating', 'image_name']


# Shopping Cart and Cart Item Serializers
class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.CharField(source='product.product_id')
    quantity = serializers.IntegerField()

    class Meta:
        model = CartItem
        fields = ['product_id', 'quantity']


# Shopping Cart Serializer
class ShoppingCartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, source='cartitem_set')
    owner = serializers.SerializerMethodField()

    class Meta:
        model = ShoppingCart
        fields = ['owner', 'cart_items']

    def get_owner(self, obj):
        """Return the serialized owner based on whether it's a Customer or Guest."""
        if isinstance(obj.owner, Customer):
            return CustomerSerializer(obj.owner).data
        elif isinstance(obj.owner, Guest):
            return GuestSerializer(obj.owner).data
        return None  # Handle case where there's no owner





class WishlistItemSerializer(serializers.ModelSerializer):
    product_id = serializers.CharField(source='product.product_id')
    model = serializers.CharField(source='product.model')

    class Meta:
        model = WishlistItem
        fields = ['product_id', 'model']

class WishlistSerializer(serializers.ModelSerializer):
    wishlist_items = WishlistItemSerializer(many=True, source='wishlistitem_set')

    class Meta:
        model = Wishlist
        fields = ['customer', 'wishlist_items']




class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = ['order_item', 'status', 'refunded_amount']

#comment serializer
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'product', 'customer', 'comment', 'approval_status']
