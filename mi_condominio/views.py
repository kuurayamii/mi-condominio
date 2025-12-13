from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from .models import Condominio


# TODO: Borrar esta vista después cuando ya no sea necesaria
# def index(response):
#     return HttpResponse("Hola, estas en el indice de micondominio")


def landing(request):
    """Vista de la landing page"""
    return render(request, 'mi_condominio/landing.html')


def login_view(request):
    """
    Vista para el inicio de sesión de usuarios.
    Autentica al usuario y lo redirige a la página de inicio.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido {user.username}!')
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'mi_condominio/login.html')


@login_required
def logout_view(request):
    """
    Vista para cerrar sesión.
    Cierra la sesión del usuario y lo redirige a la landing page.
    """
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('landing')


@login_required
def dashboard(request):
    """
    Vista principal del dashboard.
    Muestra estadísticas y gráficos del sistema.
    """
    # TODO: Agregar lógica para obtener estadísticas reales de la base de datos
    total_condominios = Condominio.objects.count()

    context = {
        'total_condominios': total_condominios,
        'total_usuarios': 0,
        'incidencias_abiertas': 0,
        'reuniones_proximas': 0,
    }
    return render(request, 'mi_condominio/dashboard/dashboard.html', context)


# ============================================================================
# VISTAS PARA GESTIÓN DE CONDOMINIOS
# ============================================================================

@login_required
def condominio_list(request):
    """
    Vista que muestra el listado de todos los condominios.
    Incluye búsqueda y filtros.
    """
    condominios = Condominio.objects.all()

    # Búsqueda
    search_query = request.GET.get('search', '')
    if search_query:
        condominios = condominios.filter(
            models.Q(nombre__icontains=search_query) |
            models.Q(rut__icontains=search_query) |
            models.Q(comuna__icontains=search_query) |
            models.Q(region__icontains=search_query)
        )

    context = {
        'condominios': condominios,
        'search_query': search_query,
    }
    return render(request, 'mi_condominio/condominios/list.html', context)


@login_required
def condominio_create(request):
    """
    Vista para crear un nuevo condominio.
    """
    if request.method == 'POST':
        # Obtener datos del formulario
        rut = request.POST.get('rut')
        nombre = request.POST.get('nombre')
        direccion = request.POST.get('direccion')
        region = request.POST.get('region')
        comuna = request.POST.get('comuna')
        mail_contacto = request.POST.get('mail_contacto')

        # Validar que no exista un condominio con el mismo RUT
        if Condominio.objects.filter(rut=rut).exists():
            messages.error(request, 'Ya existe un condominio con este RUT.')
        else:
            try:
                # Crear el condominio
                condominio = Condominio.objects.create(
                    rut=rut,
                    nombre=nombre,
                    direccion=direccion,
                    region=region,
                    comuna=comuna,
                    mail_contacto=mail_contacto
                )
                messages.success(request, f'Condominio "{condominio.nombre}" creado exitosamente.')
                return redirect('condominio_list')
            except Exception as e:
                messages.error(request, f'Error al crear el condominio: {str(e)}')

    return render(request, 'mi_condominio/condominios/form.html', {
        'action': 'Crear',
        'condominio': None,
    })


@login_required
def condominio_edit(request, pk):
    """
    Vista para editar un condominio existente.
    """
    condominio = get_object_or_404(Condominio, pk=pk)

    if request.method == 'POST':
        # Obtener datos del formulario
        rut = request.POST.get('rut')
        nombre = request.POST.get('nombre')
        direccion = request.POST.get('direccion')
        region = request.POST.get('region')
        comuna = request.POST.get('comuna')
        mail_contacto = request.POST.get('mail_contacto')

        # Validar que no exista otro condominio con el mismo RUT
        if Condominio.objects.filter(rut=rut).exclude(pk=pk).exists():
            messages.error(request, 'Ya existe otro condominio con este RUT.')
        else:
            try:
                # Actualizar el condominio
                condominio.rut = rut
                condominio.nombre = nombre
                condominio.direccion = direccion
                condominio.region = region
                condominio.comuna = comuna
                condominio.mail_contacto = mail_contacto
                condominio.save()

                messages.success(request, f'Condominio "{condominio.nombre}" actualizado exitosamente.')
                return redirect('condominio_list')
            except Exception as e:
                messages.error(request, f'Error al actualizar el condominio: {str(e)}')

    return render(request, 'mi_condominio/condominios/form.html', {
        'action': 'Editar',
        'condominio': condominio,
    })


@login_required
def condominio_delete(request, pk):
    """
    Vista para eliminar un condominio.
    """
    condominio = get_object_or_404(Condominio, pk=pk)

    if request.method == 'POST':
        nombre = condominio.nombre
        try:
            condominio.delete()
            messages.success(request, f'Condominio "{nombre}" eliminado exitosamente.')
        except Exception as e:
            messages.error(request, f'Error al eliminar el condominio: {str(e)}')
        return redirect('condominio_list')

    return render(request, 'mi_condominio/condominios/delete.html', {
        'condominio': condominio,
    })

