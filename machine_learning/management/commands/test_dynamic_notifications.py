from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from machine_learning.views import generate_dynamic_notifications
from django.test import RequestFactory
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Test dynamic notification generation from database templates'

    def handle(self, *args, **options):
        # Get or create a test user
        User = get_user_model()
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write('Created test user')
        else:
            self.stdout.write('Using existing test user')
        
        # Create a mock request
        factory = RequestFactory()
        request = factory.post('/api/notifications/generate-dynamic/', 
                              data='{"count": 3}', 
                              content_type='application/json')
        request.user = user
        
        # Generate notifications
        try:
            response = generate_dynamic_notifications(request)
            self.stdout.write(f'Response status: {response.status_code}')
            self.stdout.write(f'Response content: {response.content.decode()}')
        except Exception as e:
            self.stdout.write(f'Error: {str(e)}')
        
        # Show notification count
        from machine_learning.models import Notification
        total_notifications = Notification.objects.count()
        user_notifications = Notification.objects.filter(user=user).count()
        
        self.stdout.write(f'Total notifications in database: {total_notifications}')
        self.stdout.write(f'Notifications for test user: {user_notifications}')
