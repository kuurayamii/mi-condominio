from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from django.db.models import Q
from .models import Condominio, Reunion, Usuario, Incidencia, CategoriaIncidencia, Bitacora, EvidenciaIncidencia, Amonestacion
from django.contrib.auth.models import User
from .forms import (
    CondominioForm,
    UsuarioForm,
    ReunionForm,
    IncidenciaForm,
    CategoriaIncidenciaForm,
    BitacoraForm,
    EvidenciaIncidenciaForm,
    AmonestacionForm
)


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
    from datetime import date

    # TODO: Agregar lógica para obtener estadísticas reales de la base de datos
    total_condominios = Condominio.objects.count()

    # Contar reuniones próximas (desde hoy en adelante)
    reuniones_proximas = Reunion.objects.filter(fecha_reunion__gte=date.today()).count()

    # Contar usuarios activos
    total_usuarios = Usuario.objects.filter(estado_cuenta='ACTIVO').count()

    # Contar incidencias abiertas (no cerradas ni canceladas)
    incidencias_abiertas = Incidencia.objects.exclude(
        estado__in=['CERRADA', 'CANCELADA']
    ).count()

    context = {
        'total_condominios': total_condominios,
        'total_usuarios': total_usuarios,
        'incidencias_abiertas': incidencias_abiertas,
        'reuniones_proximas': reuniones_proximas,
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
    Vista para crear un nuevo condominio usando Django Forms.
    """
    if request.method == 'POST':
        form = CondominioForm(request.POST)
        if form.is_valid():
            condominio = form.save()
            messages.success(request, f'Condominio "{condominio.nombre}" creado exitosamente.')
            return redirect('condominio_list')
        else:
            # Los errores se mostrarán automáticamente en el template
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = CondominioForm()

    return render(request, 'mi_condominio/condominios/form.html', {
        'form': form,
        'action': 'Crear',
        'condominio': None,
    })


@login_required
def condominio_edit(request, pk):
    """
    Vista para editar un condominio existente usando Django Forms.
    """
    condominio = get_object_or_404(Condominio, pk=pk)

    if request.method == 'POST':
        form = CondominioForm(request.POST, instance=condominio)
        if form.is_valid():
            condominio = form.save()
            messages.success(request, f'Condominio "{condominio.nombre}" actualizado exitosamente.')
            return redirect('condominio_list')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = CondominioForm(instance=condominio)

    return render(request, 'mi_condominio/condominios/form.html', {
        'form': form,
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


# ============================================================================
# VISTAS PARA GESTIÓN DE REUNIONES
# ============================================================================

@login_required
def reunion_list(request):
    """
    Vista que muestra el listado de todas las reuniones.
    Incluye búsqueda y filtros por condominio.
    """
    from datetime import date

    reuniones = Reunion.objects.select_related('condominio').all()

    # Filtro por condominio
    condominio_id = request.GET.get('condominio', '')
    if condominio_id:
        reuniones = reuniones.filter(condominio_id=condominio_id)

    # Búsqueda
    search_query = request.GET.get('search', '')
    if search_query:
        reuniones = reuniones.filter(
            models.Q(nombre_reunion__icontains=search_query) |
            models.Q(condominio__nombre__icontains=search_query) |
            models.Q(motivo_reunion__icontains=search_query) |
            models.Q(lugar_reunion__icontains=search_query)
        )

    # Obtener todos los condominios para el filtro
    condominios = Condominio.objects.all().order_by('nombre')

    context = {
        'reuniones': reuniones,
        'condominios': condominios,
        'search_query': search_query,
        'condominio_id': condominio_id,
        'today': date.today(),
    }
    return render(request, 'mi_condominio/reuniones/list.html', context)


@login_required
def reunion_create(request):
    """
    Vista para crear una nueva reunión usando Django Forms.
    """
    if request.method == 'POST':
        form = ReunionForm(request.POST)
        if form.is_valid():
            reunion = form.save()
            messages.success(request, f'Reunión "{reunion.nombre_reunion}" creada exitosamente.')
            return redirect('reunion_list')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = ReunionForm()

    return render(request, 'mi_condominio/reuniones/form.html', {
        'form': form,
        'action': 'Crear',
        'reunion': None,
    })


@login_required
def reunion_edit(request, pk):
    """
    Vista para editar una reunión existente usando Django Forms.
    """
    reunion = get_object_or_404(Reunion, pk=pk)

    if request.method == 'POST':
        form = ReunionForm(request.POST, instance=reunion)
        if form.is_valid():
            reunion = form.save()
            messages.success(request, f'Reunión "{reunion.nombre_reunion}" actualizada exitosamente.')
            return redirect('reunion_list')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = ReunionForm(instance=reunion)

    return render(request, 'mi_condominio/reuniones/form.html', {
        'form': form,
        'action': 'Editar',
        'reunion': reunion,
    })


@login_required
def reunion_delete(request, pk):
    """
    Vista para eliminar una reunión.
    """
    reunion = get_object_or_404(Reunion, pk=pk)

    if request.method == 'POST':
        nombre = reunion.nombre_reunion
        try:
            reunion.delete()
            messages.success(request, f'Reunión "{nombre}" eliminada exitosamente.')
        except Exception as e:
            messages.error(request, f'Error al eliminar la reunión: {str(e)}')
        return redirect('reunion_list')

    return render(request, 'mi_condominio/reuniones/delete.html', {
        'reunion': reunion,
    })


# ============================================================================
# VISTAS PARA GESTIÓN DE USUARIOS
# ============================================================================

@login_required
def usuario_list(request):
    """
    Vista que muestra el listado de todos los usuarios.
    Incluye búsqueda y filtros por condominio y tipo de usuario.
    """
    usuarios = Usuario.objects.select_related('condominio', 'user').all()

    # Filtro por condominio
    condominio_id = request.GET.get('condominio', '')
    if condominio_id:
        usuarios = usuarios.filter(condominio_id=condominio_id)

    # Filtro por tipo de usuario
    tipo_usuario = request.GET.get('tipo_usuario', '')
    if tipo_usuario:
        usuarios = usuarios.filter(tipo_usuario=tipo_usuario)

    # Búsqueda
    search_query = request.GET.get('search', '')
    if search_query:
        usuarios = usuarios.filter(
            models.Q(nombres__icontains=search_query) |
            models.Q(apellido__icontains=search_query) |
            models.Q(rut__icontains=search_query) |
            models.Q(correo__icontains=search_query) |
            models.Q(condominio__nombre__icontains=search_query)
        )

    # Obtener condominios y tipos para filtros
    condominios = Condominio.objects.all().order_by('nombre')

    context = {
        'usuarios': usuarios,
        'condominios': condominios,
        'tipos_usuario': Usuario.TipoUsuario.choices,
        'search_query': search_query,
        'condominio_id': condominio_id,
        'tipo_usuario_filtro': tipo_usuario,
    }
    return render(request, 'mi_condominio/usuarios/list.html', context)


@login_required
def usuario_create(request):
    """
    Vista para crear un nuevo usuario usando Django Forms.
    Crea automáticamente un User de Django vinculado.
    """
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Validar username único
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Ya existe un usuario con este nombre de usuario.')
            form.add_error(None, 'El nombre de usuario ya está en uso.')
        elif form.is_valid():
            try:
                # Crear User de Django primero
                django_user = User.objects.create_user(
                    username=username,
                    email=form.cleaned_data['correo'],
                    password=password,
                    first_name=form.cleaned_data['nombres'],
                    last_name=form.cleaned_data['apellido']
                )

                # Crear usuario del sistema
                usuario = form.save(commit=False)
                usuario.user = django_user
                usuario.save()

                messages.success(request, f'Usuario "{usuario.nombres} {usuario.apellido}" creado exitosamente.')
                return redirect('usuario_list')
            except Exception as e:
                messages.error(request, f'Error al crear el usuario: {str(e)}')
                # Rollback: eliminar User de Django si falla la creación del Usuario
                if 'django_user' in locals():
                    django_user.delete()
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = UsuarioForm()

    return render(request, 'mi_condominio/usuarios/form.html', {
        'form': form,
        'action': 'Crear',
        'usuario': None,
    })


@login_required
def usuario_edit(request, pk):
    """
    Vista para editar un usuario existente usando Django Forms.
    """
    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        password = request.POST.get('password')

        if form.is_valid():
            usuario = form.save()

            # Actualizar User de Django si existe
            if usuario.user:
                usuario.user.email = usuario.correo
                usuario.user.first_name = usuario.nombres
                usuario.user.last_name = usuario.apellido
                if password:  # Solo actualizar password si se proporcionó
                    usuario.user.set_password(password)
                usuario.user.save()

            messages.success(request, f'Usuario "{usuario.nombres} {usuario.apellido}" actualizado exitosamente.')
            return redirect('usuario_list')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = UsuarioForm(instance=usuario)

    return render(request, 'mi_condominio/usuarios/form.html', {
        'form': form,
        'action': 'Editar',
        'usuario': usuario,
    })


@login_required
def usuario_delete(request, pk):
    """
    Vista para eliminar un usuario.
    También elimina el User de Django asociado.
    """
    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == 'POST':
        nombre_completo = f"{usuario.nombres} {usuario.apellido}"
        django_user = usuario.user
        try:
            usuario.delete()
            # El User de Django se eliminará automáticamente por CASCADE
            messages.success(request, f'Usuario "{nombre_completo}" eliminado exitosamente.')
        except Exception as e:
            messages.error(request, f'Error al eliminar el usuario: {str(e)}')
        return redirect('usuario_list')

    return render(request, 'mi_condominio/usuarios/delete.html', {
        'usuario': usuario,
    })


# ============================================================================
# VISTAS PARA GESTIÓN DE INCIDENCIAS
# ============================================================================

@login_required
def incidencia_list(request):
    """
    Vista que muestra el listado de todas las incidencias.
    Incluye búsqueda y filtros por condominio, estado, prioridad y categoría.
    """
    incidencias = Incidencia.objects.select_related('condominio', 'tipo_incidencia', 'usuario_reporta').all()

    # Filtro por condominio
    condominio_id = request.GET.get('condominio', '')
    if condominio_id:
        incidencias = incidencias.filter(condominio_id=condominio_id)

    # Filtro por estado
    estado = request.GET.get('estado', '')
    if estado:
        incidencias = incidencias.filter(estado=estado)

    # Filtro por prioridad
    prioridad = request.GET.get('prioridad', '')
    if prioridad:
        incidencias = incidencias.filter(prioridad=prioridad)

    # Filtro por categoría
    categoria_id = request.GET.get('categoria', '')
    if categoria_id:
        incidencias = incidencias.filter(tipo_incidencia_id=categoria_id)

    # Búsqueda
    search_query = request.GET.get('search', '')
    if search_query:
        incidencias = incidencias.filter(
            models.Q(titulo__icontains=search_query) |
            models.Q(descripcion__icontains=search_query) |
            models.Q(condominio__nombre__icontains=search_query) |
            models.Q(usuario_reporta__nombres__icontains=search_query) |
            models.Q(usuario_reporta__apellido__icontains=search_query)
        )

    # Obtener datos para filtros
    condominios = Condominio.objects.all().order_by('nombre')
    categorias = CategoriaIncidencia.objects.all().order_by('nombre_categoria_incidencia')

    context = {
        'incidencias': incidencias,
        'condominios': condominios,
        'categorias': categorias,
        'estados': Incidencia.Estado.choices,
        'prioridades': Incidencia.Prioridad.choices,
        'search_query': search_query,
        'condominio_id': condominio_id,
        'estado_filtro': estado,
        'prioridad_filtro': prioridad,
        'categoria_id': categoria_id,
    }
    return render(request, 'mi_condominio/incidencias/list.html', context)


@login_required
def incidencia_create(request):
    """
    Vista para crear una nueva incidencia usando Django Forms.
    """
    if request.method == 'POST':
        form = IncidenciaForm(request.POST)
        if form.is_valid():
            incidencia = form.save()
            messages.success(request, f'Incidencia "{incidencia.titulo}" creada exitosamente.')
            return redirect('incidencia_list')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = IncidenciaForm()

    return render(request, 'mi_condominio/incidencias/form.html', {
        'form': form,
        'action': 'Crear',
        'incidencia': None,
    })


@login_required
def incidencia_edit(request, pk):
    """
    Vista para editar una incidencia existente usando Django Forms.
    """
    incidencia = get_object_or_404(Incidencia, pk=pk)

    if request.method == 'POST':
        form = IncidenciaForm(request.POST, instance=incidencia)
        if form.is_valid():
            incidencia = form.save()
            messages.success(request, f'Incidencia "{incidencia.titulo}" actualizada exitosamente.')
            return redirect('incidencia_list')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = IncidenciaForm(instance=incidencia)

    return render(request, 'mi_condominio/incidencias/form.html', {
        'form': form,
        'action': 'Editar',
        'incidencia': incidencia,
    })


@login_required
def incidencia_delete(request, pk):
    """
    Vista para eliminar una incidencia.
    """
    incidencia = get_object_or_404(Incidencia, pk=pk)

    if request.method == 'POST':
        titulo = incidencia.titulo
        try:
            incidencia.delete()
            messages.success(request, f'Incidencia "{titulo}" eliminada exitosamente.')
        except Exception as e:
            messages.error(request, f'Error al eliminar la incidencia: {str(e)}')
        return redirect('incidencia_list')

    return render(request, 'mi_condominio/incidencias/delete.html', {
        'incidencia': incidencia,
    })


# ============================================================================
# VISTAS PARA GESTIÓN DE CATEGORÍAS DE INCIDENCIAS
# ============================================================================

@login_required
def categoria_list(request):
    """
    Vista que muestra el listado de todas las categorías de incidencias.
    Incluye búsqueda por nombre.
    """
    categorias = CategoriaIncidencia.objects.all().order_by('id')

    # Búsqueda
    search_query = request.GET.get('search', '')
    if search_query:
        categorias = categorias.filter(
            nombre_categoria_incidencia__icontains=search_query
        )

    context = {
        'categorias': categorias,
        'search_query': search_query,
    }
    return render(request, 'mi_condominio/categorias/list.html', context)


@login_required
def categoria_create(request):
    """
    Vista para crear una nueva categoría usando Django Forms.
    """
    if request.method == 'POST':
        form = CategoriaIncidenciaForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoría "{categoria.nombre_categoria_incidencia}" creada exitosamente.')
            return redirect('categoria_list')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = CategoriaIncidenciaForm()

    return render(request, 'mi_condominio/categorias/form.html', {
        'form': form,
        'action': 'Crear',
        'categoria': None,
    })


@login_required
def categoria_edit(request, pk):
    """
    Vista para editar una categoría existente usando Django Forms.
    """
    categoria = get_object_or_404(CategoriaIncidencia, pk=pk)

    if request.method == 'POST':
        form = CategoriaIncidenciaForm(request.POST, instance=categoria)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoría "{categoria.nombre_categoria_incidencia}" actualizada exitosamente.')
            return redirect('categoria_list')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = CategoriaIncidenciaForm(instance=categoria)

    return render(request, 'mi_condominio/categorias/form.html', {
        'form': form,
        'action': 'Editar',
        'categoria': categoria,
    })


@login_required
def categoria_delete(request, pk):
    """
    Vista para eliminar una categoría.
    """
    categoria = get_object_or_404(CategoriaIncidencia, pk=pk)

    # Contar incidencias asociadas
    incidencias_count = categoria.incidencias.count()

    if request.method == 'POST':
        nombre = categoria.nombre_categoria_incidencia
        try:
            categoria.delete()
            messages.success(request, f'Categoría "{nombre}" eliminada exitosamente.')
        except Exception as e:
            messages.error(request, f'Error al eliminar la categoría: {str(e)}')
        return redirect('categoria_list')

    return render(request, 'mi_condominio/categorias/delete.html', {
        'categoria': categoria,
        'incidencias_count': incidencias_count,
    })


# ============================================================================
# VISTAS PARA GESTIÓN DE BITÁCORA
# ============================================================================

@login_required
def bitacora_list(request):
    """
    Vista que muestra el listado de todas las bitácoras.
    Incluye búsqueda y filtro por incidencia.
    """
    bitacoras = Bitacora.objects.select_related('incidencia', 'incidencia__condominio').all().order_by('-fecha_bitacora', '-id')

    # Filtro por incidencia
    incidencia_id = request.GET.get('incidencia', '')
    if incidencia_id:
        bitacoras = bitacoras.filter(incidencia_id=incidencia_id)

    # Búsqueda
    search_query = request.GET.get('search', '')
    if search_query:
        bitacoras = bitacoras.filter(
            models.Q(detalle__icontains=search_query) |
            models.Q(accion__icontains=search_query) |
            models.Q(incidencia__titulo__icontains=search_query)
        )

    # Obtener todas las incidencias para el filtro
    incidencias = Incidencia.objects.select_related('condominio').all().order_by('-id')

    context = {
        'bitacoras': bitacoras,
        'incidencias': incidencias,
        'search_query': search_query,
        'incidencia_id': incidencia_id,
    }
    return render(request, 'mi_condominio/bitacoras/list.html', context)


@login_required
def bitacora_create(request):
    """
    Vista para crear una nueva bitácora usando Django Forms.
    """
    if request.method == 'POST':
        form = BitacoraForm(request.POST)
        if form.is_valid():
            bitacora = form.save()
            messages.success(request, f'Registro de bitácora creado exitosamente para "{bitacora.incidencia.titulo}".')
            return redirect('bitacora_list')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = BitacoraForm()

    return render(request, 'mi_condominio/bitacoras/form.html', {
        'form': form,
        'action': 'Crear',
        'bitacora': None,
    })


@login_required
def bitacora_edit(request, pk):
    """
    Vista para editar una bitácora existente usando Django Forms.
    """
    bitacora = get_object_or_404(Bitacora, pk=pk)

    if request.method == 'POST':
        form = BitacoraForm(request.POST, instance=bitacora)
        if form.is_valid():
            bitacora = form.save()
            messages.success(request, f'Registro de bitácora actualizado exitosamente.')
            return redirect('bitacora_list')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = BitacoraForm(instance=bitacora)

    return render(request, 'mi_condominio/bitacoras/form.html', {
        'form': form,
        'action': 'Editar',
        'bitacora': bitacora,
    })


@login_required
def bitacora_delete(request, pk):
    """
    Vista para eliminar una bitácora.
    """
    bitacora = get_object_or_404(Bitacora, pk=pk)

    if request.method == 'POST':
        incidencia_titulo = bitacora.incidencia.titulo
        try:
            bitacora.delete()
            messages.success(request, f'Registro de bitácora eliminado exitosamente.')
        except Exception as e:
            messages.error(request, f'Error al eliminar el registro: {str(e)}')
        return redirect('bitacora_list')

    return render(request, 'mi_condominio/bitacoras/delete.html', {
        'bitacora': bitacora,
    })


# ==================== VISTAS PARA EVIDENCIAS ====================

@login_required
def evidencia_list(request):
    evidencias = EvidenciaIncidencia.objects.select_related('incidencia', 'incidencia__condominio').all().order_by('-id')

    # Filtros
    incidencia_id = request.GET.get('incidencia')
    tipo_archivo = request.GET.get('tipo_archivo')
    search = request.GET.get('search')

    if incidencia_id:
        evidencias = evidencias.filter(incidencia_id=incidencia_id)

    if tipo_archivo:
        evidencias = evidencias.filter(tipo_archivo_evidencia=tipo_archivo)

    if search:
        evidencias = evidencias.filter(
            Q(incidencia__titulo__icontains=search) |
            Q(archivo_evidencia__icontains=search)
        )

    # Para los filtros
    incidencias = Incidencia.objects.select_related('condominio').all().order_by('-id')
    tipos_archivo = EvidenciaIncidencia.TipoArchivo.choices

    return render(request, 'mi_condominio/evidencias/list.html', {
        'evidencias': evidencias,
        'incidencias': incidencias,
        'tipos_archivo': tipos_archivo,
    })


@login_required
def evidencia_create(request):
    """
    Vista para crear una nueva evidencia con upload de archivo.
    """
    if request.method == 'POST':
        form = EvidenciaIncidenciaForm(request.POST, request.FILES)
        if form.is_valid():
            evidencia = form.save()
            messages.success(request, f'Evidencia agregada exitosamente a la incidencia "{evidencia.incidencia.titulo}".')
            return redirect('evidencia_list')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = EvidenciaIncidenciaForm()

    return render(request, 'mi_condominio/evidencias/form.html', {
        'form': form,
        'action': 'Crear',
        'evidencia': None,
    })


@login_required
def evidencia_edit(request, pk):
    """
    Vista para editar una evidencia existente con opción de reemplazar archivo.
    """
    evidencia = get_object_or_404(EvidenciaIncidencia, pk=pk)

    if request.method == 'POST':
        form = EvidenciaIncidenciaForm(request.POST, request.FILES, instance=evidencia)
        if form.is_valid():
            evidencia = form.save()
            messages.success(request, 'Evidencia actualizada exitosamente.')
            return redirect('evidencia_list')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = EvidenciaIncidenciaForm(instance=evidencia)

    return render(request, 'mi_condominio/evidencias/form.html', {
        'form': form,
        'action': 'Editar',
        'evidencia': evidencia,
    })


@login_required
def evidencia_delete(request, pk):
    """
    Vista para eliminar una evidencia y su archivo asociado del servidor.
    """
    evidencia = get_object_or_404(EvidenciaIncidencia, pk=pk)

    if request.method == 'POST':
        incidencia_titulo = evidencia.incidencia.titulo

        # Eliminar el archivo del servidor antes de eliminar el registro
        if evidencia.archivo_evidencia:
            evidencia.archivo_evidencia.delete(save=False)

        evidencia.delete()
        messages.success(request, f'Evidencia de "{incidencia_titulo}" eliminada exitosamente.')
        return redirect('evidencia_list')

    return render(request, 'mi_condominio/evidencias/delete.html', {
        'evidencia': evidencia,
    })


# ==================== VISTAS PARA AMONESTACIONES ====================

@login_required
def amonestacion_list(request):
    amonestaciones = Amonestacion.objects.select_related('usuario_reporta').all().order_by('-fecha_amonestacion', '-id')

    # Filtros
    usuario_reporta_id = request.GET.get('usuario_reporta')
    tipo_amonestacion = request.GET.get('tipo_amonestacion')
    motivo = request.GET.get('motivo')
    search = request.GET.get('search')

    if usuario_reporta_id:
        amonestaciones = amonestaciones.filter(usuario_reporta_id=usuario_reporta_id)

    if tipo_amonestacion:
        amonestaciones = amonestaciones.filter(tipo_amonestacion=tipo_amonestacion)

    if motivo:
        amonestaciones = amonestaciones.filter(motivo=motivo)

    if search:
        amonestaciones = amonestaciones.filter(
            Q(motivo_detalle__icontains=search) |
            Q(nombre_amonestado__icontains=search) |
            Q(apellidos_amonestado__icontains=search) |
            Q(rut_amonestado__icontains=search)
        )

    # Para los filtros
    usuarios = Usuario.objects.all().order_by('apellido', 'nombres')
    tipos_amonestacion = Amonestacion.TipoAmonestacion.choices
    motivos = Amonestacion.MotivoAmonestacion.choices

    return render(request, 'mi_condominio/amonestaciones/list.html', {
        'amonestaciones': amonestaciones,
        'usuarios': usuarios,
        'tipos_amonestacion': tipos_amonestacion,
        'motivos': motivos,
    })


@login_required
def amonestacion_create(request):
    """
    Vista para crear una nueva amonestación usando Django Forms.
    """
    if request.method == 'POST':
        form = AmonestacionForm(request.POST)
        if form.is_valid():
            amonestacion = form.save()
            messages.success(request, f'Amonestación registrada exitosamente para {amonestacion.nombre_amonestado} {amonestacion.apellidos_amonestado}.')
            return redirect('amonestacion_list')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = AmonestacionForm()

    return render(request, 'mi_condominio/amonestaciones/form.html', {
        'form': form,
        'action': 'Crear',
        'amonestacion': None,
    })


@login_required
def amonestacion_edit(request, pk):
    """
    Vista para editar una amonestación existente usando Django Forms.
    """
    amonestacion = get_object_or_404(Amonestacion, pk=pk)

    if request.method == 'POST':
        form = AmonestacionForm(request.POST, instance=amonestacion)
        if form.is_valid():
            amonestacion = form.save()
            messages.success(request, 'Amonestación actualizada exitosamente.')
            return redirect('amonestacion_list')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = AmonestacionForm(instance=amonestacion)

    return render(request, 'mi_condominio/amonestaciones/form.html', {
        'form': form,
        'action': 'Editar',
        'amonestacion': amonestacion,
    })


@login_required
def amonestacion_delete(request, pk):
    amonestacion = get_object_or_404(Amonestacion, pk=pk)

    if request.method == 'POST':
        amonestado_nombre = f"{amonestacion.nombre_amonestado} {amonestacion.apellidos_amonestado}"
        amonestacion.delete()
        messages.success(request, f'Amonestación de {amonestado_nombre} eliminada exitosamente.')
        return redirect('amonestacion_list')

    return render(request, 'mi_condominio/amonestaciones/delete.html', {
        'amonestacion': amonestacion,
    })


# ==================== VISTAS PARA ASISTENTE DE IA ====================

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from . import ai_assistant


@login_required
def ai_chat_interface(request):
    """Vista principal del chat con el asistente de IA"""
    return render(request, 'mi_condominio/ai_chat/chat.html')


@login_required
@require_POST
def ai_chat_send_message(request):
    """API endpoint para enviar un mensaje al asistente"""
    import json

    try:
        data = json.loads(request.body)
        mensaje = data.get('mensaje', '').strip()

        if not mensaje:
            return JsonResponse({
                'exito': False,
                'error': 'El mensaje no puede estar vacío'
            }, status=400)

        # Obtener el usuario actual (necesitas tener el modelo Usuario vinculado con el User de Django)
        try:
            usuario = Usuario.objects.get(correo=request.user.email)
        except Usuario.DoesNotExist:
            return JsonResponse({
                'exito': False,
                'error': 'Usuario no encontrado en el sistema'
            }, status=404)

        # Procesar el mensaje con el asistente
        resultado = ai_assistant.chat(usuario, mensaje)

        return JsonResponse(resultado)

    except json.JSONDecodeError:
        return JsonResponse({
            'exito': False,
            'error': 'Formato de JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'exito': False,
            'error': str(e)
        }, status=500)


@login_required
def ai_chat_history(request):
    """API endpoint para obtener el historial de la sesión actual"""
    try:
        usuario = Usuario.objects.get(correo=request.user.email)
        session = ai_assistant.get_or_create_session(usuario)
        history = ai_assistant.get_session_history(session.id)

        return JsonResponse(history)

    except Usuario.DoesNotExist:
        return JsonResponse({
            'exito': False,
            'error': 'Usuario no encontrado'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'exito': False,
            'error': str(e)
        }, status=500)


@login_required
@require_POST
def ai_chat_clear(request):
    """API endpoint para limpiar la sesión y comenzar una nueva conversación"""
    try:
        usuario = Usuario.objects.get(correo=request.user.email)
        resultado = ai_assistant.clear_session(usuario)

        return JsonResponse(resultado)

    except Usuario.DoesNotExist:
        return JsonResponse({
            'exito': False,
            'error': 'Usuario no encontrado'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'exito': False,
            'error': str(e)
        }, status=500)


@login_required
@require_POST
def ai_chat_confirm_action(request):
    """API endpoint para ejecutar una acción después de la confirmación del usuario"""
    try:
        data = json.loads(request.body)
        accion = data.get('accion')
        datos = data.get('datos')

        if not accion or not datos:
            return JsonResponse({
                'exito': False,
                'error': 'Faltan parámetros: accion y datos son requeridos'
            }, status=400)

        # Importar las funciones de ejecución
        from . import ai_tools

        # Ejecutar la acción correspondiente
        if accion in ai_tools.EXECUTION_FUNCTIONS:
            resultado = ai_tools.EXECUTION_FUNCTIONS[accion](datos)

            # Guardar en el historial del chat el resultado
            usuario = Usuario.objects.get(correo=request.user.email)
            session = ai_assistant.get_or_create_session(usuario)

            if resultado.get('exito'):
                mensaje_confirmacion = f"✓ {resultado['mensaje']}"
            else:
                mensaje_confirmacion = f"✗ Error: {resultado.get('error', 'Error desconocido')}"

            # Crear mensaje del asistente con el resultado
            ChatMessage.objects.create(
                sesion=session,
                role='assistant',
                contenido=mensaje_confirmacion
            )

            return JsonResponse(resultado)
        else:
            return JsonResponse({
                'exito': False,
                'error': f'Acción "{accion}" no reconocida'
            }, status=400)

    except Usuario.DoesNotExist:
        return JsonResponse({
            'exito': False,
            'error': 'Usuario no encontrado'
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'exito': False,
            'error': 'JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'exito': False,
            'error': str(e)
        }, status=500)
