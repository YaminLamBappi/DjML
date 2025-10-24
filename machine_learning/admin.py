from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Notification, NotificationTemplate, ServiceCard

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'notification_type', 'priority', 'user', 'is_read', 
        'is_active', 'created_at', 'expiry_status'
    ]
    list_filter = [
        'notification_type', 'priority', 'is_read', 'is_active', 
        'is_global', 'created_at'
    ]
    search_fields = ['title', 'message', 'model_name', 'operation_id']
    readonly_fields = ['id', 'created_at', 'updated_at', 'read_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'title', 'message', 'notification_type', 'priority')
        }),
        ('Targeting', {
            'fields': ('user', 'is_global'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_read', 'is_active', 'auto_expire', 'expiry_date'),
            'classes': ('collapse',)
        }),
        ('Actions', {
            'fields': ('action_url', 'action_text'),
            'classes': ('collapse',)
        }),
        ('ML Context', {
            'fields': ('model_name', 'operation_id', 'metadata'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'read_at'),
            'classes': ('collapse',)
        }),
    )
    
    def expiry_status(self, obj):
        if not obj.auto_expire or not obj.expiry_date:
            return "Never"
        if obj.is_expired():
            return format_html('<span style="color: red;">Expired</span>')
        else:
            return format_html('<span style="color: green;">Active</span>')
    expiry_status.short_description = 'Expiry Status'
    
    actions = ['mark_as_read', 'mark_as_unread', 'activate_notifications', 'deactivate_notifications']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True, read_at=timezone.now())
        self.message_user(request, f'{updated} notifications marked as read.')
    mark_as_read.short_description = "Mark selected notifications as read"
    
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False, read_at=None)
        self.message_user(request, f'{updated} notifications marked as unread.')
    mark_as_unread.short_description = "Mark selected notifications as unread"
    
    def activate_notifications(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} notifications activated.')
    activate_notifications.short_description = "Activate selected notifications"
    
    def deactivate_notifications(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} notifications deactivated.')
    deactivate_notifications.short_description = "Deactivate selected notifications"

@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'notification_type', 'priority', 'is_active', 'created_at', 'preview']
    list_filter = ['notification_type', 'priority', 'is_active', 'created_at']
    search_fields = ['name', 'title_template', 'message_template']
    readonly_fields = ['created_at', 'preview']
    
    fieldsets = (
        ('Template Information', {
            'fields': ('name', 'is_active')
        }),
        ('Content', {
            'fields': ('title_template', 'message_template', 'preview')
        }),
        ('Settings', {
            'fields': ('notification_type', 'priority')
        }),
        ('Available Variables', {
            'fields': ('variable_help',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )
    
    actions = ['activate_templates', 'deactivate_templates', 'test_template']
    
    def preview(self, obj):
        """Show a preview of the template with sample data"""
        if not obj.title_template or not obj.message_template:
            return "No template content"
        
        sample_data = {
            'accuracy': '94.2',
            'records': '5000',
            'duration': '30',
            'cpu_usage': '75',
            'confidence': '0.87',
            'improvement': '1.5',
            'file_size': '25',
            'record_count': '50000',
            'model_version': '3',
            'predictor_version': '2',
            'production_version': '1',
            'anomaly_confidence': '0.92',
            'neural_net_version': '4'
        }
        
        try:
            title = obj.title_template.format(**sample_data)
            message = obj.message_template.format(**sample_data)
            return f"<strong>{title}</strong><br><small>{message}</small>"
        except KeyError as e:
            return f"<span style='color: red;'>Missing variable: {e}</span>"
    preview.allow_tags = True
    preview.short_description = 'Preview'
    
    def variable_help(self, obj):
        """Show available variables for templates"""
        return """
        Available variables for templates:
        • {accuracy} - Model accuracy (85-95%)
        • {records} - Number of records (1000-11000)
        • {duration} - Processing time in minutes (5-65)
        • {cpu_usage} - CPU usage percentage (70-90)
        • {confidence} - Confidence score (0.7-1.0)
        • {improvement} - Accuracy improvement (0.5-2.5%)
        • {file_size} - File size in MB (10-60)
        • {record_count} - Record count (10000-110000)
        • {model_version} - Model version (1-10)
        • {predictor_version} - Predictor version (1-3)
        • {production_version} - Production version (1-3)
        • {anomaly_confidence} - Anomaly confidence (0.8-1.0)
        • {neural_net_version} - Neural net version (1-5)
        """
    variable_help.short_description = 'Variable Help'
    
    def activate_templates(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} templates activated.')
    activate_templates.short_description = "Activate selected templates"
    
    def deactivate_templates(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} templates deactivated.')
    deactivate_templates.short_description = "Deactivate selected templates"
    
    def test_template(self, request, queryset):
        """Test selected templates by generating notifications"""
        from machine_learning.views import generate_dynamic_notifications
        from django.test import RequestFactory
        
        factory = RequestFactory()
        test_request = factory.post('/api/notifications/generate-dynamic/', 
                                  data='{"count": 1}', 
                                  content_type='application/json')
        test_request.user = request.user
        
        for template in queryset:
            # Temporarily deactivate other templates
            NotificationTemplate.objects.exclude(id=template.id).update(is_active=False)
            template.is_active = True
            template.save()
            
            try:
                response = generate_dynamic_notifications(test_request)
                if response.status_code == 200:
                    self.message_user(request, f'Template "{template.name}" tested successfully!')
                else:
                    self.message_user(request, f'Template "{template.name}" test failed: {response.content.decode()}')
            except Exception as e:
                self.message_user(request, f'Template "{template.name}" error: {str(e)}')
        
        # Reactivate all templates
        NotificationTemplate.objects.all().update(is_active=True)
    test_template.short_description = "Test selected templates"

@admin.register(ServiceCard)
class ServiceCardAdmin(admin.ModelAdmin):
    list_display = ('title', 'service_key', 'icon', 'metric_value', 'metric_label')