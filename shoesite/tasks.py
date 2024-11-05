from celery import shared_task
from .models import Product

@shared_task
def update_all_popularity_scores():
    for product in Product.objects.all():
        product.update_popularity_score()


