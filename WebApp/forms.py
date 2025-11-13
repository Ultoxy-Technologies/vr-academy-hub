from django import forms
from AdminApp.models import CustomUser, EventRegistration
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

 
from django.contrib.auth import authenticate 

class CustomUserLoginForm(forms.Form):
    mobile_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter Mobile Number',
            'class': 'form-control'
        }),
        label="Mobile Number"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter Password',
            'class': 'form-control'
        }),
        label="Password"
    )

    def clean(self):
        cleaned_data = super().clean()
        mobile_number = cleaned_data.get('mobile_number')
        password = cleaned_data.get('password')

        if mobile_number and password:
            # Authenticate user
            user = authenticate(mobile_number=mobile_number, password=password)
            if not user:
                raise forms.ValidationError("Invalid mobile number or password.")
            elif not user.is_active:
                raise forms.ValidationError("This account is inactive.")
            
            cleaned_data['user'] = user  # store user for later use
        return cleaned_data

 
class EventRegistrationForm(forms.ModelForm):
    class Meta:
        model = EventRegistration
        fields = ['full_name', 'email', 'mobile_number', 'address', 'special_requirements']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address'
            }),
            'mobile_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your mobile number'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your complete address',
                'rows': 3
            }),
            'special_requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Any special requirements or questions?',
                'rows': 3
            }),
        }
        labels = {
            'full_name': 'Full Name',
            'email': 'Email Address',
            'mobile_number': 'Mobile Number',
            'address': 'Complete Address',
            'special_requirements': 'Special Requirements',
        }

