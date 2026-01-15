
from django.urls import path
from .views import *
from .enrollment_views import * 
urlpatterns = [
    path('software-welcome-page', software_welcome_page, name='software_welcome_page'),
    path('crm_software_dashboard', crm_software_dashboard, name='crm_software_dashboard'), 
    path('enrollments/export-filtered/', export_enrollments_filtered, name='export_enrollments_filtered'),
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
    path('enrollments/<int:pk>/', enrollment_detail, name='enrollment_detail'),
    path('enrollments/export/', export_enrollments, name='export_enrollments'),
    path('enrollments/template/', download_enrollment_template, name='download_enrollment_template'),
    path('enrollments/import/', import_enrollments, name='import_enrollments'),
    path('enrollments/create/', create_enrollment, name='create_enrollment'),
    path('enrollments/<int:pk>/update/', update_enrollment, name='update_enrollment'),
    path('enrollments/<int:pk>/delete/', delete_enrollment, name='delete_enrollment'),

    path('payment/<int:enrollment_id>/payment/', record_payment, name='record_payment'),
    path('payment/<int:id>/update_payment/', update_payment, name='payment_update_payment'),
    path('payment/<int:id>/delete_payment/', delete_payment, name='payment_delete_payment'),
    path('payments/<int:pk>/receipt/', print_payment_receipt, name='print_payment_receipt'),

        # Batch Management URLs
    path('batches/', batch_list, name='enrollment_batch_list'),
    path('batches/create/', create_batch, name='create_batch'),
    path('batches/<int:pk>/update/', update_batch, name='update_batch'),
    path('batches/<int:pk>/delete/', delete_batch, name='delete_batch'),
    path('batches/<int:pk>/details/', batch_detail, name='enroallments_batch_detail'),
    
    path('batch/<int:batch_id>/export-excel/', export_batch_report_excel, name='export_batch_excel'),
    # enroll_student_from_follow_up
    path('enroll_student_from_follow_up/<int:id>/', enroll_student_from_follow_up, name='enroll_student_from_follow_up'),

    path('branches/', branch_list, name='branch_list'),
    path('branches/create/', create_branch, name='create_branch'),
    path('branches/<int:pk>/update/', update_branch, name='update_branch'),
    path('branches/<int:pk>/delete/', delete_branch, name='delete_branch'),

    # Student Interest CRUD URLs
    path('student-interests/', student_interest_list, name='student_interest_list'),
    path('student-interests/create/', create_student_interest, name='create_student_interest'),
    path('student-interests/<int:pk>/update/', update_student_interest, name='update_student_interest'),
    path('student-interests/<int:pk>/delete/', delete_student_interest, name='delete_student_interest'),

    # Event Management URLs
    path('enrollment-events/', event_list, name='enrollment_event_list'),
    path('enrollment-events/create/', create_event, name='enrollment_create_event'),
    path('enrollment-events/<int:pk>/', event_detail, name='enrollment_event_detail'),
    path('enrollment-events/<int:pk>/update/', update_event, name='enrollment_update_event'),
    path('enrollment-events/<int:pk>/delete/', delete_event, name='enrollment_delete_event'),



]
