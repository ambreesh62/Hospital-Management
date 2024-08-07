from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from accounts.forms import AuthenticationForm
from django.contrib.auth import authenticate, login as auth_login
from .models import Patient, Appointment
from django.http import Http404
from .forms import (
    SignUpForm,
    DoctorForm,
    PatientForm,
    AppointmentForm,
    EditDoctorProfileForm,
)
from .models import Doctor, Appointment,CustomUser
import json
from .forms import SignUpForm
from django.contrib.auth.models import Group
from django.contrib.auth import logout
from .utils import create_google_calendar_event
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import google.auth.exceptions




def home_view(request):
    return render(request, "home.html")


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            user_type = form.cleaned_data.get('user_type')
            if user_type == 'doctor':
                Doctor.objects.create(user=user)
            elif user_type == 'patient':
                Patient.objects.create(user=user)
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
        else:
            # Collect all errors from form
            errors = form.errors.as_data()
            for field, field_errors in errors.items():
                for error in field_errors:
                    messages.error(request, f"Error in {field}: {error.message}")
    else:
        form = SignUpForm()

    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        print("POST data:", request.POST)
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            print("Authenticated user:", user)
            auth_login(request, user)
            messages.success(request, "User login successfully!")

            # Redirect to the appropriate dashboard based on user type
            if user.user_type == "doctor":
                return redirect(reverse("doctor_dashboard"))
            elif user.user_type == "patient":
                return redirect(reverse("patient_dashboard"))
            else:
                return redirect(reverse("home"))
        else:
            print("Form errors:", form.errors)
            messages.error(request, "Invalid username or password")
    else:
        form = AuthenticationForm()

    return render(request, "login.html", {"form": form})


# Dummy data to simulate database records
appointments_data = [
    {
        "id": 1,
        "doctor_name": "Dr. Smith",
        "date": "2024-07-30",
        "time": "10:00",
        "status": "Confirmed",
    },
    # Add more appointments if needed
]

medical_history_data = [
    {
        "date": "2024-01-15",
        "doctor_name": "Dr. John",
        "diagnosis": "Flu",
        "prescription": "Rest, Fluids",
    },
    # Add more medical history records if needed
]


def get_object_from_list(data_list, **kwargs):
    for item in data_list:
        if all(item.get(k) == v for k, v in kwargs.items()):
            return item
    raise Http404


@login_required
def patient_dashboard_view(request):
    user = request.user
    appointments = [
        {
            "id": 1,
            "doctor_name": "Dr. Smith",
            "date": "2024-07-30",
            "time": "10:00",
            "status": "Confirmed",
        },
        # Add more appointments if needed
    ]
    medical_history = [
        {
            "date": "2024-01-15",
            "doctor_name": "Dr. John",
            "diagnosis": "Flu",
            "prescription": "Rest, Fluids",
        },
        # Add more medical history records if needed
    ]
    doctors = Doctor.objects.all()  # Fetch all doctors

    context = {
        "user": user,
        "appointments": appointments,
        "medical_history": medical_history,
        "doctors": doctors,  # Add available doctors to context
    }
    return render(request, "patient_dashboard.html", context)


@login_required
def create_appointment(request):
    if request.method == "POST":
        doctor_id = request.POST.get("doctor")
        date = request.POST.get("date")
        time = request.POST.get("time")

        doctor = get_object_or_404(User, id=doctor_id)
        appointment = Appointment.objects.create(
            doctor=doctor,
            patient=request.user,  # Assuming the patient is the logged-in user
            date=date,
            time=time,
        )

        messages.success(request, "Appointment created successfully!")
        return redirect("patient_dashboard")  # Adjust redirection as needed

    return render(request, "create_appointment.html", appointment)



@login_required
def edit_appointment(request, id):
    appointment = get_object_from_list(appointments_data, id=id)
    if request.method == "POST":
        doctor = request.POST.get("doctor")
        date = request.POST.get("date")
        time = request.POST.get("time")

        # Update the appointment data
        appointment["doctor_name"] = doctor
        appointment["date"] = date
        appointment["time"] = time

        # Display a success message
        messages.success(request, "Appointment updated successfully!")

        return redirect("patient_dashboard")  # Redirect to the patient dashboard

    context = {"appointment": appointment}
    return render(request, "edit_appointment.html", context)


@login_required
def cancel_appointment(request, id):
    appointment = get_object_from_list(appointments_data, id=id)
    appointments_data.remove(appointment)

    # Display a success message
    messages.success(request, "Appointment canceled successfully!")

    return redirect("patient_dashboard")  # Redirect to the patient dashboard


def about(request):
    return render(request, "about.html")


@login_required
def doctor_dashboard_view(request):
    doctor = get_object_or_404(Doctor, user=request.user)
    
    appointments = Appointment.objects.filter(doctor=doctor)

    # Fetch all doctors (or adjust the query as needed)
    doctors = Doctor.objects.all()
    user = CustomUser.objects.get(id=request.user.id)

    context = {
        'appointments': appointments,
        'doctors': doctors,
        'user': user,
        'doctor' : doctor
    }
    
    return render(request, 'doctor_dashboard.html', context)


@login_required
def book_appointment_view(request, doctor_id):
    doctor = get_object_or_404(CustomUser, id=doctor_id)
    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.doctor = doctor
            appointment.patient = request.user
            appointment.end_time = (datetime.combine(appointment.date, appointment.start_time) + timedelta(minutes=45)).time()
            appointment.save()
            
            try:
                # Create Google Calendar event
                create_google_calendar_event(appointment)
                messages.success(request, "Appointment booked successfully!")
            except FileNotFoundError:
                messages.error(request, "Authorization token not found. Please complete the OAuth2 flow.")
            except google.auth.exceptions.GoogleAuthError as e:
                messages.error(request, f"Failed to create Google Calendar event: {e}")
            
            return redirect('appointment_confirmation', appointment_id=appointment.id)
    else:
        form = AppointmentForm()
    return render(request, 'book_appointment.html', {'form': form, 'doctor': doctor})


def add_doctor(request):
    if request.method == "POST":
        form = DoctorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("doctor_dashboard")  # Adjust to your desired redirect
    else:
        form = DoctorForm()
    return render(request, "add_doctor.html", {"form": form})


def add_patient(request):
    if request.method == "POST":
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Patient added successfully!")
            return redirect("patient_dashboard")  # Adjust the redirect as needed
    else:
        form = PatientForm()
    return render(request, "add_patient.html", {"form": form})


def error_page(request):
    return render(request, "error.html")


@login_required
def profile_view(request):
    doctor = get_object_or_404(Doctor, user=request.user)
    context = {
        "doctor": doctor,
    }
    return render(request, "doctor_profile.html", context)


def logout_view(request):
    logout(request)
    return redirect("home")


def patient_dashboard_view(request):
    user = request.user
    doctors = Doctor.objects.all()
    context = {
        "user": user,
        "doctors": doctors,
    }
    return render(request, "patient_dashboard.html", context)


@login_required
def add_doctor_view(request):
    if request.method == "POST":
        form = DoctorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("doctor_dashboard")
    else:
        form = DoctorForm()
    return render(request, "add_doctor.html", {"form": form})


@login_required
def view_doctor_view(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    return render(request, "view_doctor.html", {"doctor": doctor})


@login_required
def edit_doctor_view(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)

    if request.method == "POST":
        form = EditDoctorProfileForm(request.POST, request.FILES, instance=doctor)
        if form.is_valid():
            form.save()
            return redirect("view_doctor", doctor_id=doctor.id)
        else:
            # Print form errors for debugging
            print(form.errors)
    else:
        form = EditDoctorProfileForm(instance=doctor)

    return render(request, "edit_doctor.html", {"form": form})


@login_required
def delete_doctor_view(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    if request.method == "POST":
        doctor.delete()
        return redirect("doctor_dashboard")
    return render(request, "delete_doctor.html", {"doctor": doctor})


@login_required
def update_doctor_profile_view(request):
    doctor = get_object_or_404(Doctor, user=request.user)
    if request.method == "POST":
        form = EditDoctorProfileForm(request.POST, request.FILES, instance=doctor)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("doctor_profile")  # Redirect to the profile view
    else:
        form = EditDoctorProfileForm(instance=doctor)

    context = {
        "form": form,
    }
    return render(request, "update_doctor_profile.html", context)


def view_doctor_view(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    return render(request, "view_doctor.html", {"doctor": doctor})



# Integrate a blog system within the application created in the previous task. 
# The doctors can upload new blog posts and the patients can view them. 

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import BlogPostForm
from .models import BlogPost, Category

@login_required
def create_blog_post(request):
    if request.user.user_type != 'doctor':
        return redirect('home')  # Redirect non-doctors
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            blog_post = form.save(commit=False)
            blog_post.author = request.user
            blog_post.save()
            messages.success(request, 'Blog post created successfully!')
            return redirect('doctor_dashboard')
    else:
        form = BlogPostForm()
    return render(request, 'create_blog_post.html', {'form': form})



def post_detail_view(request, id):
    post = get_object_or_404(BlogPost, id=id)
    return render(request, 'post_detail.html', {'post': post})


@login_required
def doctor_blogs_view(request):
    if request.user.is_authenticated and request.user.user_type == 'doctor':
        blog_posts = BlogPost.objects.filter(author=request.user, is_draft=False)
        return render(request, 'doctor_blogs.html', {'blog_posts': blog_posts})
    else:
        return redirect('login')


def view_blog_view(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'filtered_posts': {category: category.blogpost_set.filter(is_draft=False) for category in categories}
    }
    return render(request, 'view_blog.html', context)

def category_blogs_view(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    blogs = BlogPost.objects.filter(category=category, is_draft=False)
    return render(request, 'category_blogs.html', {'category': category, 'blogs': blogs})


@login_required
def edit_blog_post(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Blog post edited successfully!')
            return redirect(reverse('post_detail', kwargs={'id': post_id}))
    else:
        form = BlogPostForm(instance=post)
    return render(request, 'edit_blog_post.html', {'form': form})

# New
def doctor_list(request):
    doctors = CustomUser.objects.filter(user_type='Doctor')
    return render(request, 'doctor_list.html', {'doctors': doctors})

@login_required
def appointment_details(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    return render(request, 'appointment_details.html', {'appointment': appointment})

@login_required
def appointment_confirmation_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    context = {
        'appointment': appointment,
    }
    
    return render(request, 'appointment_confirmation.html', context)



def create_google_calendar_event(appointment):
    creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/calendar'])
    service = build('calendar', 'v3', credentials=creds)
    
    event = {
        'summary': f'Appointment with Dr. {appointment.doctor.get_full_name()}',
        'description': f'Specialty: {appointment.specialty}',
        'start': {
            'dateTime': f'{appointment.date}T{appointment.start_time}',
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': f'{appointment.date}T{appointment.end_time}',
            'timeZone': 'UTC',
        },
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    return event

@login_required
def view_appointment(request, id):
    # Fetch the appointment by ID
    appointment = get_object_or_404(Appointment, id=id)
    
    # Prepare the context
    context = {
        'appointment': appointment
    }
    
    return render(request, 'view_appointment.html', context)