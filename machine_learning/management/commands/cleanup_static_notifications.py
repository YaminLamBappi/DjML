from django.core.management.base import BaseCommand
from machine_learning.models import Notification

class Command(BaseCommand):
    help = 'Remove all static/legacy notifications and keep only dynamic ones'

    def handle(self, *args, **options):
        # Remove notifications that are not dynamic (don't have isDynamic metadata)
        static_notifications = Notification.objects.filter(
            metadata__isDynamic__isnull=True
        )
        
        count = static_notifications.count()
        static_notifications.delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'Removed {count} static notifications from database')
        )
        
        # Show remaining dynamic notifications
        dynamic_count = Notification.objects.filter(
            metadata__isDynamic=True
        ).count()
        
        self.stdout.write(f'Remaining dynamic notifications: {dynamic_count}')
        
        # Show total notifications
        total_count = Notification.objects.count()
        self.stdout.write(f'Total notifications in database: {total_count}')
