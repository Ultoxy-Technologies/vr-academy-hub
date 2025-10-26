from django import forms
from AdminApp.models import CustomUser


from django import forms
from django.core.exceptions import ValidationError

class CustomUserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'}),
        label="Password"
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password'}),
        label="Confirm Password"
    )

    class Meta:
        model = CustomUser
        fields = [
            'username',
            'name',
            'dob',
            'dist',
            'taluka',
            'village',
            'mobile_number',
            'email',
            'password',
        ]
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'name': forms.TextInput(attrs={'placeholder': 'Full Name'}),
            'mobile_number': forms.TextInput(attrs={'placeholder': 'Mobile Number'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email Address'}),
            'dist': forms.TextInput(attrs={'placeholder': 'District'}),
            'taluka': forms.TextInput(attrs={'placeholder': 'Taluka'}),
            'village': forms.TextInput(attrs={'placeholder': 'Village'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise ValidationError("Full name is required.")
        return name

    def clean_mobile_number(self):
        mobile = self.cleaned_data.get('mobile_number')
        if not mobile:
            raise ValidationError("Mobile number is required.")
        if not mobile.isdigit():
            raise ValidationError("Mobile number must contain only digits.")
        if CustomUser.objects.filter(mobile_number=mobile).exists():
            raise ValidationError("This mobile number is already registered.")
        return mobile

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError("Email is required.")
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error("password_confirm", "Passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user

