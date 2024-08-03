from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Patient, Appointment


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "profile_picture",
                    "address_line1",
                    "city",
                    "state",
                    "pincode",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
        ("User Type", {"fields": ("user_type",)}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "password1",
                    "password2",
                    "user_type",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
    )


admin.site.register(CustomUser, CustomUserAdmin)


# class PatientAdmin(admin.ModelAdmin):
#     list_display = ('user', 'date_of_birth', 'gender', 'address')  # Make sure these fields exist in your model

# admin.site.register(Patient, PatientAdmin)


from .models import BlogPost, Category

admin.site.register(BlogPost)
admin.site.register(Category)