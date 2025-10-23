from django.test import TestCase
from django.urls import path 
from .views import index

urlpatterns = [
    path('', index, name='index'),
]