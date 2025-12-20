"""
Management command para cargar las regiones y comunas de Chile.

Este comando pobla la base de datos con las 16 regiones de Chile
y sus respectivas comunas.

Uso:
    python manage.py cargar_regiones_comunas
"""

from django.core.management.base import BaseCommand
from mi_condominio.models import Region, Comuna


class Command(BaseCommand):
    help = 'Carga las regiones y comunas de Chile en la base de datos'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando carga de regiones y comunas de Chile...\n')

        # Datos de regiones y comunas
        regiones_comunas = {
            'XV': {
                'nombre': 'Región de Arica y Parinacota',
                'numero_romano': 'XV',
                'comunas': ['Arica', 'Camarones', 'Putre', 'General Lagos']
            },
            'I': {
                'nombre': 'Región de Tarapacá',
                'numero_romano': 'I',
                'comunas': ['Iquique', 'Alto Hospicio', 'Pozo Almonte', 'Camiña', 'Colchane', 'Huara', 'Pica']
            },
            'II': {
                'nombre': 'Región de Antofagasta',
                'numero_romano': 'II',
                'comunas': ['Antofagasta', 'Mejillones', 'Sierra Gorda', 'Taltal', 'Calama', 'Ollagüe', 'San Pedro de Atacama', 'Tocopilla', 'María Elena']
            },
            'III': {
                'nombre': 'Región de Atacama',
                'numero_romano': 'III',
                'comunas': ['Copiapó', 'Caldera', 'Tierra Amarilla', 'Chañaral', 'Diego de Almagro', 'Vallenar', 'Alto del Carmen', 'Freirina', 'Huasco']
            },
            'IV': {
                'nombre': 'Región de Coquimbo',
                'numero_romano': 'IV',
                'comunas': ['La Serena', 'Coquimbo', 'Andacollo', 'La Higuera', 'Paiguano', 'Vicuña', 'Illapel', 'Canela', 'Los Vilos', 'Salamanca', 'Ovalle', 'Combarbalá', 'Monte Patria', 'Punitaqui', 'Río Hurtado']
            },
            'V': {
                'nombre': 'Región de Valparaíso',
                'numero_romano': 'V',
                'comunas': ['Valparaíso', 'Casablanca', 'Concón', 'Juan Fernández', 'Puchuncaví', 'Quintero', 'Viña del Mar', 'Isla de Pascua', 'Los Andes', 'Calle Larga', 'Rinconada', 'San Esteban', 'La Ligua', 'Cabildo', 'Papudo', 'Petorca', 'Zapallar', 'Quillota', 'Calera', 'Hijuelas', 'La Cruz', 'Nogales', 'San Antonio', 'Algarrobo', 'Cartagena', 'El Quisco', 'El Tabo', 'Santo Domingo', 'San Felipe', 'Catemu', 'Llaillay', 'Panquehue', 'Putaendo', 'Santa María', 'Quilpué', 'Limache', 'Olmué', 'Villa Alemana']
            },
            'RM': {
                'nombre': 'Región Metropolitana de Santiago',
                'numero_romano': 'XIII',
                'comunas': ['Cerrillos', 'Cerro Navia', 'Conchalí', 'El Bosque', 'Estación Central', 'Huechuraba', 'Independencia', 'La Cisterna', 'La Florida', 'La Granja', 'La Pintana', 'La Reina', 'Las Condes', 'Lo Barnechea', 'Lo Espejo', 'Lo Prado', 'Macul', 'Maipú', 'Ñuñoa', 'Pedro Aguirre Cerda', 'Peñalolén', 'Providencia', 'Pudahuel', 'Quilicura', 'Quinta Normal', 'Recoleta', 'Renca', 'San Joaquín', 'San Miguel', 'San Ramón', 'Vitacura', 'Puente Alto', 'Pirque', 'San José de Maipo', 'Colina', 'Lampa', 'Tiltil', 'San Bernardo', 'Buin', 'Calera de Tango', 'Paine', 'Melipilla', 'Alhué', 'Curacaví', 'María Pinto', 'San Pedro', 'Talagante', 'El Monte', 'Isla de Maipo', 'Padre Hurtado', 'Peñaflor', 'Santiago']
            },
            'VI': {
                'nombre': 'Región del Libertador General Bernardo O\'Higgins',
                'numero_romano': 'VI',
                'comunas': ['Rancagua', 'Codegua', 'Coinco', 'Coltauco', 'Doñihue', 'Graneros', 'Las Cabras', 'Machalí', 'Malloa', 'Mostazal', 'Olivar', 'Peumo', 'Pichidegua', 'Quinta de Tilcoco', 'Rengo', 'Requínoa', 'San Vicente', 'Pichilemu', 'La Estrella', 'Litueche', 'Marchihue', 'Navidad', 'Paredones', 'San Fernando', 'Chépica', 'Chimbarongo', 'Lolol', 'Nancagua', 'Palmilla', 'Peralillo', 'Placilla', 'Pumanque', 'Santa Cruz']
            },
            'VII': {
                'nombre': 'Región del Maule',
                'numero_romano': 'VII',
                'comunas': ['Talca', 'ConsVitución', 'Curepto', 'Empedrado', 'Maule', 'Pelarco', 'Pencahue', 'Río Claro', 'San Clemente', 'San Rafael', 'Cauquenes', 'Chanco', 'Pelluhue', 'Curicó', 'Hualañé', 'Licantén', 'Molina', 'Rauco', 'Romeral', 'Sagrada Familia', 'Teno', 'Vichuquén', 'Linares', 'Colbún', 'Longaví', 'Parral', 'Retiro', 'San Javier', 'Villa Alegre', 'Yerbas Buenas']
            },
            'VIII': {
                'nombre': 'Región del Biobío',
                'numero_romano': 'VIII',
                'comunas': ['Concepción', 'Coronel', 'Chiguayante', 'Florida', 'Hualqui', 'Lota', 'Penco', 'San Pedro de la Paz', 'Santa Juana', 'Talcahuano', 'Tomé', 'Hualpén', 'Lebu', 'Arauco', 'Cañete', 'Contulmo', 'Curanilahue', 'Los Álamos', 'Tirúa', 'Los Ángeles', 'Antuco', 'Cabrero', 'Laja', 'Mulchén', 'Nacimiento', 'Negrete', 'Quilaco', 'Quilleco', 'San Rosendo', 'Santa Bárbara', 'Tucapel', 'Yumbel', 'Alto Biobío', 'Chillán', 'Bulnes', 'Cobquecura', 'Coelemu', 'Coihueco', 'Chillán Viejo', 'El Carmen', 'Ninhue', 'Ñiquén', 'Pemuco', 'Pinto', 'Portezuelo', 'Quillón', 'Quirihue', 'Ránquil', 'San Carlos', 'San Fabián', 'San Ignacio', 'San Nicolás', 'Treguaco', 'Yungay']
            },
            'IX': {
                'nombre': 'Región de La Araucanía',
                'numero_romano': 'IX',
                'comunas': ['Temuco', 'Carahue', 'Cunco', 'Curarrehue', 'Freire', 'Galvarino', 'Gorbea', 'Lautaro', 'Loncoche', 'Melipeuco', 'Nueva Imperial', 'Padre Las Casas', 'Perquenco', 'Pitrufquén', 'Pucón', 'Saavedra', 'Teodoro Schmidt', 'Toltén', 'Vilcún', 'Villarrica', 'Cholchol', 'Angol', 'Collipulli', 'Curacautín', 'Ercilla', 'Lonquimay', 'Los Sauces', 'Lumaco', 'Purén', 'Renaico', 'Traiguén', 'Victoria']
            },
            'XIV': {
                'nombre': 'Región de Los Ríos',
                'numero_romano': 'XIV',
                'comunas': ['Valdivia', 'Corral', 'Lanco', 'Los Lagos', 'Máfil', 'Mariquina', 'Paillaco', 'Panguipulli', 'La Unión', 'Futrono', 'Lago Ranco', 'Río Bueno']
            },
            'X': {
                'nombre': 'Región de Los Lagos',
                'numero_romano': 'X',
                'comunas': ['Puerto Montt', 'Calbuco', 'Cochamó', 'Fresia', 'Frutillar', 'Los Muermos', 'Llanquihue', 'Maullín', 'Puerto Varas', 'Castro', 'Ancud', 'Chonchi', 'Curaco de Vélez', 'Dalcahue', 'Puqueldón', 'Queilén', 'Quellón', 'Quemchi', 'Quinchao', 'Osorno', 'Puerto Octay', 'Purranque', 'Puyehue', 'Río Negro', 'San Juan de la Costa', 'San Pablo', 'Chaitén', 'Futaleufú', 'Hualaihué', 'Palena']
            },
            'XI': {
                'nombre': 'Región Aysén del General Carlos Ibáñez del Campo',
                'numero_romano': 'XI',
                'comunas': ['Coyhaique', 'Lago Verde', 'Aysén', 'Cisnes', 'Guaitecas', 'Cochrane', 'O\'Higgins', 'Tortel', 'Chile Chico', 'Río Ibáñez']
            },
            'XII': {
                'nombre': 'Región de Magallanes y de la Antártica Chilena',
                'numero_romano': 'XII',
                'comunas': ['Punta Arenas', 'Laguna Blanca', 'Río Verde', 'San Gregorio', 'Cabo de Hornos', 'Antártica', 'Porvenir', 'Primavera', 'Timaukel', 'Natales', 'Torres del Paine']
            },
        }

        # Contadores
        regiones_creadas = 0
        regiones_existentes = 0
        comunas_creadas = 0
        comunas_existentes = 0

        # Cargar regiones y comunas
        for codigo, data in regiones_comunas.items():
            # Crear o obtener región
            region, created = Region.objects.get_or_create(
                codigo=codigo,
                defaults={
                    'nombre': data['nombre'],
                    'numero_romano': data['numero_romano']
                }
            )

            if created:
                regiones_creadas += 1
                self.stdout.write(f'  ✅ Región creada: {region.nombre}')
            else:
                regiones_existentes += 1
                self.stdout.write(f'  ℹ️  Región ya existe: {region.nombre}')

            # Crear comunas para esta región
            for nombre_comuna in data['comunas']:
                comuna, created = Comuna.objects.get_or_create(
                    region=region,
                    nombre=nombre_comuna
                )

                if created:
                    comunas_creadas += 1
                else:
                    comunas_existentes += 1

        # Resumen
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('✅ Carga completada exitosamente!\n'))
        self.stdout.write(f'📊 Resumen:')
        self.stdout.write(f'   • Regiones creadas: {regiones_creadas}')
        self.stdout.write(f'   • Regiones existentes: {regiones_existentes}')
        self.stdout.write(f'   • Comunas creadas: {comunas_creadas}')
        self.stdout.write(f'   • Comunas existentes: {comunas_existentes}')
        self.stdout.write(f'   • Total regiones: {Region.objects.count()}')
        self.stdout.write(f'   • Total comunas: {Comuna.objects.count()}')
        self.stdout.write('='*60)
