
from django.urls import path
from .views import *
urlpatterns = [
    path('dashboard', student_dashboard, name='student_dashboard'), 
    path('free_course_list/', course_list, name='free_course_list'),
    path('course/<int:course_id>/', free_course_video, name='free_course_video'),
    path('course/<int:course_id>/certificate/', download_certificate, name='download_certificate'),
    path('certificates/', certificate_list, name='certificate_list'),

]
