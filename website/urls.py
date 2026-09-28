from django.urls import path
from . import views

app_name = 'website'

urlpatterns = [
    path('', views.home, name='home'),
    path('apply/', views.submit_application, name='submit_application'),
    path('contact/', views.submit_contact, name='submit_contact'),
]
