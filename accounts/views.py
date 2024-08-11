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
    PatientProfileForm
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
from .utils import create_google_calendar_event




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




def get_object_from_list(data_list, **kwargs):
    for item in data_list:
        if all(item.get(k) == v for k, v in kwargs.items()):
            return item
    raise Http404


@login_required
def patient_dashboard_view(request):
    user = request.user

    # Check if the user is a patient
    if user.user_type != 'patient':
        messages.success(request, 'No permission allowed to switch patient dashboard!')
        return redirect('doctor_dashboard')  # or any other appropriate page

    # Retrieve all doctors to display on the dashboard
    doctors = Doctor.objects.all()

    # Pass data to the template
    context = {
        'user': user,
        'doctors': doctors,
    }

    return render(request, 'patient_dashboard.html', context)




def about(request):
    return render(request, "about.html")


@login_required
def doctor_dashboard_view(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        messages.success(request, 'No permission allowed to switch doctor dashboard!')
        return redirect('patient_dashboard')

    # Get the logged-in user
    user = request.user

    # Fetch appointments related to the logged-in doctor
    appointments = Appointment.objects.filter(doctor=doctor)

    # Fetch all doctors (if needed; adjust query as required)
    doctors = Doctor.objects.all()

    # Prepare context data
    context = {
        'appointments': appointments,
        'doctors': doctors,
        'user': user,
        'doctor': doctor,
    }
    
    return render(request, 'doctor_dashboard.html', context)

from django.http import JsonResponse

@login_required
def book_appointment_view(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)  # Ensure this returns a Doctor instance
    
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            form = AppointmentForm(data)
            if form.is_valid():
                appointment = form.save(commit=False)
                appointment.doctor = doctor  # This should be a Doctor instance
                appointment.patient = request.user
                appointment.end_time = (datetime.combine(appointment.date, appointment.start_time) + timedelta(minutes=45)).time()
                appointment.save()

                return JsonResponse({'status': 'success', 'message': 'Appointment booked successfully!'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid form data'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'})
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



def error_page(request):
    return render(request, "error.html")


def profile_view(request):
    doctor = get_object_or_404(Doctor, user=request.user)
    return render(request, 'doctor_profile.html', {'doctor' : doctor}) 
@login_required
def patient_profile_view(request):
    patient = get_object_or_404(Patient, user=request.user)
    return render(request, 'patient_profile.html', {'patient': patient})    

@login_required
def edit_patient_profile(request):
    patient = get_object_or_404(Patient, user=request.user)
    if request.method == 'POST':
        form = PatientProfileForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')  # Redirect to the patient's profile page
    else:
        form = PatientProfileForm(instance=patient)
    
    return render(request, 'edit_patient_profile.html', {'form': form})




def logout_view(request):
    logout(request)
    return redirect("home")




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
        messages.error(request, 'You do not have permission to create Post Blog.')
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
    if request.user.user_type != 'doctor':
        return redirect('home')  # Or any other appropriate action

    blog_posts = BlogPost.objects.filter(author=request.user)
    context = {
        'blog_posts': blog_posts,
    }
    return render(request, 'doctor_blogs.html', context)


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
    if request.user.user_type != 'doctor':
        messages.error(request, 'You do not have permission to edit this post.')
        return redirect('home')  # Redirect to a different page if not a doctor
    
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

from django.http import HttpResponse

@login_required
def view_appointment(request, id):
    try:
        appointment = Appointment.objects.get(id=id)
    except Appointment.DoesNotExist:
        return HttpResponse("Appointment not found.")
    
    context = {
        'appointment': appointment,
    }
    return render(request, 'view_appointment.html', context)

@login_required
def accept_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    # Implement the logic to accept the appointment
    appointment.status = 'Accepted'  # Assuming there's a status field
    appointment.save()
    return redirect('doctor_dashboard')

def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.delete()  # This will delete the appointment
    return redirect('doctor_dashboard')
