
from django.urls import path
from .views import *
from .enrollment_views import * 
urlpatterns = [
    path('software-welcome-page', software_welcome_page, name='software_welcome_page'),
    path('crm_software_dashboard', crm_software_dashboard, name='crm_software_dashboard'), 
    path('followups/', crm_follow_up_list, name='crm_follow_up_list'),
    path('creat_follow_up/', create_followup, name='crm_create_followup'),
    path('delete_follow_up/<int:id>', delete_follow_up, name='crm_delete_follow_up'),
    path('followups/export/', export_followups, name='export_followups'),
    path('followups/import/', import_followups, name='import_followups'),
    path('followups/template/', download_template, name='download_template'), 
    
    path('followups/<int:pk>/', followup_detail, name='followup_detail'),
    path('followups/<int:id>/update/', update_followup, name='update_followup'),

    path('enquiries/', enquiry_list, name='crm_enquiry_list'),
    path('enquiries/<int:enquiry_id>/add-to-followup/', add_to_followup, name='crm_add_to_followup'),
    path('enquiries/export/', export_enquiries, name='crm_export_enquiries'),

    # Enrollment Management URLs
    path('enrollment-dashboard/', enrollment_dashboard, name='enrollment_dashboard'),
    path('enrollments/', enrolled_student_list, name='enrolled_student_list'),
    path('enrollments/export/', export_enrollments, name='export_enrollments'),
    path('enrollments/template/', download_enrollment_template, name='download_enrollment_template'),
    path('enrollments/import/', import_enrollments, name='import_enrollments'),
    path('enrollments/create/', create_enrollment, name='create_enrollment'),
    path('enrollments/<int:pk>/update/', update_enrollment, name='update_enrollment'),
    path('enrollments/<int:pk>/delete/', delete_enrollment, name='delete_enrollment'),

        # Batch Management URLs
    path('batches/', batch_list, name='enrollment_batch_list'),
    path('batches/create/', create_batch, name='create_batch'),
    path('batches/<int:pk>/update/', update_batch, name='update_batch'),
    path('batches/<int:pk>/delete/', delete_batch, name='delete_batch'),

]
