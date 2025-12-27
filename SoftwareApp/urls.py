
from django.urls import path
from .views import *
urlpatterns = [
    path('software-welcome-page', software_welcome_page, name='software_welcome_page'),
    path('crm_software_dashboard', crm_software_dashboard, name='crm_software_dashboard'), 
    path('followups/', crm_follow_up_list, name='crm_follow_up_list'),
    path('creat_follow_up/', create_followup, name='crm_create_followup'),
    path('followups/export/', export_followups, name='export_followups'),
    path('followups/import/', import_followups, name='import_followups'),
    path('followups/template/', download_template, name='download_template'), 
    
    path('followups/<int:pk>/', followup_detail, name='followup_detail'),
    path('followups/<int:id>/update/', update_followup, name='update_followup'),

    path('enquiries/', enquiry_list, name='crm_enquiry_list'),
    path('enquiries/<int:enquiry_id>/add-to-followup/', add_to_followup, name='crm_add_to_followup'),
    path('enquiries/export/', export_enquiries, name='crm_export_enquiries'),

]
