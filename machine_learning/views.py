from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.models import User
import json
import random
from .models import Notification, NotificationTemplate

def index(request):
    return render(request, 'layout/layout.master.html')

# Notification Views

@login_required
def notification_list(request):
    """List all notifications for the current user"""
    notifications = Notification.objects.filter(
        Q(user=request.user) | Q(is_global=True),
        is_active=True
    ).exclude(
        Q(expiry_date__lt=timezone.now()) & Q(auto_expire=True)
    ).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Count unread notifications
    unread_count = notifications.filter(is_read=False).count()
    
    context = {
        'notifications': page_obj,
        'unread_count': unread_count,
        'total_count': notifications.count(),
    }
    return render(request, 'notifications/list.html', context)

@login_required
def notification_detail(request, notification_id):
    """View notification details and mark as read"""
    notification = get_object_or_404(Notification, id=notification_id)
    
    # Check if user can view this notification
    if notification.user and notification.user != request.user and not notification.is_global:
        return HttpResponse("Not authorized", status=403)
    
    # Mark as read when viewed
    if not notification.is_read:
        notification.mark_as_read()
    
    context = {
        'notification': notification,
    }
    return render(request, 'notifications/detail.html', context)

@login_required
@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    """Mark a specific notification as read"""
    notification = get_object_or_404(Notification, id=notification_id)
    
    # Check if user can modify this notification
    if notification.user and notification.user != request.user and not notification.is_global:
        return JsonResponse({'error': 'Not authorized'}, status=403)
    
    notification.mark_as_read()
    return JsonResponse({'success': True, 'message': 'Notification marked as read'})

@login_required
@require_http_methods(["POST"])
def mark_all_read(request):
    """Mark all notifications as read for the current user"""
    notifications = Notification.objects.filter(
        Q(user=request.user) | Q(is_global=True),
        is_read=False,
        is_active=True
    )
    
    updated_count = notifications.update(
        is_read=True,
        read_at=timezone.now()
    )
    
    return JsonResponse({
        'success': True, 
        'message': f'{updated_count} notifications marked as read'
    })

@login_required
@require_http_methods(["POST"])
def delete_notification(request, notification_id):
    """Delete a notification"""
    notification = get_object_or_404(Notification, id=notification_id)
    
    # Check if user can delete this notification
    if notification.user and notification.user != request.user and not notification.is_global:
        return JsonResponse({'error': 'Not authorized'}, status=403)
    
    notification.delete()
    return JsonResponse({'success': True, 'message': 'Notification deleted'})

# API Views for AJAX

@login_required
def get_notifications_api(request):
    """API endpoint to get notifications for AJAX requests"""
    notifications = Notification.objects.filter(
        Q(user=request.user) | Q(is_global=True),
        is_active=True
    ).exclude(
        Q(expiry_date__lt=timezone.now()) & Q(auto_expire=True)
    ).order_by('-created_at')[:10]  # Limit to 10 most recent
    
    notifications_data = []
    for notification in notifications:
        notifications_data.append({
            'id': str(notification.id),
            'title': notification.title,
            'message': notification.message,
            'type': notification.notification_type,
            'priority': notification.priority,
            'is_read': notification.is_read,
            'created_at': notification.created_at.isoformat(),
            'action_url': notification.action_url,
            'action_text': notification.action_text,
            'model_name': notification.model_name,
        })
    
    unread_count = Notification.objects.filter(
        Q(user=request.user) | Q(is_global=True),
        is_read=False,
        is_active=True
    ).exclude(
        Q(expiry_date__lt=timezone.now()) & Q(auto_expire=True)
    ).count()
    
    return JsonResponse({
        'notifications': notifications_data,
        'unread_count': unread_count
    })

@login_required
@csrf_exempt
def create_notification_api(request):
    """API endpoint to create notifications programmatically"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Required fields
        title = data.get('title')
        message = data.get('message')
        notification_type = data.get('type', 'info')
        
        if not title or not message:
            return JsonResponse({'error': 'Title and message are required'}, status=400)
        
        # Create notification
        notification = Notification.objects.create(
            title=title,
            message=message,
            notification_type=notification_type,
            priority=data.get('priority', 'medium'),
            user=request.user if not data.get('is_global', False) else None,
            is_global=data.get('is_global', False),
            action_url=data.get('action_url', ''),
            action_text=data.get('action_text', ''),
            model_name=data.get('model_name', ''),
            operation_id=data.get('operation_id', ''),
            metadata=data.get('metadata', {}),
            auto_expire=data.get('auto_expire', True),
        )
        
        return JsonResponse({
            'success': True,
            'notification_id': str(notification.id),
            'message': 'Notification created successfully'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Utility functions for creating notifications

def create_ml_training_notification(user, model_name, status, details=None):
    """Create a notification for ML training events"""
    notification_type = 'success' if status == 'completed' else 'error' if status == 'failed' else 'info'
    priority = 'high' if status in ['completed', 'failed'] else 'medium'
    
    title = f"Model Training {status.title()}"
    message = f"Training for model '{model_name}' has {status}."
    if details:
        message += f" Details: {details}"
    
    return Notification.objects.create(
        title=title,
        message=message,
        notification_type=notification_type,
        priority=priority,
        user=user,
        model_name=model_name,
        action_text="View Model" if status == 'completed' else "",
        action_url=f"/models/{model_name}/" if status == 'completed' else "",
    )

def create_prediction_notification(user, model_name, prediction_result, confidence=None):
    """Create a notification for prediction results"""
    title = "Prediction Completed"
    message = f"Prediction using model '{model_name}' completed successfully."
    if confidence:
        message += f" Confidence: {confidence:.2%}"
    
    return Notification.objects.create(
        title=title,
        message=message,
        notification_type='prediction',
        priority='medium',
        user=user,
        model_name=model_name,
        metadata={'prediction_result': prediction_result, 'confidence': confidence},
        action_text="View Results",
        action_url="/predictions/",
    )

def create_system_notification(title, message, priority='medium', is_global=True):
    """Create a system-wide notification"""
    return Notification.objects.create(
        title=title,
        message=message,
        notification_type='system',
        priority=priority,
        is_global=is_global,
        user=None,
    )

@login_required
@csrf_exempt
def generate_dynamic_notifications(request):
    """Generate and save dynamic notifications to database"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        # Get count from request body, default to 2 if not provided
        data = json.loads(request.body) if request.body else {}
        count = data.get('count', 2)
        
        # Validate count
        if not isinstance(count, int) or count < 1 or count > 10:
            count = 2  # Default to 2 if invalid
        
        # Get notification templates from database
        notification_templates = []
        templates = NotificationTemplate.objects.filter(is_active=True)
        
        for template in templates:
            # Generate random values for template variables
            template_data = {
                'accuracy': f"{85 + (random.random() * 10):.1f}",
                'records': random.randint(1000, 11000),
                'duration': random.randint(5, 65),
                'cpu_usage': random.randint(70, 90),
                'confidence': f"{random.random() * 0.3 + 0.7:.2f}",
                'improvement': f"{random.random() * 2 + 0.5:.1f}",
                'file_size': random.randint(10, 60),
                'record_count': random.randint(10000, 110000),
                'model_version': random.randint(1, 10),
                'predictor_version': random.randint(1, 3),
                'production_version': random.randint(1, 3),
                'anomaly_confidence': f"{random.random() * 0.2 + 0.8:.2f}",
                'neural_net_version': random.randint(1, 5)
            }
            
            # Format the template with random data
            try:
                formatted_title = template.title_template.format(**template_data)
                formatted_message = template.message_template.format(**template_data)
                
                # Determine model name and action based on template type
                model_name = ''
                action_text = ''
                action_url = ''
                
                if template.notification_type == 'training':
                    model_name = f'NeuralNet_v{template_data["neural_net_version"]}'
                    action_text = 'View Progress'
                    action_url = '/models/training/'
                elif template.notification_type == 'prediction':
                    model_name = f'Predictor_{template_data["predictor_version"]}'
                    action_text = 'View Prediction'
                    action_url = '/predictions/'
                elif template.notification_type == 'success' and 'model' in template.name:
                    model_name = f'Model_v{template_data["model_version"]}'
                    action_text = 'View Model'
                    action_url = '/models/'
                elif template.notification_type == 'info' and 'data' in template.name:
                    action_text = 'View Results'
                    action_url = '/data/processing/'
                elif template.notification_type == 'warning' and 'system' in template.name:
                    action_text = 'View Metrics'
                    action_url = '/system/metrics/'
                elif template.notification_type == 'warning' and 'anomaly' in template.name:
                    action_text = 'Investigate'
                    action_url = '/anomalies/'
                elif template.notification_type == 'success' and 'deployment' in template.name:
                    model_name = f'Production_Model_v{template_data["production_version"]}'
                    action_text = 'Deploy Now'
                    action_url = '/deploy/'
                elif template.notification_type == 'info' and 'dataset' in template.name:
                    action_text = 'View Dataset'
                    action_url = '/datasets/'
                
                notification_templates.append({
                    'title': formatted_title,
                    'message': formatted_message,
                    'notification_type': template.notification_type,
                    'priority': template.priority,
                    'model_name': model_name,
                    'action_text': action_text,
                    'action_url': action_url
                })
            except KeyError as e:
                # Skip templates with missing variables
                continue
        
        # Select the requested number of random notifications
        selected_notifications = random.sample(notification_templates, min(count, len(notification_templates)))
        created_notifications = []
        
        for template in selected_notifications:
            notification = Notification.objects.create(
                title=template['title'],
                message=template['message'],
                notification_type=template['notification_type'],
                priority=template['priority'],
                user=request.user,
                model_name=template.get('model_name', ''),
                action_text=template.get('action_text', ''),
                action_url=template.get('action_url', ''),
                metadata={
                    'isDynamic': True,
                    'generated_at': timezone.now().isoformat(),
                    'generated_by': 'system',
                    'source': 'dynamic_generator'
                }
            )
            created_notifications.append({
                'id': str(notification.id),
                'title': notification.title,
                'message': notification.message,
                'type': notification.notification_type,
                'priority': notification.priority,
                'created_at': notification.created_at.isoformat(),
                'action_url': notification.action_url,
                'action_text': notification.action_text,
                'model_name': notification.model_name,
                'metadata': notification.metadata
            })
        
        return JsonResponse({
            'success': True,
            'notifications': created_notifications,
            'message': f'Generated {len(created_notifications)} dynamic notifications'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
