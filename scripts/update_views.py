"""
Script temporal para actualizar views.py con formularios Django.
Este script actualizará las funciones create/edit restantes.
"""

# Texto de reemplazo para cada módulo

usuario_create_new = '''@login_required
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
                if 'django_user' in locals():
                    django_user.delete()  # Rollback si falla
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = UsuarioForm()

    return render(request, 'mi_condominio/usuarios/form.html', {
        'form': form,
        'action': 'Crear',
        'usuario': None,
    })'''

usuario_edit_new = '''@login_required
def usuario_edit(request, pk):
    """
    Vista para editar un usuario existente usando Django Forms.
    """
    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            usuario = form.save()

            # Actualizar User de Django si existe
            if usuario.user:
                usuario.user.email = usuario.correo
                usuario.user.first_name = usuario.nombres
                usuario.user.last_name = usuario.apellido
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
    })'''

print("Template views created. Apply manually.")
print("\nUsuario Create:")
print(usuario_create_new)
print("\nUsuario Edit:")
print(usuario_edit_new)
