from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from AdminApp.models import CRMFollowup, Branch, CRM_Student_Interested_for_options, Enquiry

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'role', 'role_display', 'name', 'profile_image', 'mobile_number',
            'dob', 'dist', 'taluka', 'village', 'is_active', 'is_staff', 'is_superuser',
            'date_joined', 'last_login', 'full_name'
        ]

    def get_full_name(self, obj):
        name = getattr(obj, 'name', '')
        if not name:
            name = f"{getattr(obj, 'first_name', '')} {getattr(obj, 'last_name', '')}".strip()
        return name if name else getattr(obj, 'mobile_number', str(obj))

    def get_profile_image(self, obj):
        if hasattr(obj, 'profile_image') and obj.profile_image:
            try:
                request = self.context.get('request')
                if request is not None:
                    return request.build_absolute_uri(obj.profile_image.url)
                return obj.profile_image.url
            except Exception:
                return None
        return None


class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    assigned_leads_count = serializers.SerializerMethodField()
    recorded_followups_count = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'name',
            'full_name',
            'profile_image',
            'mobile_number',
            'email',
            'role',
            'role_display',
            'dob',
            'dist',
            'taluka',
            'village',
            'is_active',
            'is_staff',
            'is_superuser',
            'date_joined',
            'last_login',
            'assigned_leads_count',
            'recorded_followups_count',
        ]
        read_only_fields = [
            'id',
            'mobile_number',
            'role',
            'role_display',
            'is_active',
            'is_staff',
            'is_superuser',
            'date_joined',
            'last_login',
            'assigned_leads_count',
            'recorded_followups_count',
        ]

    def get_full_name(self, obj):
        name = getattr(obj, 'name', '')
        if not name:
            name = f"{getattr(obj, 'first_name', '')} {getattr(obj, 'last_name', '')}".strip()
        return name if name else getattr(obj, 'mobile_number', str(obj))

    def get_assigned_leads_count(self, obj):
        try:
            return CRMFollowup.objects.filter(follow_up_by=obj).count()
        except Exception:
            return 0

    def get_recorded_followups_count(self, obj):
        try:
            return CRMFollowup.history.filter(history_user=obj).count()
        except Exception:
            return 0

    def get_profile_image(self, obj):
        if hasattr(obj, 'profile_image') and obj.profile_image:
            try:
                request = self.context.get('request')
                if request is not None:
                    return request.build_absolute_uri(obj.profile_image.url)
                return obj.profile_image.url
            except Exception:
                return None
        return None


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, min_length=6, write_only=True)
    confirm_password = serializers.CharField(required=True, min_length=6, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "New passwords do not match."})
        return attrs


class ForgotPasswordRequestSerializer(serializers.Serializer):
    identifier = serializers.CharField(required=True, help_text="Mobile number or email")


class ForgotPasswordVerifySerializer(serializers.Serializer):
    identifier = serializers.CharField(required=True, help_text="Mobile number or email")
    otp = serializers.CharField(required=True, max_length=6, min_length=4)
    new_password = serializers.CharField(required=True, min_length=6)
    confirm_password = serializers.CharField(required=True, min_length=6)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "New passwords do not match."})
        return attrs


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['id', 'branch_name']


class InterestOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CRM_Student_Interested_for_options
        fields = ['id', 'interest_option']


class CRMFollowupHistorySerializer(serializers.ModelSerializer):
    history_user_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    call_response_display = serializers.CharField(source='get_call_response_display', read_only=True)

    class Meta:
        model = CRMFollowup.history.model
        fields = [
            'history_id',
            'history_date',
            'history_type',
            'history_user_name',
            'status',
            'status_display',
            'priority',
            'priority_display',
            'call_response',
            'call_response_display',
            'follow_up_date',
            'next_followup_reminder',
            'follow_up_notes',
        ]

    def get_history_user_name(self, obj):
        if obj.history_user:
            name = getattr(obj.history_user, 'name', '')
            if not name:
                name = f"{getattr(obj.history_user, 'first_name', '')} {getattr(obj.history_user, 'last_name', '')}".strip()
            return name if name else getattr(obj.history_user, 'mobile_number', 'Staff')
        return 'System / Staff'


class CRMFollowupSerializer(serializers.ModelSerializer):
    student_interested_for_name = serializers.CharField(source='student_interested_for.interest_option', read_only=True)
    branch_name = serializers.CharField(source='branch.branch_name', read_only=True)
    follow_up_by_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    call_response_display = serializers.CharField(source='get_call_response_display', read_only=True)
    is_overdue = serializers.SerializerMethodField()
    history = serializers.SerializerMethodField()

    class Meta:
        model = CRMFollowup
        fields = [
            'id',
            'name',
            'mobile_number',
            'student_interested_for',
            'student_interested_for_name',
            'source',
            'address',
            'status',
            'status_display',
            'priority',
            'priority_display',
            'branch',
            'branch_name',
            'follow_up_by',
            'follow_up_by_name',
            'call_response',
            'call_response_display',
            'follow_up_date',
            'next_followup_reminder',
            'follow_up_notes',
            'class_start_date',
            'created_at',
            'is_overdue',
            'history',
        ]

    def get_follow_up_by_name(self, obj):
        if obj.follow_up_by:
            name = getattr(obj.follow_up_by, 'name', '')
            if not name:
                name = f"{getattr(obj.follow_up_by, 'first_name', '')} {getattr(obj.follow_up_by, 'last_name', '')}".strip()
            return name if name else getattr(obj.follow_up_by, 'mobile_number', None)
        return None

    def get_is_overdue(self, obj):
        if obj.next_followup_reminder:
            reminder = obj.next_followup_reminder
            if isinstance(reminder, str):
                from django.utils.dateparse import parse_datetime
                reminder = parse_datetime(reminder)
            if reminder and timezone.is_aware(reminder):
                return reminder < timezone.now()
            elif reminder:
                return reminder < timezone.now().replace(tzinfo=None)
        return False

    def validate_next_followup_reminder(self, value):
        if value and value < timezone.now() - timezone.timedelta(hours=6):
            raise serializers.ValidationError("Next follow-up reminder cannot be set in the past.")
        return value

    def get_history(self, obj):
        try:
            records = obj.history.all().order_by('-history_date')
            return CRMFollowupHistorySerializer(records, many=True).data
        except Exception:
            return []


class EnquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Enquiry
        fields = '__all__'
