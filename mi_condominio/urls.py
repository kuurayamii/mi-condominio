from django.urls import path

from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),

    # URLs para gestión de condominios
    path("condominios/", views.condominio_list, name="condominio_list"),
    path("condominios/crear/", views.condominio_create, name="condominio_create"),
    path("condominios/<int:pk>/editar/", views.condominio_edit, name="condominio_edit"),
    path("condominios/<int:pk>/eliminar/", views.condominio_delete, name="condominio_delete"),

    # TODO: Borrar esta ruta después cuando ya no sea necesaria
    # path("old/", views.index, name="index"),
]