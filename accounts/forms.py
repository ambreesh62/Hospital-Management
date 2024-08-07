from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, BlogPost
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
import re
from django.contrib.auth.forms import AuthenticationForm
# from .models import BlogPost, Category



class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=True)
    profile_picture = forms.ImageField(required=False)
    address_line1 = forms.CharField(max_length=255, required=True)
    city = forms.CharField(max_length=100, required=True)
    state = forms.CharField(max_length=100, required=True)
    pincode = forms.CharField(max_length=10, required=True)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
            "profile_picture",
            "address_line1",
            "city",
            "state",
            "pincode",
        )


# CustomUser = get_user_model()


class SignUpForm(UserCreationForm):
    USER_TYPE_CHOICES = (
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    )
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, required=True)
    profile_picture = forms.ImageField(required=False)
    address_line1 = forms.CharField(max_length=255, required=False)
    city = forms.CharField(max_length=100, required=False)
    state = forms.CharField(max_length=100, required=False)
    pincode = forms.CharField(max_length=10, required=False)
    first_name = forms.CharField(max_length=30, required=True, label='First Name')
    last_name = forms.CharField(max_length=30, required=True, label='Last Name')

    class Meta:
        model = CustomUser
        fields = (
            'first_name', 'last_name','username', 'email', 'password1', 'password2',
            'profile_picture', 'address_line1', 'city', 'state', 'pincode', 'user_type'
        )


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(max_length=254, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)


# accounts/forms.py

from django import forms
from .models import Doctor, Patient


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ["user", "specialty", "available_times", "profile_picture", "bio"]


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ["user", "name",  "medical_history", "gender", "address"]


# forms.py
from django import forms
from .models import Appointment


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['date', 'start_time', 'end_time', 'specialty']  
    start_time = forms.TimeField(
        widget=forms.TimeInput(format='%H:%M'),
        input_formats=['%H:%M', '%I:%M%p']
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(format='%H:%M'),
        input_formats=['%H:%M', '%I:%M%p']
    )    


class EditDoctorProfileForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ["profile_picture", "specialty", "bio", "available_times"]



class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ['specialty', 'available_times', 'profile_picture', 'bio']


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'image', 'category', 'summary', 'content', 'is_draft']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'is_draft': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }