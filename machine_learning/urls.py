from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'machine_learning'

urlpatterns = [
    path('', views.index, name='index'),

    # Auth
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/signup/', views.signup_view, name='signup'),
    path('accounts/logout/', views.logout_view, name='logout'),

    # Notification URLs
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<uuid:notification_id>/', views.notification_detail, name='notification_detail'),
    path('notifications/<uuid:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/<uuid:notification_id>/delete/', views.delete_notification, name='delete_notification'),
    path('notifications/mark-all-read/', views.mark_all_read, name='mark_all_read'),


    #Profile URLs
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    # API URLs
    path('api/notifications/', views.get_notifications_api, name='get_notifications_api'),
    path('api/notifications/create/', views.create_notification_api, name='create_notification_api'),
    path('api/notifications/generate-dynamic/', views.generate_dynamic_notifications, name='generate_dynamic_notifications'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)