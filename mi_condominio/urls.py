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

    # URLs para gestión de reuniones
    path("reuniones/", views.reunion_list, name="reunion_list"),
    path("reuniones/crear/", views.reunion_create, name="reunion_create"),
    path("reuniones/<int:pk>/editar/", views.reunion_edit, name="reunion_edit"),
    path("reuniones/<int:pk>/eliminar/", views.reunion_delete, name="reunion_delete"),

    # URLs para gestión de usuarios
    path("usuarios/", views.usuario_list, name="usuario_list"),
    path("usuarios/crear/", views.usuario_create, name="usuario_create"),
    path("usuarios/<int:pk>/editar/", views.usuario_edit, name="usuario_edit"),
    path("usuarios/<int:pk>/eliminar/", views.usuario_delete, name="usuario_delete"),

    # URLs para gestión de incidencias
    path("incidencias/", views.incidencia_list, name="incidencia_list"),
    path("incidencias/crear/", views.incidencia_create, name="incidencia_create"),
    path("incidencias/<int:pk>/editar/", views.incidencia_edit, name="incidencia_edit"),
    path("incidencias/<int:pk>/eliminar/", views.incidencia_delete, name="incidencia_delete"),

    # URLs para gestión de categorías
    path("categorias/", views.categoria_list, name="categoria_list"),
    path("categorias/crear/", views.categoria_create, name="categoria_create"),
    path("categorias/<int:pk>/editar/", views.categoria_edit, name="categoria_edit"),
    path("categorias/<int:pk>/eliminar/", views.categoria_delete, name="categoria_delete"),

    # URLs para gestión de bitácora
    path("bitacoras/", views.bitacora_list, name="bitacora_list"),
    path("bitacoras/crear/", views.bitacora_create, name="bitacora_create"),
    path("bitacoras/<int:pk>/editar/", views.bitacora_edit, name="bitacora_edit"),
    path("bitacoras/<int:pk>/eliminar/", views.bitacora_delete, name="bitacora_delete"),

    # URLs para gestión de evidencias
    path("evidencias/", views.evidencia_list, name="evidencia_list"),
    path("evidencias/crear/", views.evidencia_create, name="evidencia_create"),
    path("evidencias/<int:pk>/editar/", views.evidencia_edit, name="evidencia_edit"),
    path("evidencias/<int:pk>/eliminar/", views.evidencia_delete, name="evidencia_delete"),

    # URLs para gestión de amonestaciones
    path("amonestaciones/", views.amonestacion_list, name="amonestacion_list"),
    path("amonestaciones/crear/", views.amonestacion_create, name="amonestacion_create"),
    path("amonestaciones/<int:pk>/editar/", views.amonestacion_edit, name="amonestacion_edit"),
    path("amonestaciones/<int:pk>/eliminar/", views.amonestacion_delete, name="amonestacion_delete"),

    # TODO: Borrar esta ruta después cuando ya no sea necesaria
    # path("old/", views.index, name="index"),
]