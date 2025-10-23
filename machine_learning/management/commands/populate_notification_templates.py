from django.core.management.base import BaseCommand
from machine_learning.models import NotificationTemplate

class Command(BaseCommand):
    help = 'Populate database with notification templates'

    def handle(self, *args, **options):
        # Clear existing templates
        NotificationTemplate.objects.all().delete()
        
        # Create notification templates
        templates_data = [
            {
                'name': 'ai_model_training_update',
                'title_template': 'AI Model Training Update',
                'message_template': 'Your neural network model has completed another training epoch. Current accuracy: {accuracy}%',
                'notification_type': 'training',
                'priority': 'medium'
            },
            {
                'name': 'data_processing_complete',
                'title_template': 'Data Processing Complete',
                'message_template': 'Batch processing completed successfully. Processed {records} records in {duration} minutes.',
                'notification_type': 'info',
                'priority': 'low'
            },
            {
                'name': 'system_performance_alert',
                'title_template': 'System Performance Alert',
                'message_template': 'CPU usage is at {cpu_usage}%. Consider scaling resources.',
                'notification_type': 'warning',
                'priority': 'medium'
            },
            {
                'name': 'new_prediction_available',
                'title_template': 'New Prediction Available',
                'message_template': 'Your prediction request has been completed. Confidence score: {confidence}',
                'notification_type': 'prediction',
                'priority': 'medium'
            },
            {
                'name': 'model_performance_update',
                'title_template': 'Model Performance Update',
                'message_template': 'Model accuracy has improved by {improvement}% since last check.',
                'notification_type': 'success',
                'priority': 'high'
            },
            {
                'name': 'dataset_upload_complete',
                'title_template': 'Dataset Upload Complete',
                'message_template': 'New dataset has been uploaded and validated. Size: {file_size}MB with {record_count} records.',
                'notification_type': 'info',
                'priority': 'low'
            },
            {
                'name': 'model_deployment_ready',
                'title_template': 'Model Deployment Ready',
                'message_template': 'Your trained model is ready for deployment. Performance metrics exceed requirements.',
                'notification_type': 'success',
                'priority': 'high'
            },
            {
                'name': 'anomaly_detected',
                'title_template': 'Anomaly Detected',
                'message_template': 'Unusual pattern detected in data stream. Confidence: {anomaly_confidence}',
                'notification_type': 'warning',
                'priority': 'high'
            },
            {
                'name': 'model_accuracy_improvement',
                'title_template': 'Model Accuracy Improved',
                'message_template': 'NeuralNet_v{neural_net_version} accuracy increased by {improvement}% after retraining.',
                'notification_type': 'success',
                'priority': 'medium'
            },
            {
                'name': 'data_quality_alert',
                'title_template': 'Data Quality Alert',
                'message_template': 'Data quality score dropped to {cpu_usage}%. Review data preprocessing pipeline.',
                'notification_type': 'warning',
                'priority': 'high'
            },
            {
                'name': 'model_retraining_complete',
                'title_template': 'Model Retraining Complete',
                'message_template': 'Model_v{model_version} retraining completed with {accuracy}% accuracy on {records} samples.',
                'notification_type': 'training',
                'priority': 'medium'
            },
            {
                'name': 'prediction_batch_complete',
                'title_template': 'Prediction Batch Complete',
                'message_template': 'Batch prediction completed for {records} samples. Average confidence: {confidence}.',
                'notification_type': 'prediction',
                'priority': 'low'
            }
        ]
        
        created_count = 0
        for template_data in templates_data:
            template, created = NotificationTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults=template_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'Created template: {template.name}')
            else:
                self.stdout.write(f'Template already exists: {template.name}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} notification templates!')
        )
        self.stdout.write(f'Total templates in database: {NotificationTemplate.objects.count()}')
