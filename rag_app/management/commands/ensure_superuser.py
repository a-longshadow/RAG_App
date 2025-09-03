import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import IntegrityError


class Command(BaseCommand):
    """
    Django management command to ensure a superuser exists with credentials from environment variables.
    Usage: python manage.py ensure_superuser
    """
    help = 'Create superuser from environment variables if it does not exist'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-if-exists',
            action='store_true',
            help='Skip creation if any superuser already exists',
        )

    def handle(self, *args, **options):
        # Get superuser credentials from environment variables
        username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'testpass123')
        email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@localhost.local')

        # Check if we should skip if any superuser exists
        if options['skip_if_exists'] and User.objects.filter(is_superuser=True).exists():
            self.stdout.write(
                self.style.WARNING('Superuser already exists. Skipping creation.')
            )
            return

        # Check if specific user already exists
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            if user.is_superuser:
                self.stdout.write(
                    self.style.WARNING(f'Superuser "{username}" already exists.')
                )
            else:
                # Make existing user a superuser
                user.is_superuser = True
                user.is_staff = True
                user.set_password(password)
                user.email = email
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'User "{username}" has been promoted to superuser.')
                )
            return

        # Create new superuser
        try:
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(
                self.style.SUCCESS(f'Superuser "{username}" created successfully!')
            )
            self.stdout.write(
                self.style.SUCCESS(f'Username: {username}')
            )
            self.stdout.write(
                self.style.SUCCESS(f'Email: {email}')
            )
            self.stdout.write(
                self.style.WARNING('Password: (set from DJANGO_SUPERUSER_PASSWORD)')
            )

        except IntegrityError as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating superuser: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Unexpected error: {e}')
            )