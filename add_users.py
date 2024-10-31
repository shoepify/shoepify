from django.core.management.base import BaseCommand
from shoesite.models import User  # Adjust this import based on your actual User model

class Command(BaseCommand):
    help = 'Add dummy users to the database'

    def handle(self, *args, **kwargs):
        users = [
            {"username": "user1", "email": "user1@example.com", "password": "password123"},
            {"username": "user2", "email": "user2@example.com", "password": "password123"},
        ]

        for user_data in users:
            user, created = User.objects.get_or_create(
                username=user_data["username"],
                email=user_data["email"],
                defaults={"password": user_data["password"]},  # Remember to hash in production
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'User {user.username} created.'))
            else:
                self.stdout.write(self.style.WARNING(f'User {user.username} already exists.'))
