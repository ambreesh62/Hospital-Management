from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ("patient", "Patient"),
        ("doctor", "Doctor"),
    )

    user_type = models.CharField(
        max_length=10, choices=USER_TYPE_CHOICES, default="doctor"
    )
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", blank=True, null=True
    )
    address_line1 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)

    groups = models.ManyToManyField(
        Group,
        related_name="customuser_set",  # Use a different related_name to avoid conflict
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="customuser_set",  # Use a different related_name to avoid conflict
        blank=True,
    )

    def __str__(self):
        return self.username


class Doctor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    specialty = models.CharField(max_length=100)
    available_times = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", blank=True, null=True
    )
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.last_name}"  # Use attributes that actually exist


class Patient(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1
    )
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    medical_history = models.TextField()
    address = models.TextField(default="No address provided")  # Default address


class Appointment(models.Model):
    doctor = models.ForeignKey("Doctor", on_delete=models.CASCADE)
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20)

    def __str__(self):
        return f"Appointment with Dr. {self.doctor.user.get_full_name()} on {self.date} at {self.time}"

# New

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='blog_images/')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    summary = models.TextField()
    content = models.TextField()
    is_draft = models.BooleanField(default=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.title