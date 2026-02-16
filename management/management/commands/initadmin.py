from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

class Command(BaseCommand):
    help = 'Create or update a superuser from environment variables.'

    def handle(self, *args, **options):
        # Read from environment variables
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not username or not password:
            self.stdout.write(self.style.ERROR('Error: DJANGO_SUPERUSER_USERNAME and DJANGO_SUPERUSER_PASSWORD must be set in .env.'))
            return

        User = get_user_model()
        
        try:
            # Check if user exists
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                user.email = email
                user.set_password(password)
                user.is_staff = True
                user.is_superuser = True
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Successfully updated superuser "{username}".'))
            else:
                # Create new user
                User.objects.create_superuser(username=username, email=email, password=password)
                self.stdout.write(self.style.SUCCESS(f'Successfully created superuser "{username}".'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating/updating superuser: {e}'))
