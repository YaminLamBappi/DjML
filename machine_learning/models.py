from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

# Create your models here.

class Notification(models.Model):
    """
    Intelligent notification system for ML operations and system events
    """
    NOTIFICATION_TYPES = [
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('training', 'Model Training'),
        ('prediction', 'Prediction'),
        ('system', 'System'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, help_text="Notification title")
    message = models.TextField(help_text="Detailed notification message")
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info')
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    
    # User and targeting
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, 
                           help_text="Target user (null for all users)")
    is_global = models.BooleanField(default=False, help_text="Show to all users")
    
    # Status and interaction
    is_read = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, help_text="Whether notification is still active")
    auto_expire = models.BooleanField(default=True, help_text="Auto-expire after expiry_date")
    expiry_date = models.DateTimeField(null=True, blank=True, 
                                     help_text="When notification expires")
    
    # Action and navigation
    action_url = models.URLField(blank=True, help_text="URL to navigate to when clicked")
    action_text = models.CharField(max_length=50, blank=True, 
                                 help_text="Text for action button")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Additional data for ML operations
    model_name = models.CharField(max_length=100, blank=True, 
                                help_text="ML model name if applicable")
    operation_id = models.CharField(max_length=100, blank=True, 
                                  help_text="Operation ID for tracking")
    metadata = models.JSONField(default=dict, blank=True, 
                               help_text="Additional metadata as JSON")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['is_active', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.get_notification_type_display()}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    def is_expired(self):
        """Check if notification has expired"""
        if not self.auto_expire or not self.expiry_date:
            return False
        return timezone.now() > self.expiry_date
    
    def save(self, *args, **kwargs):
        """Override save to handle auto-expiry"""
        if self.auto_expire and not self.expiry_date:
            # Set default expiry to 7 days from creation
            self.expiry_date = timezone.now() + timezone.timedelta(days=7)
        super().save(*args, **kwargs)


class NotificationTemplate(models.Model):
    """
    Templates for creating notifications dynamically
    """
    name = models.CharField(max_length=100, unique=True)
    title_template = models.CharField(max_length=200, help_text="Template for title with {variables}")
    message_template = models.TextField(help_text="Template for message with {variables}")
    notification_type = models.CharField(max_length=20, choices=Notification.NOTIFICATION_TYPES)
    priority = models.CharField(max_length=10, choices=Notification.PRIORITY_LEVELS, default='medium')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    def create_notification(self, **kwargs):
        """Create a notification from this template"""
        title = self.title_template.format(**kwargs)
        message = self.message_template.format(**kwargs)
        
        return Notification.objects.create(
            title=title,
            message=message,
            notification_type=self.notification_type,
            priority=self.priority,
            **kwargs
        )
