from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages


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
    context = {
        'total_condominios': 0,
        'total_usuarios': 0,
        'incidencias_abiertas': 0,
        'reuniones_proximas': 0,
    }
    return render(request, 'mi_condominio/dashboard/dashboard.html', context)

