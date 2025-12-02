from django.urls import path

from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    # TODO: Borrar esta ruta después cuando ya no sea necesaria
    # path("old/", views.index, name="index"),
]