from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from datetime import datetime
from django.utils import timezone
from rest_framework_simplejwt.authentication import JWTAuthentication

from .report_services import (
    get_calling_agenda_data,
    get_counselor_performance_data,
    get_branch_funnel_data,
    generate_agenda_pdf,
    generate_agenda_excel,
)


class QueryParamJWTAuthentication(JWTAuthentication):
    """
    Authenticates JWT token from either:
    1. 'Authorization: Bearer <token>' HTTP header
    2. 'token' or 'access_token' query parameter (for direct file downloads in browsers / mobile download managers)
    """
    def authenticate(self, request):
        header = self.get_header(request)
        if header is not None:
            return super().authenticate(request)

        token = request.query_params.get('token') or request.query_params.get('access_token')
        if token:
            try:
                raw_token = token.encode('utf-8')
                validated_token = self.get_validated_token(raw_token)
                return self.get_user(validated_token), validated_token
            except Exception:
                return None

        return None


class AvailableReportsCatalogAPIView(APIView):
    """
    Returns the dynamic list of reports that the current user has permission to access.
    """
    authentication_classes = [QueryParamJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = getattr(user, 'role', 'is_student')
        is_manager = user.is_superuser or role in ['is_crm_manager', 'is_crm_and_enrollment']

        reports = [
            {
                'id': 'daily_agenda',
                'title': "Daily Calling Agenda",
                'subtitle': "Today's scheduled and overdue follow-up calls",
                'category': 'Sales Execution',
                'icon': 'alarm',
                'formats': ['json', 'pdf', 'excel'],
                'endpoint': '/api/crm/reports/agenda/',
            },
            {
                'id': 'my_performance',
                'title': "My Conversion & Performance",
                'subtitle': "Conversion rate, enrolled students, active pipeline",
                'category': 'Personal KPIs',
                'icon': 'trending_up',
                'formats': ['json'],
                'endpoint': '/api/crm/reports/performance/',
            },
        ]

        if is_manager:
            reports.extend([
                {
                    'id': 'branch_funnel',
                    'title': "Branch Lead Pipeline & Funnel",
                    'subtitle': "Branch-wide stage distribution and conversion funnel",
                    'category': 'Branch Management',
                    'icon': 'pie_chart',
                    'formats': ['json'],
                    'endpoint': '/api/crm/reports/branch-funnel/',
                },
                {
                    'id': 'counselor_comparison',
                    'title': "Team Counselor Comparison",
                    'subtitle': "Productivity, call volume, and conversions by counselor",
                    'category': 'Branch Management',
                    'icon': 'people',
                    'formats': ['json'],
                    'endpoint': '/api/crm/reports/branch-funnel/',
                },
                {
                    'id': 'source_roi',
                    'title': "Lead Source Effectiveness (ROI)",
                    'subtitle': "Website vs Social Media vs Walk-in conversion rate",
                    'category': 'Branch Management',
                    'icon': 'campaign',
                    'formats': ['json'],
                    'endpoint': '/api/crm/reports/branch-funnel/',
                },
            ])

        return Response({
            'user_name': user.name if hasattr(user, 'name') and user.name else user.username,
            'role': role,
            'is_manager': is_manager,
            'reports': reports,
        })


class DailyCallingAgendaAPIView(APIView):
    """
    API view for retrieving daily calling agenda for the salesperson / counselor.
    Supports JSON, PDF, and Excel export formats.
    """
    authentication_classes = [QueryParamJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        target_date_str = request.query_params.get('date')
        export_format = request.query_params.get('export', 'json').lower()

        target_date = None
        if target_date_str:
            try:
                target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response({'detail': 'Invalid date format. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            target_date = timezone.now().date()

        agenda_data = get_calling_agenda_data(request.user, target_date)

        if export_format == 'pdf':
            pdf_bytes = generate_agenda_pdf(request.user, agenda_data, target_date)
            filename = f"Calling_Agenda_{target_date.strftime('%Y%m%d')}_{request.user.username}.pdf"
            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

        elif export_format in ['excel', 'xlsx']:
            excel_bytes = generate_agenda_excel(request.user, agenda_data)
            filename = f"Calling_Agenda_{target_date.strftime('%Y%m%d')}_{request.user.username}.xlsx"
            response = HttpResponse(excel_bytes, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

        return Response(agenda_data)


class CounselorPerformanceAPIView(APIView):
    """
    API view for personal conversion performance and pipeline analytics.
    """
    authentication_classes = [QueryParamJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')

        perf_data = get_counselor_performance_data(request.user, date_from, date_to)
        return Response(perf_data)


class BranchFunnelReportAPIView(APIView):
    """
    API view for branch-level pipeline funnel and counselor comparisons.
    Restricted to CRM Managers, Branch Managers, and Super Admins.
    """
    authentication_classes = [QueryParamJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        branch_id = request.query_params.get('branch_id')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')

        try:
            data = get_branch_funnel_data(request.user, branch_id=branch_id, date_from=date_from, date_to=date_to)
            return Response(data)
        except PermissionError as e:
            return Response({'detail': str(e)}, status=status.HTTP_403_FORBIDDEN)
