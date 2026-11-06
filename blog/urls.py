from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("post/<slug:slug>/", views.post_detail, name="post_detail"),
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/new/", views.create_post, name="create_post"),
    path("dashboard/<int:pk>/edit/", views.edit_post, name="edit_post"),
    path("dashboard/<int:pk>/delete/", views.delete_post, name="delete_post"),
]
