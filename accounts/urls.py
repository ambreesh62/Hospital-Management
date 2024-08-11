from django.urls import path

from . import views
from .views import (
    doctor_dashboard_view,
    view_doctor_view,
    edit_doctor_view,
    delete_doctor_view,
    profile_view,
    signup_view,
    login_view,
    home_view,
    logout_view,
    update_doctor_profile_view,
    patient_dashboard_view,
    error_page,
    about,
    edit_blog_post,
    edit_patient_profile,
)

urlpatterns = [
    path("", home_view, name="home"),
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path("doctor_dashboard/", doctor_dashboard_view, name="doctor_dashboard"),
    path("patient_dashboard/", patient_dashboard_view, name="patient_dashboard"),
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
    path('doctor_blogs/', views.doctor_blogs_view, name='doctor_blogs'),
    path('view_blog/', views.view_blog_view, name='view_blog'),
    path('category_blogs/<int:category_id>/', views.category_blogs_view, name='category_blogs_view'),
    path('post/<int:id>/', views.post_detail_view, name='post_detail'), 
    path('edit_blog_post/<int:post_id>/', edit_blog_post, name='edit_blog_post'),

    # new
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('book_appointment/<int:doctor_id>/', views.book_appointment_view, name='book_appointment'),

    path('appointment-confirmation/<int:appointment_id>/', views.appointment_confirmation_view, name='appointment_confirmation'),
    path('doctor_dashboard/<int:doctor_id>/', doctor_dashboard_view, name='doctor_dashboard'),
    path('appointment/<int:id>/', views.view_appointment, name='view_appointment'),
    path('appointment/<int:appointment_id>/accept/', views.accept_appointment, name='accept_appointment'),
    path('appointment/<int:appointment_id>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('patient/edit/<int:id>/', edit_patient_profile, name='edit_patient_profile'),
    path('profile/doctor/<int:doctor_id>/', views.profile_view, name='profile_doctor_by_id'),
    path('profile/patient/<int:patient_id>/', views.profile_view, name='profile_patient_by_id'),

    path("profile/<int:patient_id>/", profile_view, name="profile"),
    path('profile/<int:patient_id>/', views.profile_view, name='profile_view'),


    




]
