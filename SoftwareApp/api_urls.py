from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .api_views import (
    BranchListAPIView,
    CRMChoicesAPIView,
    CRMFollowupDetailAPIView,
    CRMFollowupListCreateAPIView,
    CRMFollowupRecordAPIView,
    CRMFollowupStatsAPIView,
    ChangePasswordAPIView,
    CurrentUserAPIView,
    EnquiryConvertToFollowupAPIView,
    EnquiryListAPIView,
    ForgotPasswordRequestOTPAPIView,
    ForgotPasswordVerifyOTPAPIView,
    InterestOptionListAPIView,
    LoginAPIView,
    UserProfileAPIView,
)
from .report_views import (
    AvailableReportsCatalogAPIView,
    DailyCallingAgendaAPIView,
    CounselorPerformanceAPIView,
    BranchFunnelReportAPIView,
)

urlpatterns = [
    # Auth & Profile
    path('auth/login/', LoginAPIView.as_view(), name='api_login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='api_token_refresh'),
    path('auth/me/', CurrentUserAPIView.as_view(), name='api_current_user'),
    path('auth/profile/', UserProfileAPIView.as_view(), name='api_user_profile'),
    path('auth/change-password/', ChangePasswordAPIView.as_view(), name='api_change_password'),
    path('auth/forgot-password/request-otp/', ForgotPasswordRequestOTPAPIView.as_view(), name='api_forgot_password_request'),
    path('auth/forgot-password/verify-otp/', ForgotPasswordVerifyOTPAPIView.as_view(), name='api_forgot_password_verify'),

    # Follow-ups
    path('crm/followups/', CRMFollowupListCreateAPIView.as_view(), name='api_crm_followups_list_create'),
    path('crm/followups/stats/', CRMFollowupStatsAPIView.as_view(), name='api_crm_followups_stats'),
    path('crm/followups/<int:pk>/', CRMFollowupDetailAPIView.as_view(), name='api_crm_followup_detail'),
    path('crm/followups/<int:pk>/record/', CRMFollowupRecordAPIView.as_view(), name='api_crm_followup_record'),

    # Master Data & Dynamic Choices
    path('crm/choices/', CRMChoicesAPIView.as_view(), name='api_crm_choices'),
    path('crm/branches/', BranchListAPIView.as_view(), name='api_crm_branches'),
    path('crm/interests/', InterestOptionListAPIView.as_view(), name='api_crm_interests'),

    # Enquiries
    path('crm/enquiries/', EnquiryListAPIView.as_view(), name='api_crm_enquiries'),
    path('crm/enquiries/<int:pk>/convert/', EnquiryConvertToFollowupAPIView.as_view(), name='api_crm_enquiry_convert'),

    # Reports & Sales Performance (RBAC Scoped)
    path('crm/reports/catalog/', AvailableReportsCatalogAPIView.as_view(), name='api_crm_reports_catalog'),
    path('crm/reports/agenda/', DailyCallingAgendaAPIView.as_view(), name='api_crm_reports_agenda'),
    path('crm/reports/performance/', CounselorPerformanceAPIView.as_view(), name='api_crm_reports_performance'),
    path('crm/reports/branch-funnel/', BranchFunnelReportAPIView.as_view(), name='api_crm_reports_branch_funnel'),
]
