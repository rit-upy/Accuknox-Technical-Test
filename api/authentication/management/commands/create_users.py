from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string
from authentication.models import User
from faker import Faker

class Command(BaseCommand):
    help = 'Create random users'

    def add_arguments(self, parser):
        parser.add_argument('total', type=int, help='Indicates the number of users to be created')

    def handle(self, *args, **kwargs):
        total = kwargs['total']
        fake = Faker()
        for _ in range(total):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = fake.email()
            password = get_random_string(length = 30)
            User.objects.create_user(email=email, password=password, first_name=first_name, last_name=last_name)
            self.stdout.write(self.style.SUCCESS(f'Successfully created user {email}'))
