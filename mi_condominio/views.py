from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from .models import Condominio, Reunion, Usuario, Incidencia, CategoriaIncidencia, Bitacora
from django.contrib.auth.models import User


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
    Vista para crear una nueva reunión.
    """
    if request.method == 'POST':
        # Obtener datos del formulario
        condominio_id = request.POST.get('condominio')
        tipo_reunion = request.POST.get('tipo_reunion')
        nombre_reunion = request.POST.get('nombre_reunion')
        fecha_reunion = request.POST.get('fecha_reunion')
        lugar_reunion = request.POST.get('lugar_reunion')
        motivo_reunion = request.POST.get('motivo_reunion')
        acta_reunion_url = request.POST.get('acta_reunion_url')

        try:
            # Obtener el condominio
            condominio = get_object_or_404(Condominio, pk=condominio_id)

            # Crear la reunión
            reunion = Reunion.objects.create(
                condominio=condominio,
                tipo_reunion=tipo_reunion,
                nombre_reunion=nombre_reunion,
                fecha_reunion=fecha_reunion,
                lugar_reunion=lugar_reunion if lugar_reunion else None,
                motivo_reunion=motivo_reunion if motivo_reunion else None,
                acta_reunion_url=acta_reunion_url if acta_reunion_url else None,
            )
            messages.success(request, f'Reunión "{reunion.nombre_reunion}" creada exitosamente.')
            return redirect('reunion_list')
        except Exception as e:
            messages.error(request, f'Error al crear la reunión: {str(e)}')

    # Obtener todos los condominios para el selector
    condominios = Condominio.objects.all().order_by('nombre')

    return render(request, 'mi_condominio/reuniones/form.html', {
        'action': 'Crear',
        'reunion': None,
        'condominios': condominios,
        'tipos_reunion': Reunion.TipoReunion.choices,
    })


@login_required
def reunion_edit(request, pk):
    """
    Vista para editar una reunión existente.
    """
    reunion = get_object_or_404(Reunion, pk=pk)

    if request.method == 'POST':
        # Obtener datos del formulario
        condominio_id = request.POST.get('condominio')
        tipo_reunion = request.POST.get('tipo_reunion')
        nombre_reunion = request.POST.get('nombre_reunion')
        fecha_reunion = request.POST.get('fecha_reunion')
        lugar_reunion = request.POST.get('lugar_reunion')
        motivo_reunion = request.POST.get('motivo_reunion')
        acta_reunion_url = request.POST.get('acta_reunion_url')

        try:
            # Obtener el condominio
            condominio = get_object_or_404(Condominio, pk=condominio_id)

            # Actualizar la reunión
            reunion.condominio = condominio
            reunion.tipo_reunion = tipo_reunion
            reunion.nombre_reunion = nombre_reunion
            reunion.fecha_reunion = fecha_reunion
            reunion.lugar_reunion = lugar_reunion if lugar_reunion else None
            reunion.motivo_reunion = motivo_reunion if motivo_reunion else None
            reunion.acta_reunion_url = acta_reunion_url if acta_reunion_url else None
            reunion.save()

            messages.success(request, f'Reunión "{reunion.nombre_reunion}" actualizada exitosamente.')
            return redirect('reunion_list')
        except Exception as e:
            messages.error(request, f'Error al actualizar la reunión: {str(e)}')

    # Obtener todos los condominios para el selector
    condominios = Condominio.objects.all().order_by('nombre')

    return render(request, 'mi_condominio/reuniones/form.html', {
        'action': 'Editar',
        'reunion': reunion,
        'condominios': condominios,
        'tipos_reunion': Reunion.TipoReunion.choices,
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
    Vista para crear un nuevo usuario.
    Crea automáticamente un User de Django vinculado.
    """
    if request.method == 'POST':
        # Obtener datos del formulario
        condominio_id = request.POST.get('condominio')
        nombres = request.POST.get('nombres')
        apellido = request.POST.get('apellido')
        genero = request.POST.get('genero')
        rut = request.POST.get('rut')
        correo = request.POST.get('correo')
        residencia = request.POST.get('residencia')
        tipo_usuario = request.POST.get('tipo_usuario')
        estado_cuenta = request.POST.get('estado_cuenta')
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Validaciones
        if Usuario.objects.filter(rut=rut).exists():
            messages.error(request, 'Ya existe un usuario con este RUT.')
        elif Usuario.objects.filter(correo=correo).exists():
            messages.error(request, 'Ya existe un usuario con este correo.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Ya existe un usuario con este nombre de usuario.')
        else:
            try:
                # Obtener el condominio
                condominio = get_object_or_404(Condominio, pk=condominio_id)

                # Crear User de Django
                django_user = User.objects.create_user(
                    username=username,
                    email=correo,
                    password=password,
                    first_name=nombres,
                    last_name=apellido
                )

                # Crear el usuario del sistema
                usuario = Usuario.objects.create(
                    user=django_user,
                    condominio=condominio,
                    nombres=nombres,
                    apellido=apellido,
                    genero=genero if genero else None,
                    rut=rut,
                    correo=correo,
                    residencia=residencia if residencia else None,
                    tipo_usuario=tipo_usuario,
                    estado_cuenta=estado_cuenta,
                )

                messages.success(request, f'Usuario "{usuario.nombres} {usuario.apellido}" creado exitosamente.')
                return redirect('usuario_list')
            except Exception as e:
                messages.error(request, f'Error al crear el usuario: {str(e)}')

    # Obtener condominios para el selector
    condominios = Condominio.objects.all().order_by('nombre')

    return render(request, 'mi_condominio/usuarios/form.html', {
        'action': 'Crear',
        'usuario': None,
        'condominios': condominios,
        'generos': Usuario.Genero.choices,
        'tipos_usuario': Usuario.TipoUsuario.choices,
        'estados_cuenta': Usuario.EstadoCuenta.choices,
    })


@login_required
def usuario_edit(request, pk):
    """
    Vista para editar un usuario existente.
    """
    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == 'POST':
        # Obtener datos del formulario
        condominio_id = request.POST.get('condominio')
        nombres = request.POST.get('nombres')
        apellido = request.POST.get('apellido')
        genero = request.POST.get('genero')
        rut = request.POST.get('rut')
        correo = request.POST.get('correo')
        residencia = request.POST.get('residencia')
        tipo_usuario = request.POST.get('tipo_usuario')
        estado_cuenta = request.POST.get('estado_cuenta')
        password = request.POST.get('password')

        # Validar RUT y correo únicos
        if Usuario.objects.filter(rut=rut).exclude(pk=pk).exists():
            messages.error(request, 'Ya existe otro usuario con este RUT.')
        elif Usuario.objects.filter(correo=correo).exclude(pk=pk).exists():
            messages.error(request, 'Ya existe otro usuario con este correo.')
        else:
            try:
                # Obtener el condominio
                condominio = get_object_or_404(Condominio, pk=condominio_id)

                # Actualizar el usuario
                usuario.condominio = condominio
                usuario.nombres = nombres
                usuario.apellido = apellido
                usuario.genero = genero if genero else None
                usuario.rut = rut
                usuario.correo = correo
                usuario.residencia = residencia if residencia else None
                usuario.tipo_usuario = tipo_usuario
                usuario.estado_cuenta = estado_cuenta
                usuario.save()

                # Actualizar User de Django si existe
                if usuario.user:
                    usuario.user.first_name = nombres
                    usuario.user.last_name = apellido
                    usuario.user.email = correo
                    if password:  # Solo actualizar password si se proporcionó uno nuevo
                        usuario.user.set_password(password)
                    usuario.user.save()

                messages.success(request, f'Usuario "{usuario.nombres} {usuario.apellido}" actualizado exitosamente.')
                return redirect('usuario_list')
            except Exception as e:
                messages.error(request, f'Error al actualizar el usuario: {str(e)}')

    # Obtener condominios para el selector
    condominios = Condominio.objects.all().order_by('nombre')

    return render(request, 'mi_condominio/usuarios/form.html', {
        'action': 'Editar',
        'usuario': usuario,
        'condominios': condominios,
        'generos': Usuario.Genero.choices,
        'tipos_usuario': Usuario.TipoUsuario.choices,
        'estados_cuenta': Usuario.EstadoCuenta.choices,
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
    Vista para crear una nueva incidencia.
    """
    if request.method == 'POST':
        # Obtener datos del formulario
        condominio_id = request.POST.get('condominio')
        tipo_incidencia_id = request.POST.get('tipo_incidencia')
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')
        estado = request.POST.get('estado')
        prioridad = request.POST.get('prioridad')
        ubicacion_latitud = request.POST.get('ubicacion_latitud')
        ubicacion_longitud = request.POST.get('ubicacion_longitud')
        direccion_incidencia = request.POST.get('direccion_incidencia')
        usuario_reporta_id = request.POST.get('usuario_reporta')

        try:
            # Obtener objetos relacionados
            condominio = get_object_or_404(Condominio, pk=condominio_id)
            tipo_incidencia = get_object_or_404(CategoriaIncidencia, pk=tipo_incidencia_id)
            usuario_reporta = get_object_or_404(Usuario, pk=usuario_reporta_id)

            # Crear la incidencia
            incidencia = Incidencia.objects.create(
                condominio=condominio,
                tipo_incidencia=tipo_incidencia,
                titulo=titulo,
                descripcion=descripcion if descripcion else None,
                estado=estado,
                prioridad=prioridad,
                ubicacion_latitud_reporte=ubicacion_latitud if ubicacion_latitud else None,
                ubicacion_longitud_reporte=ubicacion_longitud if ubicacion_longitud else None,
                direccion_condominio_incidencia=direccion_incidencia if direccion_incidencia else None,
                usuario_reporta=usuario_reporta,
            )
            messages.success(request, f'Incidencia "{incidencia.titulo}" creada exitosamente.')
            return redirect('incidencia_list')
        except Exception as e:
            messages.error(request, f'Error al crear la incidencia: {str(e)}')

    # Obtener datos para el formulario
    condominios = Condominio.objects.all().order_by('nombre')
    categorias = CategoriaIncidencia.objects.all().order_by('nombre_categoria_incidencia')
    usuarios = Usuario.objects.filter(estado_cuenta='ACTIVO').select_related('condominio').order_by('apellido', 'nombres')

    return render(request, 'mi_condominio/incidencias/form.html', {
        'action': 'Crear',
        'incidencia': None,
        'condominios': condominios,
        'categorias': categorias,
        'usuarios': usuarios,
        'estados': Incidencia.Estado.choices,
        'prioridades': Incidencia.Prioridad.choices,
    })


@login_required
def incidencia_edit(request, pk):
    """
    Vista para editar una incidencia existente.
    """
    incidencia = get_object_or_404(Incidencia, pk=pk)

    if request.method == 'POST':
        # Obtener datos del formulario
        condominio_id = request.POST.get('condominio')
        tipo_incidencia_id = request.POST.get('tipo_incidencia')
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')
        estado = request.POST.get('estado')
        prioridad = request.POST.get('prioridad')
        ubicacion_latitud = request.POST.get('ubicacion_latitud')
        ubicacion_longitud = request.POST.get('ubicacion_longitud')
        direccion_incidencia = request.POST.get('direccion_incidencia')
        usuario_reporta_id = request.POST.get('usuario_reporta')
        fecha_cierre = request.POST.get('fecha_cierre')

        try:
            # Obtener objetos relacionados
            condominio = get_object_or_404(Condominio, pk=condominio_id)
            tipo_incidencia = get_object_or_404(CategoriaIncidencia, pk=tipo_incidencia_id)
            usuario_reporta = get_object_or_404(Usuario, pk=usuario_reporta_id)

            # Actualizar la incidencia
            incidencia.condominio = condominio
            incidencia.tipo_incidencia = tipo_incidencia
            incidencia.titulo = titulo
            incidencia.descripcion = descripcion if descripcion else None
            incidencia.estado = estado
            incidencia.prioridad = prioridad
            incidencia.ubicacion_latitud_reporte = ubicacion_latitud if ubicacion_latitud else None
            incidencia.ubicacion_longitud_reporte = ubicacion_longitud if ubicacion_longitud else None
            incidencia.direccion_condominio_incidencia = direccion_incidencia if direccion_incidencia else None
            incidencia.usuario_reporta = usuario_reporta
            incidencia.fecha_cierre = fecha_cierre if fecha_cierre else None
            incidencia.save()

            messages.success(request, f'Incidencia "{incidencia.titulo}" actualizada exitosamente.')
            return redirect('incidencia_list')
        except Exception as e:
            messages.error(request, f'Error al actualizar la incidencia: {str(e)}')

    # Obtener datos para el formulario
    condominios = Condominio.objects.all().order_by('nombre')
    categorias = CategoriaIncidencia.objects.all().order_by('nombre_categoria_incidencia')
    usuarios = Usuario.objects.filter(estado_cuenta='ACTIVO').select_related('condominio').order_by('apellido', 'nombres')

    return render(request, 'mi_condominio/incidencias/form.html', {
        'action': 'Editar',
        'incidencia': incidencia,
        'condominios': condominios,
        'categorias': categorias,
        'usuarios': usuarios,
        'estados': Incidencia.Estado.choices,
        'prioridades': Incidencia.Prioridad.choices,
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
    Vista para crear una nueva categoría de incidencia.
    """
    if request.method == 'POST':
        nombre_categoria = request.POST.get('nombre_categoria_incidencia')

        # Validar que no exista una categoría con el mismo nombre
        if CategoriaIncidencia.objects.filter(nombre_categoria_incidencia__iexact=nombre_categoria).exists():
            messages.error(request, 'Ya existe una categoría con este nombre.')
        else:
            try:
                categoria = CategoriaIncidencia.objects.create(
                    nombre_categoria_incidencia=nombre_categoria
                )
                messages.success(request, f'Categoría "{categoria.nombre_categoria_incidencia}" creada exitosamente.')
                return redirect('categoria_list')
            except Exception as e:
                messages.error(request, f'Error al crear la categoría: {str(e)}')

    return render(request, 'mi_condominio/categorias/form.html', {
        'action': 'Crear',
        'categoria': None,
    })


@login_required
def categoria_edit(request, pk):
    """
    Vista para editar una categoría existente.
    """
    categoria = get_object_or_404(CategoriaIncidencia, pk=pk)

    if request.method == 'POST':
        nombre_categoria = request.POST.get('nombre_categoria_incidencia')

        # Validar que no exista otra categoría con el mismo nombre
        if CategoriaIncidencia.objects.filter(
            nombre_categoria_incidencia__iexact=nombre_categoria
        ).exclude(pk=pk).exists():
            messages.error(request, 'Ya existe otra categoría con este nombre.')
        else:
            try:
                categoria.nombre_categoria_incidencia = nombre_categoria
                categoria.save()
                messages.success(request, f'Categoría "{categoria.nombre_categoria_incidencia}" actualizada exitosamente.')
                return redirect('categoria_list')
            except Exception as e:
                messages.error(request, f'Error al actualizar la categoría: {str(e)}')

    return render(request, 'mi_condominio/categorias/form.html', {
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
    Vista para crear una nueva bitácora.
    """
    if request.method == 'POST':
        incidencia_id = request.POST.get('incidencia')
        detalle = request.POST.get('detalle')
        accion = request.POST.get('accion')

        try:
            incidencia = get_object_or_404(Incidencia, pk=incidencia_id)

            bitacora = Bitacora.objects.create(
                incidencia=incidencia,
                detalle=detalle if detalle else None,
                accion=accion if accion else None,
            )
            messages.success(request, f'Registro de bitácora creado exitosamente para "{incidencia.titulo}".')
            return redirect('bitacora_list')
        except Exception as e:
            messages.error(request, f'Error al crear el registro: {str(e)}')

    # Obtener todas las incidencias para el selector
    incidencias = Incidencia.objects.select_related('condominio').all().order_by('-id')

    return render(request, 'mi_condominio/bitacoras/form.html', {
        'action': 'Crear',
        'bitacora': None,
        'incidencias': incidencias,
    })


@login_required
def bitacora_edit(request, pk):
    """
    Vista para editar una bitácora existente.
    """
    bitacora = get_object_or_404(Bitacora, pk=pk)

    if request.method == 'POST':
        incidencia_id = request.POST.get('incidencia')
        detalle = request.POST.get('detalle')
        accion = request.POST.get('accion')

        try:
            incidencia = get_object_or_404(Incidencia, pk=incidencia_id)

            bitacora.incidencia = incidencia
            bitacora.detalle = detalle if detalle else None
            bitacora.accion = accion if accion else None
            bitacora.save()

            messages.success(request, f'Registro de bitácora actualizado exitosamente.')
            return redirect('bitacora_list')
        except Exception as e:
            messages.error(request, f'Error al actualizar el registro: {str(e)}')

    # Obtener todas las incidencias para el selector
    incidencias = Incidencia.objects.select_related('condominio').all().order_by('-id')

    return render(request, 'mi_condominio/bitacoras/form.html', {
        'action': 'Editar',
        'bitacora': bitacora,
        'incidencias': incidencias,
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

