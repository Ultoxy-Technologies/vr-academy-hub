from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """
    Form for creating a new CustomUser in Django Admin.
    Properly hashes password and validates required fields.
    """
    class Meta:
        model = CustomUser
        fields = ('mobile_number', 'name', 'email', 'role')

    def clean_mobile_number(self):
        mobile = self.cleaned_data.get('mobile_number')
        if not mobile:
            raise forms.ValidationError("Mobile number is required.")
        if CustomUser.objects.filter(mobile_number=mobile).exists():
            raise forms.ValidationError("A user with this mobile number already exists.")
        return mobile


class CustomUserChangeForm(UserChangeForm):
    """
    Form for editing an existing CustomUser in Django Admin.
    Includes Django's ReadOnlyPasswordHashField with the password reset link.
    """
    class Meta:
        model = CustomUser
        fields = '__all__'
