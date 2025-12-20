"""
Formularios Django para la aplicación Mi Condominio.
Incluye validaciones personalizadas para garantizar integridad de datos.
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date
import re
from .models import (
    Condominio,
    Usuario,
    Reunion,
    Incidencia,
    CategoriaIncidencia,
    Bitacora,
    EvidenciaIncidencia,
    Amonestacion
)


# ==================== VALIDADORES PERSONALIZADOS ====================

def validate_rut_chileno(value):
    """
    Valida el formato del RUT chileno.
    Acepta formato: XX.XXX.XXX-X o XXXXXXXX-X
    """
    # Remover puntos y guiones para validar
    rut_limpio = value.replace('.', '').replace('-', '').strip()

    # Validar largo (7-9 dígitos)
    if not (7 <= len(rut_limpio) <= 9):
        raise ValidationError('El RUT debe tener entre 7 y 9 caracteres (sin contar puntos y guión).')

    # Validar que tenga solo números y opcionalmente K/k al final
    if not re.match(r'^\d{7,8}[0-9Kk]$', rut_limpio):
        raise ValidationError('El RUT debe contener solo números y puede terminar en K.')

    return value


def validate_email_unique_case_insensitive(email, exclude_id=None, model_field='correo'):
    """
    Valida que el email sea único (case-insensitive).
    """
    from .models import Usuario

    if Usuario.objects.filter(correo__iexact=email).exclude(id=exclude_id).exists():
        raise ValidationError('Ya existe un usuario con este correo electrónico.')


def validate_fecha_no_pasada(value):
    """
    Valida que la fecha no sea en el pasado.
    """
    if value < date.today():
        raise ValidationError('La fecha no puede ser en el pasado.')


def validate_fecha_no_muy_futura(value, max_years=5):
    """
    Valida que la fecha no sea demasiado en el futuro.
    """
    from datetime import timedelta
    max_date = date.today() + timedelta(days=365 * max_years)
    if value > max_date:
        raise ValidationError(f'La fecha no puede ser más de {max_years} años en el futuro.')


# ==================== FORMULARIOS ====================

class CondominioForm(forms.ModelForm):
    """Formulario para crear/editar Condominios."""

    class Meta:
        model = Condominio
        fields = ['rut', 'nombre', 'direccion', 'region', 'comuna', 'mail_contacto']
        widgets = {
            'rut': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'XX.XXX.XXX-X',
                'maxlength': '12'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del condominio'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección completa'
            }),
            'region': forms.Select(attrs={
                'class': 'form-select'
            }, choices=[
                ('', 'Seleccione una región'),
                ('Arica y Parinacota', 'Arica y Parinacota'),
                ('Tarapacá', 'Tarapacá'),
                ('Antofagasta', 'Antofagasta'),
                ('Atacama', 'Atacama'),
                ('Coquimbo', 'Coquimbo'),
                ('Valparaíso', 'Valparaíso'),
                ('Metropolitana', 'Metropolitana'),
                ('O\'Higgins', 'O\'Higgins'),
                ('Maule', 'Maule'),
                ('Ñuble', 'Ñuble'),
                ('Biobío', 'Biobío'),
                ('Araucanía', 'Araucanía'),
                ('Los Ríos', 'Los Ríos'),
                ('Los Lagos', 'Los Lagos'),
                ('Aysén', 'Aysén'),
                ('Magallanes', 'Magallanes'),
            ]),
            'comuna': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Comuna'
            }),
            'mail_contacto': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
        }

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        if rut:
            validate_rut_chileno(rut)

            # Validar unicidad (excluyendo el registro actual en edición)
            qs = Condominio.objects.filter(rut=rut)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                raise ValidationError('Ya existe un condominio con este RUT.')

        return rut

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if nombre and len(nombre.strip()) < 3:
            raise ValidationError('El nombre debe tener al menos 3 caracteres.')
        return nombre

    def clean_mail_contacto(self):
        email = self.cleaned_data.get('mail_contacto')
        if email:
            # Validar formato básico (Django ya lo hace, pero podemos agregar más)
            if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                raise ValidationError('Ingrese un correo electrónico válido.')
        return email


class UsuarioForm(forms.ModelForm):
    """Formulario para crear/editar Usuarios."""

    class Meta:
        model = Usuario
        fields = ['condominio', 'nombres', 'apellido', 'genero', 'rut',
                  'correo', 'residencia', 'tipo_usuario', 'estado_cuenta']
        widgets = {
            'condominio': forms.Select(attrs={'class': 'form-select'}),
            'nombres': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombres'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellidos'
            }),
            'genero': forms.Select(attrs={'class': 'form-select'}),
            'rut': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'XX.XXX.XXX-X',
                'maxlength': '12'
            }),
            'correo': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'usuario@ejemplo.com'
            }),
            'residencia': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Dirección de residencia (opcional)'
            }),
            'tipo_usuario': forms.Select(attrs={'class': 'form-select'}),
            'estado_cuenta': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        if rut:
            validate_rut_chileno(rut)

            # Validar unicidad
            qs = Usuario.objects.filter(rut=rut)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                raise ValidationError('Ya existe un usuario con este RUT.')

        return rut

    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        if correo:
            # Validar unicidad (case-insensitive)
            qs = Usuario.objects.filter(correo__iexact=correo)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                raise ValidationError('Ya existe un usuario con este correo electrónico.')

        return correo

    def clean_nombres(self):
        nombres = self.cleaned_data.get('nombres')
        if nombres and len(nombres.strip()) < 2:
            raise ValidationError('Los nombres deben tener al menos 2 caracteres.')
        return nombres

    def clean_apellido(self):
        apellido = self.cleaned_data.get('apellido')
        if apellido and len(apellido.strip()) < 2:
            raise ValidationError('Los apellidos deben tener al menos 2 caracteres.')
        return apellido


class ReunionForm(forms.ModelForm):
    """Formulario para crear/editar Reuniones."""

    class Meta:
        model = Reunion
        fields = ['condominio', 'tipo_reunion', 'nombre_reunion',
                  'fecha_reunion', 'lugar_reunion', 'motivo_reunion', 'acta_reunion_url']
        widgets = {
            'condominio': forms.Select(attrs={'class': 'form-select'}),
            'tipo_reunion': forms.Select(attrs={'class': 'form-select'}),
            'nombre_reunion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la reunión'
            }),
            'fecha_reunion': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'lugar_reunion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Lugar de la reunión (opcional)'
            }),
            'motivo_reunion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Motivo o temática de la reunión (opcional)'
            }),
            'acta_reunion_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://ejemplo.com/acta.pdf (opcional)'
            }),
        }

    def clean_fecha_reunion(self):
        fecha = self.cleaned_data.get('fecha_reunion')
        if fecha:
            # Validar que no sea muy antigua (más de 6 meses atrás)
            from datetime import timedelta
            fecha_minima = date.today() - timedelta(days=180)

            if fecha < fecha_minima:
                raise ValidationError('La fecha de la reunión no puede ser más de 6 meses en el pasado.')

            # Validar que no sea muy futura
            validate_fecha_no_muy_futura(fecha, max_years=2)

        return fecha

    def clean_nombre_reunion(self):
        nombre = self.cleaned_data.get('nombre_reunion')
        if nombre and len(nombre.strip()) < 3:
            raise ValidationError('El nombre debe tener al menos 3 caracteres.')
        return nombre


class IncidenciaForm(forms.ModelForm):
    """Formulario para crear/editar Incidencias."""

    class Meta:
        model = Incidencia
        fields = ['condominio', 'tipo_incidencia', 'titulo', 'descripcion',
                  'estado', 'prioridad', 'ubicacion_latitud_reporte',
                  'ubicacion_longitud_reporte', 'direccion_condominio_incidencia',
                  'usuario_reporta', 'fecha_cierre']
        widgets = {
            'condominio': forms.Select(attrs={'class': 'form-select'}),
            'tipo_incidencia': forms.Select(attrs={'class': 'form-select'}),
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título de la incidencia'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descripción detallada (opcional)'
            }),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'prioridad': forms.Select(attrs={'class': 'form-select'}),
            'ubicacion_latitud_reporte': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'ubicacion_latitud',
                'readonly': 'readonly',
                'placeholder': 'Latitud (automático)'
            }),
            'ubicacion_longitud_reporte': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'ubicacion_longitud',
                'readonly': 'readonly',
                'placeholder': 'Longitud (automático)'
            }),
            'direccion_condominio_incidencia': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'direccion_incidencia',
                'readonly': 'readonly',
                'placeholder': 'Dirección (automático)'
            }),
            'usuario_reporta': forms.Select(attrs={'class': 'form-select'}),
            'fecha_cierre': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

    def clean_titulo(self):
        titulo = self.cleaned_data.get('titulo')
        if titulo and len(titulo.strip()) < 5:
            raise ValidationError('El título debe tener al menos 5 caracteres.')
        return titulo

    def clean_fecha_cierre(self):
        fecha_cierre = self.cleaned_data.get('fecha_cierre')
        estado = self.cleaned_data.get('estado')

        # Si el estado es CERRADA, debe tener fecha de cierre
        if estado == 'CERRADA' and not fecha_cierre:
            raise ValidationError('Debe especificar una fecha de cierre si el estado es CERRADA.')

        # La fecha de cierre no puede ser futura
        if fecha_cierre and fecha_cierre > date.today():
            raise ValidationError('La fecha de cierre no puede ser en el futuro.')

        return fecha_cierre

    def clean(self):
        cleaned_data = super().clean()
        estado = cleaned_data.get('estado')
        fecha_cierre = cleaned_data.get('fecha_cierre')

        # Validar coherencia entre estado y fecha de cierre
        if estado in ['CERRADA', 'CANCELADA'] and not fecha_cierre:
            cleaned_data['fecha_cierre'] = date.today()

        return cleaned_data


class CategoriaIncidenciaForm(forms.ModelForm):
    """Formulario para crear/editar Categorías de Incidencia."""

    class Meta:
        model = CategoriaIncidencia
        fields = ['nombre_categoria_incidencia']
        widgets = {
            'nombre_categoria_incidencia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la categoría'
            }),
        }

    def clean_nombre_categoria_incidencia(self):
        nombre = self.cleaned_data.get('nombre_categoria_incidencia')
        if nombre:
            # Validar largo mínimo
            if len(nombre.strip()) < 3:
                raise ValidationError('El nombre debe tener al menos 3 caracteres.')

            # Validar unicidad (case-insensitive)
            qs = CategoriaIncidencia.objects.filter(nombre_categoria_incidencia__iexact=nombre)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                raise ValidationError('Ya existe una categoría con este nombre.')

        return nombre


class BitacoraForm(forms.ModelForm):
    """Formulario para crear/editar Bitácoras."""

    class Meta:
        model = Bitacora
        fields = ['incidencia', 'detalle', 'accion']
        widgets = {
            'incidencia': forms.Select(attrs={'class': 'form-select'}),
            'detalle': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Detalle del registro (opcional)'
            }),
            'accion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Acción ejecutada (opcional)'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        detalle = cleaned_data.get('detalle')
        accion = cleaned_data.get('accion')

        # Al menos uno de los dos debe estar presente
        if not detalle and not accion:
            raise ValidationError('Debe proporcionar al menos un detalle o una acción.')

        return cleaned_data


class EvidenciaIncidenciaForm(forms.ModelForm):
    """Formulario para crear/editar Evidencias con upload de archivos."""

    class Meta:
        model = EvidenciaIncidencia
        fields = ['incidencia', 'archivo_evidencia', 'tipo_archivo_evidencia']
        widgets = {
            'incidencia': forms.Select(attrs={'class': 'form-select'}),
            'archivo_evidencia': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*,video/*,audio/*,.pdf,.doc,.docx,.xls,.xlsx,.txt'
            }),
            'tipo_archivo_evidencia': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_archivo_evidencia(self):
        archivo = self.cleaned_data.get('archivo_evidencia')
        if archivo:
            # Validar tamaño del archivo (máximo 50MB)
            max_size = 50 * 1024 * 1024  # 50MB en bytes
            if archivo.size > max_size:
                raise ValidationError(f'El archivo es demasiado grande. Tamaño máximo: 50MB. Tamaño actual: {archivo.size / (1024*1024):.2f}MB')

            # Obtener extensión del archivo
            import os
            extension = os.path.splitext(archivo.name)[1].lower()

            # Validar extensión según tipo de archivo
            tipo_archivo = self.data.get('tipo_archivo_evidencia')
            extensiones_validas = {
                'IMAGEN': ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp'],
                'VIDEO': ['.mp4', '.avi', '.mov', '.wmv', '.webm', '.mkv'],
                'DOCUMENTO': ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt', '.odt', '.ods'],
                'AUDIO': ['.mp3', '.wav', '.ogg', '.m4a', '.aac'],
                'OTRO': []  # Acepta cualquier extensión
            }

            # Validar extensión si se especificó un tipo
            if tipo_archivo and tipo_archivo in extensiones_validas and extensiones_validas[tipo_archivo]:
                if extension not in extensiones_validas[tipo_archivo]:
                    extensiones_texto = ', '.join(extensiones_validas[tipo_archivo])
                    raise ValidationError(
                        f'El archivo no corresponde al tipo "{tipo_archivo}". '
                        f'Extensiones válidas: {extensiones_texto}'
                    )

        return archivo

    def clean(self):
        cleaned_data = super().clean()
        archivo = cleaned_data.get('archivo_evidencia')
        tipo_archivo = cleaned_data.get('tipo_archivo_evidencia')

        # Autodetectar tipo de archivo si no se especificó
        if archivo and not tipo_archivo:
            import os
            extension = os.path.splitext(archivo.name)[1].lower()

            if extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp']:
                cleaned_data['tipo_archivo_evidencia'] = 'IMAGEN'
            elif extension in ['.mp4', '.avi', '.mov', '.wmv', '.webm', '.mkv']:
                cleaned_data['tipo_archivo_evidencia'] = 'VIDEO'
            elif extension in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt', '.odt', '.ods']:
                cleaned_data['tipo_archivo_evidencia'] = 'DOCUMENTO'
            elif extension in ['.mp3', '.wav', '.ogg', '.m4a', '.aac']:
                cleaned_data['tipo_archivo_evidencia'] = 'AUDIO'
            else:
                cleaned_data['tipo_archivo_evidencia'] = 'OTRO'

        return cleaned_data


class AmonestacionForm(forms.ModelForm):
    """Formulario para crear/editar Amonestaciones."""

    class Meta:
        model = Amonestacion
        fields = ['tipo_amonestacion', 'motivo', 'motivo_detalle', 'fecha_amonestacion',
                  'nombre_amonestado', 'apellidos_amonestado', 'rut_amonestado',
                  'numero_departamento', 'fecha_limite_pago', 'usuario_reporta']
        widgets = {
            'tipo_amonestacion': forms.Select(attrs={'class': 'form-select'}),
            'motivo': forms.Select(attrs={'class': 'form-select'}),
            'motivo_detalle': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Detalle adicional del motivo (opcional)'
            }),
            'fecha_amonestacion': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'nombre_amonestado': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del sancionado'
            }),
            'apellidos_amonestado': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellidos del sancionado'
            }),
            'rut_amonestado': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'XX.XXX.XXX-X',
                'maxlength': '12'
            }),
            'numero_departamento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de departamento (opcional)'
            }),
            'fecha_limite_pago': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'usuario_reporta': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_rut_amonestado(self):
        rut = self.cleaned_data.get('rut_amonestado')
        if rut:
            validate_rut_chileno(rut)
        return rut

    def clean_fecha_amonestacion(self):
        fecha = self.cleaned_data.get('fecha_amonestacion')
        if fecha:
            # No puede ser muy antigua (más de 1 año)
            from datetime import timedelta
            fecha_minima = date.today() - timedelta(days=365)

            if fecha < fecha_minima:
                raise ValidationError('La fecha de amonestación no puede ser más de 1 año en el pasado.')

            # No puede ser futura
            if fecha > date.today():
                raise ValidationError('La fecha de amonestación no puede ser en el futuro.')

        return fecha

    def clean_fecha_limite_pago(self):
        fecha_limite = self.cleaned_data.get('fecha_limite_pago')
        fecha_amonestacion = self.cleaned_data.get('fecha_amonestacion')
        tipo_amonestacion = self.cleaned_data.get('tipo_amonestacion')

        # Si es MULTA, debe tener fecha límite
        if tipo_amonestacion == 'MULTA' and not fecha_limite:
            raise ValidationError('Las multas deben tener una fecha límite de pago.')

        # La fecha límite debe ser posterior a la fecha de amonestación
        if fecha_limite and fecha_amonestacion and fecha_limite <= fecha_amonestacion:
            raise ValidationError('La fecha límite de pago debe ser posterior a la fecha de amonestación.')

        return fecha_limite

    def clean_nombre_amonestado(self):
        nombre = self.cleaned_data.get('nombre_amonestado')
        if nombre and len(nombre.strip()) < 2:
            raise ValidationError('El nombre debe tener al menos 2 caracteres.')
        return nombre

    def clean_apellidos_amonestado(self):
        apellidos = self.cleaned_data.get('apellidos_amonestado')
        if apellidos and len(apellidos.strip()) < 2:
            raise ValidationError('Los apellidos deben tener al menos 2 caracteres.')
        return apellidos

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo_amonestacion')
        fecha_limite = cleaned_data.get('fecha_limite_pago')
        motivo = cleaned_data.get('motivo')
        motivo_detalle = cleaned_data.get('motivo_detalle')

        # Si el motivo es OTRO, el detalle es obligatorio
        if motivo == 'OTRO' and not motivo_detalle:
            raise ValidationError('Debe especificar el detalle del motivo cuando selecciona "Otro motivo".')

        # Si NO es MULTA, no debería tener fecha límite
        if tipo != 'MULTA' and fecha_limite:
            self.add_error('fecha_limite_pago', 'Solo las multas deben tener fecha límite de pago.')

        return cleaned_data
