# serializers.py
from rest_framework import serializers
from .models import Customer, OrderItem, Refund, Product, Wishlist, WishlistItem, ShoppingCart, CartItem
import base64


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            'customer_id', 'password', 'name', 'tax_id', 'email',
            'home_address', 'billing_address', 'phone_number'
        ]





class ProductSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'product_id',
            'model',
            'serial_number',
            'stock',
            'warranty_status',
            'distributor_info',
            'description',
            'base_price',
            'price',
            'image_url'  # Include the image URL
        ]

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

# Shopping Cart and Cart Item Serializers
class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.CharField(source='product.product_id')
    quantity = serializers.IntegerField()

    class Meta:
        model = CartItem
        fields = ['product_id', 'quantity']

class ShoppingCartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, source='cartitem_set')

    class Meta:
        model = ShoppingCart
        fields = ['customer', 'cart_items']




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
