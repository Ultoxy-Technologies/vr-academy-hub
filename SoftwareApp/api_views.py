import re
from datetime import date, datetime
from django.contrib.auth import authenticate, get_user_model
from django.db.models import Q, F
from django.utils import timezone
from rest_framework import generics, status, views
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from AdminApp.models import Branch, CRM_Student_Interested_for_options, CRMFollowup, Enquiry, PasswordResetOTP
from .serializers import (
    BranchSerializer,
    ChangePasswordSerializer,
    CRMFollowupSerializer,
    EnquirySerializer,
    ForgotPasswordRequestSerializer,
    ForgotPasswordVerifySerializer,
    InterestOptionSerializer,
    UserProfileSerializer,
    UserSerializer,
)

User = get_user_model()


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'per_page'
    max_page_size = 200

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'per_page': self.get_page_size(self.request),
            'results': data,
        })


# ==========================================
# Authentication & User Profile APIs
# ==========================================
class LoginAPIView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')

        if not username or not password:
            return Response(
                {'error': 'Both username and password are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, username=username, password=password)
        if not user:
            return Response(
                {'error': 'Invalid username or password.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {'error': 'This user account is inactive.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        refresh = RefreshToken.for_user(user)
        user_data = UserProfileSerializer(user, context={'request': request}).data

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': user_data,
        })


class CurrentUserAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user, context={'request': request})
        return Response(serializer.data)


class UserProfileAPIView(views.APIView):
    """
    GET: Retrieve full profile with stats for the authenticated user.
    PATCH: Update editable personal fields (name, email, dob, dist, taluka, village).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordAPIView(views.APIView):
    """
    POST: Change password for the authenticated user.
    Requires old_password, new_password, confirm_password.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']

        if not user.check_password(old_password):
            return Response(
                {'old_password': ['Current password is incorrect.']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()

        return Response({'message': 'Password updated successfully.'})


class ForgotPasswordRequestOTPAPIView(views.APIView):
    """
    POST: Generate OTP for password reset. Identifier can be mobile number or email.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        identifier = serializer.validated_data['identifier'].strip()
        user = User.objects.filter(Q(mobile_number=identifier) | Q(email__iexact=identifier)).first()

        if not user:
            return Response(
                {'error': 'No active user account found with this mobile number or email.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Invalidate old OTPs
        PasswordResetOTP.objects.filter(user=user).delete()

        # Generate new OTP
        otp_code = PasswordResetOTP.generate_otp(length=6)
        PasswordResetOTP.objects.create(user=user, otp=otp_code)

        if user.email:
            from WebApp.views import send_password_forgat_email_in_background
            subject = "Your Password Reset OTP - VR Academy Hub"
            message = f"""
            <html>
            <body style="font-family: 'Segoe UI', Arial, sans-serif; background-color: #f4f6f8; margin: 0; padding: 40px 0;">
                <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" 
                       style="max-width: 600px; background-color: #ffffff; border-radius: 12px; 
                              overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.08);">
                    <tr>
                        <td align="center" style="background: linear-gradient(135deg, #2563eb, #4f46e5); padding: 25px 0;">
                            <h1 style="color: #ffffff; margin: 0; font-size: 24px; letter-spacing: 1px;">VR Academy Hub</h1>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 30px; color: #333333;">
                            <p style="font-size: 16px;">Hello <strong>{user.name or user.mobile_number}</strong>,</p>
                            <p style="font-size: 15px; line-height: 1.6;">
                                We received a request to reset your password. Please use the One-Time Password (OTP) below to proceed:
                            </p>
                            <p style="text-align: center; margin: 30px 0;">
                                <span style="display: inline-block; font-size: 30px; font-weight: 800; color: #2563eb; 
                                            background-color: #eef2ff; border: 2px dashed #6366f1; padding: 14px 36px; border-radius: 10px; 
                                            letter-spacing: 4px;">
                                    {otp_code}
                                </span>
                            </p>
                            <p style="font-size: 14px; color: #555;">
                                This code is valid for <strong>15 minutes</strong>.
                            </p>
                            <p style="font-size: 14px; color: #555;">
                                Your login username: <strong>{user.mobile_number}</strong>
                            </p>
                        </td>
                    </tr>
                </table>
            </body>
            </html>
            """
            send_password_forgat_email_in_background(
                subject=subject,
                message=message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'vrtrainingacademy@gmail.com'),
                recipient_list=[user.email],
            )

        return Response({
            'message': f'Password reset OTP sent to {user.email or identifier}.',
            'identifier': identifier,
            'otp_debug': otp_code,
        })


class ForgotPasswordVerifyOTPAPIView(views.APIView):
    """
    POST: Verify OTP and reset user password.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        identifier = serializer.validated_data['identifier'].strip()
        otp = serializer.validated_data['otp'].strip()
        new_password = serializer.validated_data['new_password']

        user = User.objects.filter(Q(mobile_number=identifier) | Q(email__iexact=identifier)).first()
        if not user:
            return Response(
                {'error': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        otp_record = PasswordResetOTP.objects.filter(user=user, otp=otp).order_by('-created_at').first()
        if not otp_record or not otp_record.is_valid(minutes_valid=15):
            return Response(
                {'otp': ['Invalid or expired OTP. Please request a new one.']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()

        # Invalidate used OTP
        otp_record.delete()

        return Response({'message': 'Password reset successful. You can now sign in with your new password.'})


# ==========================================
# CRM Follow-ups APIs
# ==========================================
def apply_followup_filters(queryset, params):
    search_query = params.get('search', '').strip()
    status_filter = params.get('status', '').strip()
    priority_filter = params.get('priority', '').strip()
    branch = params.get('branch', '').strip()
    address = params.get('address', '').strip()

    # 1. Record Created Date Range (start - end)
    created_from = params.get('created_from', '').strip()
    created_to = params.get('created_to', '').strip()

    # 2. Next Followup Date Range (start - end)
    next_followup_from = params.get('next_followup_from', '').strip() or params.get('followup_from', '').strip()
    next_followup_to = params.get('next_followup_to', '').strip() or params.get('followup_to', '').strip()

    # General / Legacy date filters
    date_from = params.get('date_from', '').strip()
    date_to = params.get('date_to', '').strip()

    if search_query:
        digits = re.sub(r'\D', '', search_query)
        search_filter = (
            Q(name__icontains=search_query) |
            Q(mobile_number__icontains=search_query) |
            Q(follow_up_notes__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(student_interested_for__interest_option__icontains=search_query)
        )
        if digits:
            search_filter |= Q(mobile_number__icontains=digits)
            if len(digits) >= 10:
                search_filter |= Q(mobile_number__icontains=digits[-10:])
        queryset = queryset.filter(search_filter)

    if status_filter:
        queryset = queryset.filter(status=status_filter)

    if priority_filter:
        queryset = queryset.filter(priority=priority_filter)

    if branch:
        queryset = queryset.filter(branch=branch)

    if address:
        queryset = queryset.filter(address__icontains=address)

    # Apply Created Date Filter (Start - End)
    if created_from:
        try:
            created_from_obj = datetime.strptime(created_from, '%Y-%m-%d').date()
            queryset = queryset.filter(created_at__date__gte=created_from_obj)
        except ValueError:
            pass

    if created_to:
        try:
            created_to_obj = datetime.strptime(created_to, '%Y-%m-%d').date()
            queryset = queryset.filter(created_at__date__lte=created_to_obj)
        except ValueError:
            pass

    # Apply Next Follow-up Date Filter (Start - End)
    if next_followup_from:
        try:
            next_followup_from_obj = datetime.strptime(next_followup_from, '%Y-%m-%d').date()
            queryset = queryset.filter(next_followup_reminder__date__gte=next_followup_from_obj)
        except ValueError:
            pass

    if next_followup_to:
        try:
            next_followup_to_obj = datetime.strptime(next_followup_to, '%Y-%m-%d').date()
            queryset = queryset.filter(next_followup_reminder__date__lte=next_followup_to_obj)
        except ValueError:
            pass

    # Legacy fallback
    if date_from and not created_from and not next_followup_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            queryset = queryset.filter(
                Q(follow_up_date__date__gte=date_from_obj) | Q(created_at__date__gte=date_from_obj) | Q(next_followup_reminder__date__gte=date_from_obj)
            )
        except ValueError:
            pass

    if date_to and not created_to and not next_followup_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            queryset = queryset.filter(
                Q(follow_up_date__date__lte=date_to_obj) | Q(created_at__date__lte=date_to_obj) | Q(next_followup_reminder__date__lte=date_to_obj)
            )
        except ValueError:
            pass

    return queryset


class CRMFollowupStatsAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = CRMFollowup.objects.all()
        qs = apply_followup_filters(qs, request.query_params)

        today = date.today()
        now = timezone.now()

        total_leads = qs.count()
        high_priority = qs.filter(priority='high').count()
        today_followups = qs.filter(follow_up_date__date=today).count()
        pending_followups = qs.filter(next_followup_reminder__lt=now).count()

        return Response({
            'total_leads': total_leads,
            'high_priority': high_priority,
            'pending_followups': pending_followups,
            'today_followups': today_followups,
        })


class CRMFollowupListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CRMFollowupSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = CRMFollowup.objects.all()
        params = self.request.query_params

        # Base filters
        queryset = apply_followup_filters(queryset, params)

        # Grid Filter
        grid_filter = params.get('grid_filter', '').strip()
        if grid_filter == 'high_priority':
            queryset = queryset.filter(priority='high')
        elif grid_filter == 'pending_followups':
            queryset = queryset.filter(next_followup_reminder__lt=timezone.now())
        elif grid_filter == 'today_followups':
            queryset = queryset.filter(follow_up_date__date=date.today())

        # Sorting
        sort_field = params.get('sort', '').strip()
        sort_order = params.get('order', 'asc').strip()
        sort_map = {
            'name': 'name',
            'mobile': 'mobile_number',
            'status': 'status',
            'priority': 'priority',
            'next_followup': 'next_followup_reminder',
            'branch': 'branch__branch_name',
            'followup_by': 'follow_up_by__first_name',
        }

        if sort_field in sort_map:
            db_field = sort_map[sort_field]
            if sort_order == 'desc':
                queryset = queryset.order_by(F(db_field).desc(nulls_last=True))
            else:
                queryset = queryset.order_by(F(db_field).asc(nulls_last=True))
        else:
            queryset = queryset.order_by('-follow_up_date')

        return queryset

    def perform_create(self, serializer):
        kwargs = {
            'follow_up_by': self.request.user,
        }
        if not serializer.validated_data.get('follow_up_date'):
            kwargs['follow_up_date'] = timezone.now()
        instance = serializer.save(**kwargs)
        if self.request.user and self.request.user.is_authenticated:
            instance._history_user = self.request.user


class CRMFollowupDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CRMFollowup.objects.all()
    serializer_class = CRMFollowupSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        kwargs = {}
        if self.request.user and self.request.user.is_authenticated:
            kwargs['follow_up_by'] = self.request.user
            kwargs['follow_up_date'] = timezone.now()
        instance = serializer.save(**kwargs)
        if self.request.user and self.request.user.is_authenticated:
            instance._history_user = self.request.user


class CRMFollowupRecordAPIView(views.APIView):
    """
    API endpoint to record a follow-up interaction.
    Updates the follow-up note, call response, status, priority, and next reminder.
    Automatically sets follow_up_by to current user and follow_up_date to now.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            followup = CRMFollowup.objects.get(pk=pk)
        except CRMFollowup.DoesNotExist:
            return Response({'error': 'Follow-up not found.'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        if 'follow_up_notes' in data:
            followup.follow_up_notes = data['follow_up_notes']
        if 'call_response' in data and data['call_response']:
            followup.call_response = data['call_response']
        if 'status' in data and data['status']:
            followup.status = data['status']
        if 'priority' in data and data['priority']:
            followup.priority = data['priority']
        if 'next_followup_reminder' in data:
            val = data['next_followup_reminder']
            if isinstance(val, str) and val.strip():
                from django.utils.dateparse import parse_datetime
                dt = parse_datetime(val)
                if dt:
                    if timezone.is_naive(dt):
                        dt = timezone.make_aware(dt)
                    if dt < timezone.now() - timezone.timedelta(minutes=15):
                        return Response(
                            {'next_followup_reminder': ['Next follow-up reminder cannot be set in the past.']},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    followup.next_followup_reminder = dt
            elif val is None or val == '':
                followup.next_followup_reminder = None
            elif isinstance(val, datetime):
                dt = val
                if timezone.is_naive(dt):
                    dt = timezone.make_aware(dt)
                if dt < timezone.now() - timezone.timedelta(minutes=15):
                    return Response(
                        {'next_followup_reminder': ['Next follow-up reminder cannot be set in the past.']},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                followup.next_followup_reminder = dt
        if 'branch' in data and data['branch']:
            followup.branch_id = data['branch']
        if 'student_interested_for' in data and data['student_interested_for']:
            followup.student_interested_for_id = data['student_interested_for']

        followup.follow_up_by = request.user
        followup.follow_up_date = timezone.now()
        followup._history_user = request.user
        followup.save()

        serializer = CRMFollowupSerializer(followup)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ==========================================
# Master Data APIs
# ==========================================
class CRMChoicesAPIView(views.APIView):
    """
    Returns all dynamic model choices and metadata for the CRM.
    Ensures frontend has zero hardcoded choices.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        status_choices = [{'value': k, 'label': v} for k, v in CRMFollowup.STATUS]
        priority_choices = [{'value': k, 'label': v} for k, v in CRMFollowup.PRIORITY_CHOICES]
        call_response_choices = [{'value': k, 'label': v} for k, v in CRMFollowup.CALL_RESPONSE_CHOICES]
        source_choices = [{'value': k, 'label': v} for k, v in CRMFollowup.SOURCE_CHOICES]
        role_choices = [{'value': k, 'label': v} for k, v in getattr(User, 'ROLE_CHOICES', [])]
        branches = BranchSerializer(Branch.objects.all(), many=True).data
        interests = InterestOptionSerializer(CRM_Student_Interested_for_options.objects.all(), many=True).data

        return Response({
            'status_choices': status_choices,
            'priority_choices': priority_choices,
            'call_response_choices': call_response_choices,
            'source_choices': source_choices,
            'role_choices': role_choices,
            'branches': branches,
            'interests': interests,
        })


class BranchListAPIView(generics.ListAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None


class InterestOptionListAPIView(generics.ListAPIView):
    queryset = CRM_Student_Interested_for_options.objects.all()
    serializer_class = InterestOptionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None


# ==========================================
# Enquiry APIs
# ==========================================
class EnquiryListAPIView(generics.ListAPIView):
    queryset = Enquiry.objects.all().order_by('-submitted_at')
    serializer_class = EnquirySerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]


class EnquiryConvertToFollowupAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            enquiry = Enquiry.objects.get(pk=pk)
        except Enquiry.DoesNotExist:
            return Response({'error': 'Enquiry not found.'}, status=status.HTTP_404_NOT_FOUND)

        followup = CRMFollowup.objects.create(
            name=enquiry.full_name,
            mobile_number=enquiry.phone,
            source='website',
            status='interested',
            priority='medium',
            follow_up_notes=f"Converted from website enquiry. Message: {enquiry.message or ''}",
            follow_up_by=request.user,
        )
        enquiry.is_added_in_CRMFollowup_model = True
        enquiry.save()

        serializer = CRMFollowupSerializer(followup)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
