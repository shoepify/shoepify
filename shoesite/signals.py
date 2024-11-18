# signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import OrderItem, Rating, WishlistItem, Product, Discount, ShoppingCart, Wishlist, Customer, Guest
from django.contrib.contenttypes.models import ContentType



# SHOPPING CART
# Signal to create a shopping cart for each new customer
@receiver(post_save, sender=Customer)
def create_shopping_cart_for_customer(sender, instance, created, **kwargs):
    if created:
        content_type = ContentType.objects.get_for_model(instance)
        ShoppingCart.objects.create(
            owner_content_type=content_type,
            owner_object_id=instance.pk
        )

# Signal to create a shopping cart for each new guest
@receiver(post_save, sender=Guest)
def create_shopping_cart_for_guest(sender, instance, created, **kwargs):
    if created:
        content_type = ContentType.objects.get_for_model(instance)
        ShoppingCart.objects.create(
            owner_content_type=content_type,
            owner_object_id=instance.pk
        )


# WISHLIST
# Signal to create a wishlist for each new customer
@receiver(post_save, sender=Customer)
def create_wishlist_for_customer(sender, instance, created, **kwargs):
    if created:
        Wishlist.objects.create(customer=instance)

# PRODUCT 
# update price if discount changes
@receiver(post_save, sender=Discount)
@receiver(post_delete, sender=Discount)
def update_related_products(sender, instance, **kwargs):
    products = Product.objects.filter(discount=instance)
    for product in products:
        product.save()  

@receiver(post_save, sender=OrderItem)
def update_product_on_orderitem_change(sender, instance, created, **kwargs):
    product = instance.product  # Assuming you have a foreign key to Product
    product.update_popularity_score()

@receiver(post_delete, sender=OrderItem)
def update_product_on_orderitem_delete(sender, instance, **kwargs):
    product = instance.product
    product.update_popularity_score()

# RATING

# update product's avg rating with every new rating
@receiver(post_save, sender=Rating)
def update_product_avg_rating_on_save(sender, instance, **kwargs):
    """
    Update the avg_rating field in Product model when a Rating is added or updated.
    """
    product = instance.product
    product.update_avg_rating()
    product.save()


@receiver(post_save, sender=Rating)
def update_product_on_rating_change(sender, instance, created, **kwargs):
    product = instance.product  # Assuming you have a foreign key to Product
    product.update_popularity_score()

@receiver(post_delete, sender=Rating)
def update_product_on_rating_delete(sender, instance, **kwargs):
    product = instance.product
    product.update_popularity_score()

@receiver(post_save, sender=WishlistItem)
def update_product_on_wishlistitem_change(sender, instance, created, **kwargs):
    product = instance.product  # Assuming you have a foreign key to Product
    product.update_popularity_score()

@receiver(post_delete, sender=WishlistItem)
def update_product_on_wishlistitem_delete(sender, instance, **kwargs):
    product = instance.product
    product.update_popularity_score()
