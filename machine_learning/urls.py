from django.urls import path
from . import views

app_name = 'machine_learning'

urlpatterns = [
    # Main page
    path('', views.index, name='index'),
    
    # Notification URLs
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<uuid:notification_id>/', views.notification_detail, name='notification_detail'),
    path('notifications/<uuid:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/<uuid:notification_id>/delete/', views.delete_notification, name='delete_notification'),
    path('notifications/mark-all-read/', views.mark_all_read, name='mark_all_read'),
    
    # API URLs
    path('api/notifications/', views.get_notifications_api, name='get_notifications_api'),
    path('api/notifications/create/', views.create_notification_api, name='create_notification_api'),
    path('api/notifications/generate-dynamic/', views.generate_dynamic_notifications, name='generate_dynamic_notifications'),
]
