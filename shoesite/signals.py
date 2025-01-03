# signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import OrderItem, Rating, WishlistItem, Product, Discount, ShoppingCart, Wishlist, Customer, Guest
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.models import Session

@receiver(post_save, sender=Session)
def create_guest_for_session(sender, instance, created, **kwargs):
    if created:  # Check if a new session is created
        Guest.objects.create(session_id=instance.session_key)
        



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
"""
# update product's avg rating with every new rating
@receiver(post_save, sender=Rating)
def update_product_avg_rating_on_save(sender, instance, **kwargs):
   
    #Update the avg_rating field in Product model when a Rating is added or updated.
    
    product = instance.product
    product.update_avg_rating()
    product.save()


@receiver(post_save, sender=Rating)
def update_product_on_rating_change(sender, instance, created, **kwargs):
    product = instance.product  # Assuming you have a foreign key to Product
    product.update_popularity_score()
"""
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


#it already covers updates to avg_rating and popularity_score for all related events (e.g., changes to OrderItem, Rating, and WishlistItem).
@receiver(post_save, sender=OrderItem)
@receiver(post_delete, sender=OrderItem)

@receiver(post_save, sender=Rating)
@receiver(post_delete, sender=Rating)

@receiver(post_save, sender=WishlistItem)
@receiver(post_delete, sender=WishlistItem)

def update_product_metrics(sender, instance, **kwargs):
    """
    Update popularity_score and avg_rating for the associated product
    when related objects (OrderItem, Rating, WishlistItem) are added, updated, or deleted.
    """
    product = instance.product  # Ensure the related Product is fetched
    product.update_popularity_score()
    product.update_avg_rating()
    product.save()


@receiver(post_save, sender=Discount)
@receiver(post_delete, sender=Discount)
def update_product_prices(sender, instance, **kwargs):
    """
    Update the price of all products related to a Discount when it is created, updated, or deleted.
    """
    products = Product.objects.filter(discount=instance)
    for product in products:
        product.save()  # Trigger price calculation in Product's save method
