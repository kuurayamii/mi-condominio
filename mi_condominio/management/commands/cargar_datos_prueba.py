"""
Management command para cargar datos de prueba en el sistema.
Carga 50 registros de cada modelo (excepto Comuna, Region, ChatSession, ChatMessage).
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from mi_condominio.models import (
    Condominio, Usuario, Reunion, CategoriaIncidencia,
    Incidencia, Bitacora, EvidenciaIncidencia, Amonestacion,
    Region, Comuna
)
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Carga 50 registros de prueba para cada modelo del sistema'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando carga de datos de prueba...\n')

        # Verificar que existan regiones y comunas
        if not Region.objects.exists():
            self.stdout.write(self.style.ERROR(
                'Error: No hay regiones en la base de datos. '
                'Ejecuta primero: python manage.py cargar_regiones_comunas'
            ))
            return

        # Verificar que existan categorías de incidencias
        if not CategoriaIncidencia.objects.exists():
            self.stdout.write(self.style.ERROR(
                'Error: No hay categorías de incidencias. '
                'Ejecuta primero: python manage.py cargar_categorias'
            ))
            return

        # Cargar condominios
        self.cargar_condominios()

        # Cargar usuarios
        self.cargar_usuarios()

        # Cargar reuniones
        self.cargar_reuniones()

        # Cargar incidencias
        self.cargar_incidencias()

        # Cargar bitácoras
        self.cargar_bitacoras()

        # Cargar evidencias
        self.cargar_evidencias()

        # Cargar amonestaciones
        self.cargar_amonestaciones()

        self.stdout.write(self.style.SUCCESS('\n¡Datos de prueba cargados exitosamente!'))

    def cargar_condominios(self):
        """Carga 50 condominios de prueba."""
        self.stdout.write('Cargando condominios...')

        nombres_condominios = [
            'Edificio Las Condes', 'Condominio Los Olivos', 'Torres del Sol',
            'Residencial El Parque', 'Edificio Vista Hermosa', 'Condominio Los Aromos',
            'Torres Mirador', 'Residencial San Martín', 'Edificio Portal del Mar',
            'Condominio Los Pinos', 'Torres Andalucía', 'Residencial Santa Rosa',
            'Edificio Alameda Central', 'Condominio Los Jardines', 'Torres del Valle',
            'Residencial Las Palmas', 'Edificio Providencia', 'Condominio El Bosque',
            'Torres Cordillera', 'Residencial Los Castaños', 'Edificio Bello Horizonte',
            'Condominio Los Cerezos', 'Torres Plaza Mayor', 'Residencial San Andrés',
            'Edificio Costa Azul', 'Condominio Los Robles', 'Torres del Pacífico',
            'Residencial Las Acacias', 'Edificio Nueva Aurora', 'Condominio El Arrayán',
            'Torres Los Leones', 'Residencial Monte Verde', 'Edificio Bellavista',
            'Condominio Los Sauces', 'Torres Ñuñoa', 'Residencial San Jorge',
            'Edificio Portal Oriente', 'Condominio Los Almendros', 'Torres Mapocho',
            'Residencial El Olivar', 'Edificio Las Lilas', 'Condominio Los Nogales',
            'Torres Apoquindo', 'Residencial Santa Elena', 'Edificio Plaza Norte',
            'Condominio Los Laureles', 'Torres Del Carmen', 'Residencial San Rafael',
            'Edificio Costanera', 'Condominio Los Eucaliptos'
        ]

        comunas = list(Comuna.objects.all())

        for i in range(len(nombres_condominios)):
            comuna = random.choice(comunas)
            # RUT fijo basado en el índice (sin componente aleatorio)
            rut_num = 70000000 + (i + 1) * 1000
            rut = f"{rut_num // 10}-{rut_num % 10}"

            condominio, created = Condominio.objects.get_or_create(
                rut=rut,
                defaults={
                    'nombre': nombres_condominios[i],
                    'direccion': f'{random.choice(["Av.", "Calle", "Pasaje"])} {random.choice(["Los Pinos", "Las Rosas", "El Bosque", "Santa María", "San José"])} {random.randint(100, 9999)}',
                    'region': comuna.region,
                    'comuna': comuna,
                    'mail_contacto': f'contacto{i+1}@{nombres_condominios[i].lower().replace(" ", "")}.cl'
                }
            )

            if created:
                self.stdout.write(f'  ✓ Condominio: {condominio.nombre}')

    def cargar_usuarios(self):
        """Carga 50 usuarios de prueba."""
        self.stdout.write('\nCargando usuarios...')

        nombres = [
            'Juan', 'María', 'Pedro', 'Ana', 'Carlos', 'Luisa', 'Jorge', 'Carmen',
            'Roberto', 'Patricia', 'Francisco', 'Isabel', 'Miguel', 'Rosa', 'José',
            'Teresa', 'Antonio', 'Laura', 'Manuel', 'Silvia', 'Ricardo', 'Elena',
            'Fernando', 'Mónica', 'Alejandro', 'Claudia', 'Sergio', 'Andrea',
            'Diego', 'Beatriz', 'Raúl', 'Gabriela', 'Andrés', 'Cecilia', 'Pablo',
            'Verónica', 'Javier', 'Marcela', 'Rodrigo', 'Daniela', 'Cristian',
            'Alejandra', 'Gonzalo', 'Paulina', 'Eduardo', 'Francisca', 'Hernán',
            'Carolina', 'Mauricio', 'Valentina'
        ]

        apellidos = [
            'González', 'Muñoz', 'Rojas', 'Díaz', 'Pérez', 'Soto', 'Contreras',
            'Silva', 'Martínez', 'Sepúlveda', 'Morales', 'Rodríguez', 'López',
            'Fuentes', 'Hernández', 'Torres', 'Araya', 'Flores', 'Espinoza',
            'Valenzuela', 'Castillo', 'Reyes', 'Vergara', 'Castro', 'Ramírez'
        ]

        condominios = list(Condominio.objects.all())
        tipos_usuario = ['ADMIN', 'SUPERVISOR', 'CONSERJE']
        generos = ['M', 'F', 'O', 'N']

        for i in range(50):
            rut_num = 15000000 + i * 100000 + random.randint(1000, 9999)
            rut = f"{rut_num // 10}-{rut_num % 10}"
            nombre = nombres[i]
            apellido = f"{random.choice(apellidos)} {random.choice(apellidos)}"

            # Crear usuario Django si es ADMIN
            tipo = random.choice(tipos_usuario)
            django_user = None

            if tipo == 'ADMIN':
                username = f"{nombre.lower()}.{apellido.split()[0].lower()}.{i}.{random.randint(100, 999)}"
                django_user, _ = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': f'{username}@condominio.cl',
                        'first_name': nombre,
                        'last_name': apellido.split()[0]
                    }
                )

            # Generar email único usando timestamp
            email_unico = f'{nombre.lower()}.{apellido.split()[0].lower()}.{i}.{random.randint(1000, 9999)}@email.cl'

            usuario, created = Usuario.objects.get_or_create(
                rut=rut,
                defaults={
                    'user': django_user,
                    'condominio': random.choice(condominios),
                    'nombres': nombre,
                    'apellido': apellido,
                    'genero': random.choice(generos),
                    'correo': email_unico,
                    'residencia': f'Depto {random.randint(100, 999)}',
                    'tipo_usuario': tipo,
                    'estado_cuenta': random.choice(['ACTIVO', 'ACTIVO', 'ACTIVO', 'INACTIVO'])  # 75% activos
                }
            )

            if created:
                self.stdout.write(f'  ✓ Usuario: {usuario.nombres} {usuario.apellido} ({usuario.tipo_usuario})')

    def cargar_reuniones(self):
        """Carga 50 reuniones de prueba."""
        self.stdout.write('\nCargando reuniones...')

        condominios = list(Condominio.objects.all())
        tipos_reunion = ['ORDINARIA', 'EXTRAORDINARIA', 'INFORMATIVA']

        temas_reunion = [
            'Asamblea', 'Presupuesto', 'Obras', 'Normativa', 'Reparaciones',
            'Gastos Comunes', 'Seguridad', 'Áreas Comunes', 'Reglamento',
            'Directiva', 'Mantención', 'Deudores', 'Cámaras', 'Pintura',
            'Portones', 'Quincho', 'Iluminación', 'Jardines', 'Riego',
            'Ascensores', 'Estacionamiento', 'Bicicleteros', 'Eventos',
            'Gimnasio', 'Piscina'
        ]

        lugares = [
            'Quincho del Condominio', 'Sala de Eventos', 'Salón Multiuso',
            'Sala de Reuniones', 'Hall Principal', 'Terraza Común'
        ]

        for i in range(50):
            dias_offset = random.randint(-180, 180)  # Reuniones en los últimos 6 meses y próximos 6 meses
            fecha = datetime.now().date() + timedelta(days=dias_offset)

            # Nombre de reunión corto (máx 20 caracteres)
            nombre_corto = f"{random.choice(temas_reunion)[:10]} {i+1}"

            reunion, created = Reunion.objects.get_or_create(
                condominio=random.choice(condominios),
                fecha_reunion=fecha,
                nombre_reunion=nombre_corto[:20],  # Asegurar máximo 20 caracteres
                defaults={
                    'tipo_reunion': random.choice(tipos_reunion),
                    'lugar_reunion': random.choice(lugares),
                    'motivo_reunion': f'Reunión para tratar temas relacionados con {random.choice(temas_reunion).lower()}',
                    'acta_reunion_url': f'https://drive.google.com/actas/reunion-{i+1}' if random.choice([True, False]) else None
                }
            )

            if created:
                self.stdout.write(f'  ✓ Reunión: {reunion.nombre_reunion} ({reunion.tipo_reunion})')

    def cargar_incidencias(self):
        """Carga 50 incidencias de prueba."""
        self.stdout.write('\nCargando incidencias...')

        condominios = list(Condominio.objects.all())
        categorias = list(CategoriaIncidencia.objects.all())
        usuarios = list(Usuario.objects.all())
        estados = ['PENDIENTE', 'EN_PROCESO', 'RESUELTA', 'CERRADA', 'CANCELADA']
        prioridades = ['BAJA', 'MEDIA', 'ALTA', 'URGENTE']

        titulos_por_categoria = {
            'Mantenimiento': ['Puerta dañada en hall', 'Pintura descascarada', 'Manija rota'],
            'Seguridad': ['Portón no cierra', 'Cámara sin funcionar', 'Cerradura forzada'],
            'Limpieza': ['Basura en escaleras', 'Vidrios sucios', 'Jardín descuidado'],
            'Ruidos Molestos': ['Música alta nocturna', 'Obras fuera de horario', 'Perro ladrando'],
            'Estacionamientos': ['Auto mal estacionado', 'Goteras en subterráneo', 'Iluminación apagada'],
            'Áreas Comunes': ['Quincho sucio', 'Mobiliario roto', 'Piscina sin cloro'],
            'Agua': ['Fuga en baño común', 'Cañería rota', 'Presión baja'],
            'Electricidad': ['Corte de luz', 'Ampolleta quemada', 'Cortocircuito'],
            'Ascensores': ['Ascensor detenido', 'Botones sin funcionar', 'Puerta atascada']
        }

        for i in range(50):
            categoria = random.choice(categorias)
            condominio = random.choice(condominios)

            # Obtener títulos para esta categoría o usar genéricos
            titulos = titulos_por_categoria.get(categoria.nombre_categoria_incidencia, ['Incidencia reportada'])

            dias_offset = random.randint(-90, 0)  # Incidencias en los últimos 3 meses
            fecha_reporte = datetime.now().date() + timedelta(days=dias_offset)

            estado = random.choice(estados)
            fecha_cierre = None
            if estado in ['RESUELTA', 'CERRADA', 'CANCELADA']:
                fecha_cierre = fecha_reporte + timedelta(days=random.randint(1, 30))

            # Generar coordenadas ficticias de Santiago, Chile
            lat_base = -33.4489  # Santiago
            lon_base = -70.6693
            lat = str(lat_base + random.uniform(-0.1, 0.1))
            lon = str(lon_base + random.uniform(-0.1, 0.1))

            incidencia, created = Incidencia.objects.get_or_create(
                condominio=condominio,
                titulo=f"{random.choice(titulos)} - Caso {i+1}",
                defaults={
                    'tipo_incidencia': categoria,
                    'descripcion': f'Descripción detallada de la incidencia {i+1}. Se requiere atención para resolver el problema reportado.',
                    'estado': estado,
                    'prioridad': random.choice(prioridades),
                    'ubicacion_latitud_reporte': lat,
                    'ubicacion_longitud_reporte': lon,
                    'direccion_condominio_incidencia': condominio.direccion,
                    'usuario_reporta': random.choice(usuarios),
                    'fecha_cierre': fecha_cierre
                }
            )

            if created:
                self.stdout.write(f'  ✓ Incidencia: {incidencia.titulo} ({incidencia.estado})')

    def cargar_bitacoras(self):
        """Carga 50 entradas de bitácora de prueba."""
        self.stdout.write('\nCargando bitácoras...')

        incidencias = list(Incidencia.objects.all())

        acciones = [
            'Se contactó al proveedor',
            'Se realizó inspección del lugar',
            'Se solicitó cotización',
            'Se programó visita técnica',
            'Se ejecutó reparación',
            'Se verificó solución',
            'Se cerró caso',
            'Se escaló a supervisor',
            'Se notificó a los residentes',
            'Se actualizó estado'
        ]

        detalles = [
            'Proveedor confirmó visita para mañana',
            'Inspección reveló daño mayor al esperado',
            'Cotización recibida por $150.000',
            'Técnico visitará el viernes en la tarde',
            'Reparación completada exitosamente',
            'Solución verificada y funcionando correctamente',
            'Caso cerrado tras confirmación de residente',
            'Caso requiere aprobación de directiva',
            'Se envió circular a todos los departamentos',
            'Estado actualizado según avance del trabajo'
        ]

        for i in range(50):
            incidencia = random.choice(incidencias)

            bitacora, created = Bitacora.objects.get_or_create(
                incidencia=incidencia,
                detalle=random.choice(detalles),
                accion=random.choice(acciones),
                defaults={}
            )

            if created:
                self.stdout.write(f'  ✓ Bitácora: {bitacora.accion} (Incidencia #{bitacora.incidencia.id})')

    def cargar_evidencias(self):
        """Carga 50 evidencias de prueba."""
        self.stdout.write('\nCargando evidencias...')

        incidencias = list(Incidencia.objects.all())
        tipos_archivo = ['IMAGEN', 'VIDEO', 'DOCUMENTO', 'AUDIO', 'OTRO']

        for i in range(50):
            incidencia = random.choice(incidencias)
            tipo = random.choice(tipos_archivo)

            # Crear evidencia sin archivo (campo nullable)
            # En producción se cargarían archivos reales
            evidencia = EvidenciaIncidencia.objects.create(
                incidencia=incidencia,
                tipo_archivo_evidencia=tipo,
                archivo_evidencia=None  # Sin archivo por ahora
            )

            self.stdout.write(f'  ✓ Evidencia: {evidencia.tipo_archivo_evidencia} (Incidencia #{evidencia.incidencia.id})')

    def cargar_amonestaciones(self):
        """Carga 50 amonestaciones de prueba."""
        self.stdout.write('\nCargando amonestaciones...')

        usuarios = list(Usuario.objects.all())
        condominios = list(Condominio.objects.all())

        tipos_amonestacion = ['VERBAL', 'ESCRITA', 'MULTA', 'SUSPENSION']

        motivos = [
            'RUIDOS_MOLESTOS', 'USO_INDEBIDO_ESTACIONAMIENTOS', 'DANO_BIEN_COMUN',
            'MAL_USO_AREA_COMUN', 'INCUMPLIMIENTO_NORMAS_SANITARIAS', 'TENENCIA_IRRESPONSABLE',
            'MAL_USO_DUCTOS_BASURA', 'ARRIENDO_ILEGAL', 'INCUMPLIMIENTO_OBRAS_REMODELACIONES',
            'IMPEDIMENTO_LABORES_ADMINISTRATIVAS', 'SEGURIDAD', 'OTRO'
        ]

        nombres = [
            'Pedro', 'Ana', 'Carlos', 'Luisa', 'Jorge', 'Carmen', 'Roberto',
            'Patricia', 'Francisco', 'Isabel', 'Miguel', 'Rosa', 'José',
            'Teresa', 'Antonio', 'Laura', 'Manuel', 'Silvia', 'Ricardo'
        ]

        apellidos = [
            'González', 'Muñoz', 'Rojas', 'Díaz', 'Pérez', 'Soto', 'Contreras',
            'Silva', 'Martínez', 'Sepúlveda', 'Morales', 'Rodríguez'
        ]

        for i in range(50):
            tipo = random.choice(tipos_amonestacion)
            motivo = random.choice(motivos)

            dias_offset = random.randint(-180, 0)  # Amonestaciones en los últimos 6 meses
            fecha_amonestacion = datetime.now().date() + timedelta(days=dias_offset)

            rut_num = 16000000 + i * 100000 + random.randint(1000, 9999)
            rut = f"{rut_num // 10}-{rut_num % 10}"

            # Fecha límite de pago solo si es MULTA
            fecha_limite = None
            if tipo == 'MULTA':
                fecha_limite = fecha_amonestacion + timedelta(days=30)

            motivo_detalle = None
            if motivo == 'OTRO':
                motivo_detalle = f'Motivo detallado de la amonestación número {i+1}'

            amonestacion, created = Amonestacion.objects.get_or_create(
                rut_amonestado=rut,
                fecha_amonestacion=fecha_amonestacion,
                defaults={
                    'tipo_amonestacion': tipo,
                    'motivo': motivo,
                    'motivo_detalle': motivo_detalle,
                    'nombre_amonestado': random.choice(nombres),
                    'apellidos_amonestado': f"{random.choice(apellidos)} {random.choice(apellidos)}",
                    'numero_departamento': f'{random.randint(1, 20)}{random.randint(1, 15):02d}',
                    'fecha_limite_pago': fecha_limite,
                    'usuario_reporta': random.choice(usuarios)
                }
            )

            if created:
                self.stdout.write(f'  ✓ Amonestación: {amonestacion.tipo_amonestacion} - {amonestacion.nombre_amonestado}')
