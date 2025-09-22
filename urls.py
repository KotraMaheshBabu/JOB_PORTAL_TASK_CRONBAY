from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('job/new/', views.post_job, name='post_job'),
    path('job/<int:pk>/', views.job_detail, name='job_detail'),
    path('register/', views.register, name='register'),
]
