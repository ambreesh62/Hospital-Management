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
    DoctorProfileForm
)
from .models import Doctor, Appointment
import json
from .forms import SignUpForm
from django.contrib.auth.models import Group
from django.contrib.auth import logout


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


def logout_view(request):
    logout(request)
    return redirect('home') 


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

    return render(request, "create_appointment.html")


@login_required
def view_appointment(request, id):
    appointment = get_object_from_list(appointments_data, id=id)
    context = {"appointment": appointment}
    return render(request, "view_appointment.html", context)


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


def doctor_dashboard_view(request):
    # Ensure you are getting the Doctor instance for the logged-in user
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        return render(request, "error.html", {"message": "Doctor profile not found."})

    # Query appointments associated with this doctor
    appointments = Appointment.objects.filter(doctor=doctor)

    return render(
        request,
        "doctor_dashboard.html",
        {"doctor": doctor, "appointments": appointments},
    )


@login_required
def book_appointment(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    if request.method == "POST":
        date = request.POST.get("date")
        time = request.POST.get("time")

        # Ensure the user has a related Patient profile
        try:
            patient = Patient.objects.get(user=request.user)
        except Patient.DoesNotExist:
            messages.error(request, "Patient profile not found.")
            return redirect(
                "error_page"
            )  # Adjust this to your actual error handling URL

        # Create the appointment
        Appointment.objects.create(doctor=doctor, patient=patient, date=date, time=time)

        messages.success(request, "Appointment booked successfully!")
        return redirect("doctor_dashboard")  # Adjust redirection as needed

    return render(request, "book_appointment.html", {"doctor": doctor})


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


# @login_required
# def profile_view(request):
#     doctor = get_object_or_404(Doctor, user=request.user)
#     context = {
#         "doctor": doctor,
#     }
#     return render(request, "doctor_profile.html", context)


# def logout_view(request):
#     logout(request)
#     return redirect("home")

@login_required
def profile_view(request, doctor_id=None):
    try:
        if request.user.user_type == 'doctor':
            profile = get_object_or_404(Doctor, id=doctor_id)
        elif request.user.user_type == 'patient':
            profile = get_object_or_404(Patient, user=request.user)
        else:
            messages.error(request, "User type is not recognized.")
            return redirect("home")
    except (Doctor.DoesNotExist, Patient.DoesNotExist):
        messages.error(request, "Profile does not exist.")
        return redirect("home")

    context = {
        "user": request.user,
        "profile": profile,
    }
    return render(request, "profile.html", context)


def patient_dashboard_view(request):
    user = request.user
    doctors = Doctor.objects.all()
    context = {
        "user": user,
        "doctors": doctors,
    }
    return render(request, "patient_dashboard.html", context)


@login_required
def doctor_dashboard_view(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        messages.error(request, "You are not authorized to view this page.")
        return redirect("home")  # Redirect to the home page or an appropriate page

    # Retrieve appointments related to the doctor
    appointments = Appointment.objects.filter(doctor=doctor)

    # Fetch all doctors for the doctor list
    doctors = Doctor.objects.all()

    context = {
        "user": request.user,
        "doctor": doctor,
        "appointments": appointments,
        "doctors": doctors,
    }
    return render(request, "doctor_dashboard.html", context)


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
    try:
        doctor = get_object_or_404(Doctor, user=request.user)
    except Doctor.DoesNotExist:
        messages.error(request, "Doctor profile does not exist.")
        return redirect("home")

    if request.method == "POST":
        form = DoctorProfileForm(request.POST, request.FILES, instance=doctor)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("profile")
    else:
        form = DoctorProfileForm(instance=doctor)

    context = {
        "form": form,
    }
    return render(request, "update_doctor_profile.html", context)


def view_doctor_view(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    return render(request, "view_doctor.html", {"doctor": doctor})
