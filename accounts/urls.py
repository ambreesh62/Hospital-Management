from django.urls import path

from . import views
from .views import (
    doctor_dashboard_view,
    add_doctor_view,
    view_doctor_view,
    edit_doctor_view,
    delete_doctor_view,
    profile_view,
    signup_view,
    login_view,
    home_view,
    book_appointment,
    logout_view,
    update_doctor_profile_view,
    patient_dashboard_view,
    create_appointment,
    view_appointment,
    edit_appointment,
    cancel_appointment,
    add_patient,
    error_page,
    about,
)

urlpatterns = [
    path("", home_view, name="home"),
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path("doctor_dashboard/", doctor_dashboard_view, name="doctor_dashboard"),
    path("patient_dashboard/", patient_dashboard_view, name="patient_dashboard"),
    path("create_appointment/", create_appointment, name="create_appointment"),
    path("appointment/<int:id>/", view_appointment, name="view_appointment"),
    path("appointment/<int:id>/edit/", edit_appointment, name="edit_appointment"),
    path("appointment/<int:id>/cancel/", cancel_appointment, name="cancel_appointment"),
    path(
        "book-appointment/<int:doctor_id>/", book_appointment, name="book_appointment"
    ),
    path("add_doctor/", add_doctor_view, name="add_doctor"),
    path("add_patient/", add_patient, name="add_patient"),
    path("error/", error_page, name="error_page"),
    path("profile/", profile_view, name="profile"),
    path("profile/<int:doctor_id>/", profile_view, name="profile"),
    path("logout/", logout_view, name="logout"),
    path("view_doctor/<int:doctor_id>/", view_doctor_view, name="view_doctor"),
    path("edit_doctor/<int:doctor_id>/", edit_doctor_view, name="edit_doctor"),
    path("delete_doctor/<int:doctor_id>/", delete_doctor_view, name="delete_doctor"),
    path("update_profile/", update_doctor_profile_view, name="update_doctor_profile"),
    path("about/", about, name="about"),
    path('profile/<int:doctor_id>/', views.profile_view, name='doctor_profile'),  # Handles a specific doctor's profile

    # new
    path('create_blog_post/', views.create_blog_post, name='create_blog_post'),
    path('doctor_blogs/', views.doctor_blogs_view, name='doctor_blogs_view'),
    path('patient_blogs/', views.patient_blogs_view, name='patient_blogs_view'),
    path('category_blogs/<int:category_id>/', views.category_blogs_view, name='category_blogs_view'),

]
