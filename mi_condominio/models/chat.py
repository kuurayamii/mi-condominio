"""
Modelos para el Asistente de IA.

Este módulo contiene los modelos ChatSession y ChatMessage que gestionan
las conversaciones del asistente de IA con los usuarios.
"""

from django.db import models
from .usuario import Usuario


class ChatSession(models.Model):
    """
    Sesión de chat con el asistente de IA.
    Cada sesión mantiene el contexto de la conversación.
    """
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='chat_sessions')
    titulo = models.CharField(max_length=255, blank=True, null=True, help_text="Título opcional para la sesión")
    activa = models.BooleanField(default=True, help_text="Indica si la sesión está activa")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'chat_sessions'
        verbose_name = 'Sesión de Chat'
        verbose_name_plural = 'Sesiones de Chat'
        ordering = ['-updated_at']

    def __str__(self):
        return f"Sesión {self.id} - {self.usuario.nombres} ({self.created_at.strftime('%d/%m/%Y %H:%M')})"


class ChatMessage(models.Model):
    """
    Mensaje individual en una sesión de chat.
    Puede ser del usuario o del asistente de IA.
    """
    ROLE_CHOICES = [
        ('user', 'Usuario'),
        ('assistant', 'Asistente'),
        ('system', 'Sistema'),
    ]

    sesion = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    contenido = models.TextField(help_text="Contenido del mensaje")

    # Metadata para análisis y auditoría
    tokens_usados = models.IntegerField(null=True, blank=True, help_text="Tokens consumidos en esta respuesta")
    tool_calls = models.JSONField(null=True, blank=True, help_text="Llamadas a herramientas MCP realizadas")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_messages'
        verbose_name = 'Mensaje de Chat'
        verbose_name_plural = 'Mensajes de Chat'
        ordering = ['created_at']

    def __str__(self):
        preview = self.contenido[:50] + "..." if len(self.contenido) > 50 else self.contenido
        return f"{self.get_role_display()}: {preview}"
