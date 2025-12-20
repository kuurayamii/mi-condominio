"""
Modelos de la aplicación Mi Condominio.

Este paquete contiene todos los modelos de la aplicación organizados
en módulos separados para mejor mantenibilidad.
"""

# Importar modelos base
from .condominio import Condominio
from .usuario import Usuario
from .reunion import Reunion

# Importar modelos de incidencias
from .incidencia import CategoriaIncidencia, Incidencia
from .bitacora import Bitacora
from .evidencia import EvidenciaIncidencia, evidencia_upload_path

# Importar modelo de amonestaciones
from .amonestacion import Amonestacion

# Importar modelos de chat (Asistente IA)
from .chat import ChatSession, ChatMessage


# Definir qué se exporta cuando se hace "from mi_condominio.models import *"
__all__ = [
    # Modelos base
    'Condominio',
    'Usuario',
    'Reunion',

    # Modelos de incidencias
    'CategoriaIncidencia',
    'Incidencia',
    'Bitacora',
    'EvidenciaIncidencia',
    'evidencia_upload_path',

    # Modelo de amonestaciones
    'Amonestacion',

    # Modelos de chat
    'ChatSession',
    'ChatMessage',
]
