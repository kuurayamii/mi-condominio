from django.urls import path

from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    # TODO: Borrar esta ruta después cuando ya no sea necesaria
    # path("old/", views.index, name="index"),
]