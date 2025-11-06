
from django.urls import path
from .views import *
urlpatterns = [
    path('dashboard', student_dashboard, name='student_dashboard'), 
    path('free_course_list/', course_list, name='free_course_list'),
    path('course/<int:course_id>/', free_course_video, name='free_course_video'),
    path('course/<int:course_id>/certificate/', download_certificate, name='download_certificate'),
    path('certificates/', certificate_list, name='certificate_list'),
    path('basic_to_advance_course_list/', basic_to_advance_course_list, name='basic_to_advance_course_list'),
    path('advance_to_pro_course_list/', advance_to_pro_course_list, name='advance_to_pro_course_list'),

]
