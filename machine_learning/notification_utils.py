"""
Utility functions for creating and managing notifications
"""
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from .models import Notification, NotificationTemplate

def create_notification(title, message, notification_type='info', priority='medium', 
                       user=None, is_global=False, action_url='', action_text='', 
                       model_name='', operation_id='', metadata=None, auto_expire=True, 
                       expiry_days=7):
    """
    Create a notification with the specified parameters
    
    Args:
        title (str): Notification title
        message (str): Notification message
        notification_type (str): Type of notification (info, success, warning, error, training, prediction, system)
        priority (str): Priority level (low, medium, high, urgent)
        user (User, optional): Target user (None for global notifications)
        is_global (bool): Whether this is a global notification
        action_url (str): URL to navigate to when clicked
        action_text (str): Text for action button
        model_name (str): ML model name if applicable
        operation_id (str): Operation ID for tracking
        metadata (dict): Additional metadata as JSON
        auto_expire (bool): Whether to auto-expire the notification
        expiry_days (int): Days until expiry (if auto_expire is True)
    
    Returns:
        Notification: The created notification object
    """
    expiry_date = None
    if auto_expire:
        expiry_date = timezone.now() + timedelta(days=expiry_days)
    
    return Notification.objects.create(
        title=title,
        message=message,
        notification_type=notification_type,
        priority=priority,
        user=user,
        is_global=is_global,
        action_url=action_url,
        action_text=action_text,
        model_name=model_name,
        operation_id=operation_id,
        metadata=metadata or {},
        auto_expire=auto_expire,
        expiry_date=expiry_date
    )

def create_ml_training_notification(user, model_name, status, accuracy=None, 
                                  duration=None, error_message=None, operation_id=None):
    """
    Create a notification for ML training events
    
    Args:
        user (User): User who initiated the training
        model_name (str): Name of the model being trained
        status (str): Training status (started, completed, failed)
        accuracy (float, optional): Model accuracy if completed
        duration (str, optional): Training duration
        error_message (str, optional): Error message if failed
        operation_id (str, optional): Operation ID for tracking
    
    Returns:
        Notification: The created notification object
    """
    if status == 'completed':
        title = f"Model Training Completed: {model_name}"
        message = f"Training for model '{model_name}' has completed successfully."
        if accuracy:
            message += f" Accuracy: {accuracy:.2f}%"
        if duration:
            message += f" Training time: {duration}"
        
        notification_type = 'success'
        priority = 'high'
        action_text = "View Model"
        action_url = f"/models/{model_name}/"
        
    elif status == 'failed':
        title = f"Model Training Failed: {model_name}"
        message = f"Training for model '{model_name}' has failed."
        if error_message:
            message += f" Error: {error_message}"
        
        notification_type = 'error'
        priority = 'high'
        action_text = "View Logs"
        action_url = f"/models/{model_name}/logs/"
        
    else:  # started
        title = f"Model Training Started: {model_name}"
        message = f"Training for model '{model_name}' has started."
        
        notification_type = 'info'
        priority = 'medium'
        action_text = "View Progress"
        action_url = f"/models/{model_name}/training/"
    
    metadata = {
        'model_name': model_name,
        'status': status,
        'accuracy': accuracy,
        'duration': duration,
        'error_message': error_message
    }
    
    return create_notification(
        title=title,
        message=message,
        notification_type=notification_type,
        priority=priority,
        user=user,
        model_name=model_name,
        operation_id=operation_id,
        action_url=action_url,
        action_text=action_text,
        metadata=metadata
    )

def create_prediction_notification(user, model_name, prediction_result, confidence=None, 
                                 operation_id=None, input_data=None):
    """
    Create a notification for prediction results
    
    Args:
        user (User): User who made the prediction
        model_name (str): Name of the model used
        prediction_result: The prediction result
        confidence (float, optional): Prediction confidence
        operation_id (str, optional): Operation ID for tracking
        input_data (dict, optional): Input data used for prediction
    
    Returns:
        Notification: The created notification object
    """
    title = f"Prediction Completed: {model_name}"
    message = f"Prediction using model '{model_name}' completed successfully."
    if confidence:
        message += f" Confidence: {confidence:.2%}"
    
    metadata = {
        'model_name': model_name,
        'prediction_result': prediction_result,
        'confidence': confidence,
        'input_data': input_data
    }
    
    return create_notification(
        title=title,
        message=message,
        notification_type='prediction',
        priority='medium',
        user=user,
        model_name=model_name,
        operation_id=operation_id,
        action_text="View Results",
        action_url="/predictions/",
        metadata=metadata
    )

def create_system_notification(title, message, priority='medium', is_global=True, 
                              action_url='', action_text='', expiry_days=7):
    """
    Create a system-wide notification
    
    Args:
        title (str): Notification title
        message (str): Notification message
        priority (str): Priority level
        is_global (bool): Whether this is a global notification
        action_url (str): URL to navigate to when clicked
        action_text (str): Text for action button
        expiry_days (int): Days until expiry
    
    Returns:
        Notification: The created notification object
    """
    return create_notification(
        title=title,
        message=message,
        notification_type='system',
        priority=priority,
        is_global=is_global,
        action_url=action_url,
        action_text=action_text,
        expiry_days=expiry_days
    )

def create_notification_from_template(template_name, user=None, **kwargs):
    """
    Create a notification from a template
    
    Args:
        template_name (str): Name of the notification template
        user (User, optional): Target user
        **kwargs: Variables to substitute in the template
    
    Returns:
        Notification: The created notification object
    """
    try:
        template = NotificationTemplate.objects.get(name=template_name, is_active=True)
        return template.create_notification(user=user, **kwargs)
    except NotificationTemplate.DoesNotExist:
        raise ValueError(f"Template '{template_name}' not found or not active")

def get_user_notifications(user, unread_only=False, limit=None):
    """
    Get notifications for a specific user
    
    Args:
        user (User): The user to get notifications for
        unread_only (bool): Whether to return only unread notifications
        limit (int, optional): Maximum number of notifications to return
    
    Returns:
        QuerySet: Notifications for the user
    """
    notifications = Notification.objects.filter(
        Q(user=user) | Q(is_global=True),
        is_active=True
    ).exclude(
        Q(expiry_date__lt=timezone.now()) & Q(auto_expire=True)
    ).order_by('-created_at')
    
    if unread_only:
        notifications = notifications.filter(is_read=False)
    
    if limit:
        notifications = notifications[:limit]
    
    return notifications

def mark_notifications_read(user, notification_ids=None):
    """
    Mark notifications as read
    
    Args:
        user (User): The user whose notifications to mark as read
        notification_ids (list, optional): Specific notification IDs to mark as read
    
    Returns:
        int: Number of notifications marked as read
    """
    notifications = Notification.objects.filter(
        Q(user=user) | Q(is_global=True),
        is_read=False,
        is_active=True
    )
    
    if notification_ids:
        notifications = notifications.filter(id__in=notification_ids)
    
    updated_count = notifications.update(
        is_read=True,
        read_at=timezone.now()
    )
    
    return updated_count

def cleanup_expired_notifications():
    """
    Clean up expired notifications
    
    Returns:
        int: Number of notifications cleaned up
    """
    expired_notifications = Notification.objects.filter(
        expiry_date__lt=timezone.now(),
        auto_expire=True,
        is_active=True
    )
    
    count = expired_notifications.count()
    expired_notifications.update(is_active=False)
    
    return count
