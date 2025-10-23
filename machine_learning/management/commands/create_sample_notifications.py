from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from machine_learning.models import Notification, NotificationTemplate
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Create sample notifications and templates for testing'

    def handle(self, *args, **options):
        # Create sample notification templates
        templates_data = [
            {
                'name': 'model_training_completed',
                'title_template': 'Model Training Completed: {model_name}',
                'message_template': 'The {model_name} model has been successfully trained with {accuracy}% accuracy. Training took {duration} minutes.',
                'notification_type': 'success',
                'priority': 'high'
            },
            {
                'name': 'model_training_failed',
                'title_template': 'Model Training Failed: {model_name}',
                'message_template': 'Training failed for {model_name} model. Error: {error_message}. Please check the logs for more details.',
                'notification_type': 'error',
                'priority': 'high'
            },
            {
                'name': 'prediction_completed',
                'title_template': 'Prediction Completed: {model_name}',
                'message_template': 'Prediction using {model_name} completed successfully. Result: {prediction_result} with {confidence}% confidence.',
                'notification_type': 'prediction',
                'priority': 'medium'
            },
            {
                'name': 'system_maintenance',
                'title_template': 'System Maintenance: {service_name}',
                'message_template': 'Scheduled maintenance for {service_name} will begin at {start_time}. Expected downtime: {duration} minutes.',
                'notification_type': 'warning',
                'priority': 'medium'
            },
            {
                'name': 'data_processing_completed',
                'title_template': 'Data Processing Completed',
                'message_template': 'Data processing job completed successfully. Processed {record_count} records in {duration} minutes.',
                'notification_type': 'info',
                'priority': 'low'
            }
        ]

        for template_data in templates_data:
            template, created = NotificationTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults=template_data
            )
            if created:
                self.stdout.write(f'Created template: {template.name}')
            else:
                self.stdout.write(f'Template already exists: {template.name}')

        # Create sample notifications
        sample_notifications = [
            {
                'title': 'Welcome to the ML Platform!',
                'message': 'Welcome to our intelligent machine learning platform. You can now start training models, making predictions, and analyzing data.',
                'notification_type': 'info',
                'priority': 'medium',
                'is_global': True,
                'action_text': 'Get Started',
                'action_url': '/'
            },
            {
                'title': 'Model Training Completed',
                'message': 'Your neural network model "ImageClassifier_v2" has been successfully trained with 94.2% accuracy.',
                'notification_type': 'success',
                'priority': 'high',
                'is_global': False,
                'model_name': 'ImageClassifier_v2',
                'action_text': 'View Model',
                'action_url': '/models/ImageClassifier_v2/',
                'metadata': {'accuracy': 94.2, 'training_time': '2h 15m', 'dataset_size': '50,000 images'}
            },
            {
                'title': 'Prediction Service Available',
                'message': 'The prediction service is now available for real-time inference. You can make predictions using your trained models.',
                'notification_type': 'prediction',
                'priority': 'medium',
                'is_global': True,
                'action_text': 'Try Prediction',
                'action_url': '/predict/'
            },
            {
                'title': 'System Maintenance Scheduled',
                'message': 'Scheduled maintenance will occur on Sunday, 2:00 AM - 4:00 AM UTC. Some services may be temporarily unavailable.',
                'notification_type': 'warning',
                'priority': 'medium',
                'is_global': True,
                'expiry_date': timezone.now() + timedelta(days=3)
            },
            {
                'title': 'New Dataset Uploaded',
                'message': 'A new dataset "Customer_Behavior_2024" has been uploaded and is ready for analysis.',
                'notification_type': 'info',
                'priority': 'low',
                'is_global': False,
                'action_text': 'View Dataset',
                'action_url': '/datasets/Customer_Behavior_2024/'
            },
            {
                'title': 'Model Performance Alert',
                'message': 'Model "SentimentAnalyzer" performance has dropped below 85% threshold. Consider retraining.',
                'notification_type': 'warning',
                'priority': 'high',
                'is_global': False,
                'model_name': 'SentimentAnalyzer',
                'action_text': 'Retrain Model',
                'action_url': '/models/SentimentAnalyzer/retrain/',
                'metadata': {'current_accuracy': 82.1, 'threshold': 85.0}
            },
            {
                'title': 'Data Processing Completed',
                'message': 'Data preprocessing for dataset "Sales_Data_Q1" completed successfully. 15,000 records processed.',
                'notification_type': 'info',
                'priority': 'low',
                'is_global': False,
                'metadata': {'records_processed': 15000, 'processing_time': '45m'}
            }
        ]

        for notification_data in sample_notifications:
            notification = Notification.objects.create(**notification_data)
            self.stdout.write(f'Created notification: {notification.title}')

        # Create some expired notifications for testing
        expired_notifications = [
            {
                'title': 'Old System Update',
                'message': 'This is an old system update notification that has expired.',
                'notification_type': 'info',
                'priority': 'low',
                'is_global': True,
                'expiry_date': timezone.now() - timedelta(days=1),
                'is_active': False
            }
        ]

        for notification_data in expired_notifications:
            notification = Notification.objects.create(**notification_data)
            self.stdout.write(f'Created expired notification: {notification.title}')

        self.stdout.write(
            self.style.SUCCESS('Successfully created sample notifications and templates!')
        )
        self.stdout.write(f'Total notifications: {Notification.objects.count()}')
        self.stdout.write(f'Total templates: {NotificationTemplate.objects.count()}')
