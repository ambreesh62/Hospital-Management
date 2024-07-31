from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
import re
from django.contrib.auth.forms import AuthenticationForm


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
    profile_picture = forms.ImageField(required=False) 
    address_line1 = forms.CharField(max_length=255, required=False)
    city = forms.CharField(max_length=100, required=False)
    state = forms.CharField(max_length=100, required=False)
    pincode = forms.CharField(max_length=10, required=False)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'profile_picture','address_line1', 'city', 'state', 'pincode')


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
        fields = ["user", "name", "age", "medical_history", "gender", "address"]


# forms.py
from django import forms
from .models import Appointment


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["date", "time", "status"]


class EditDoctorProfileForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ["profile_picture", "specialty", "bio", "available_times"]
