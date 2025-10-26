
from django.urls import path
from .views import *
urlpatterns = [
    path('dashboard', student_dashboard, name='student_dashboard'), 
    
]
