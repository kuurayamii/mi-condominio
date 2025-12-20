/**
 * Asistente de IA - Gestión del chat
 * Maneja la interfaz de chat, envío de mensajes, y comunicación con el backend
 */

class AIChatManager {
    constructor() {
        this.chatMessages = document.getElementById('chatMessages');
        this.chatInput = document.getElementById('chatInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.clearChatBtn = document.getElementById('clearChatBtn');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.emptyState = document.getElementById('emptyState');

        this.apiUrls = {
            send: this.chatMessages.dataset.sendUrl,
            history: this.chatMessages.dataset.historyUrl,
            clear: this.chatMessages.dataset.clearUrl,
            confirm: '/ai-chat/confirm/'
        };
    }

    init() {
        this.setupMarked();
        this.setupEventListeners();
        this.loadHistory();
    }

    setupMarked() {
        // Configurar marked para renderizar markdown
        if (typeof marked !== 'undefined') {
            marked.setOptions({
                breaks: true,
                gfm: true
            });
        }
    }

    setupEventListeners() {
        // Send button
        this.sendBtn.addEventListener('click', () => this.sendMessage());

        // Enter key to send (Shift+Enter for new line)
        this.chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Clear chat button
        this.clearChatBtn.addEventListener('click', () => this.clearChat());

        // Suggested questions
        document.querySelectorAll('.suggested-question').forEach(btn => {
            btn.addEventListener('click', () => {
                const question = btn.getAttribute('data-question');
                this.chatInput.value = question;
                this.sendMessage();
            });
        });

        // Auto-resize textarea
        this.chatInput.addEventListener('input', () => {
            this.chatInput.style.height = 'auto';
            this.chatInput.style.height = this.chatInput.scrollHeight + 'px';
        });
    }

    async sendMessage() {
        const mensaje = this.chatInput.value.trim();

        if (!mensaje) return;

        // Hide empty state
        this.emptyState.style.display = 'none';

        // Add user message to UI
        this.addMessageToUI('user', mensaje);

        // Clear input
        this.chatInput.value = '';
        this.chatInput.style.height = 'auto';

        // Disable send button and show typing indicator
        this.sendBtn.disabled = true;
        this.typingIndicator.classList.add('show');
        this.scrollToBottom();

        try {
            const response = await fetch(this.apiUrls.send, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: JSON.stringify({ mensaje: mensaje })
            });

            const data = await response.json();

            // Hide typing indicator
            this.typingIndicator.classList.remove('show');

            if (data.exito) {
                // Add assistant message to UI
                this.addMessageToUI('assistant', data.respuesta, data.tool_calls);
            } else {
                alert('Error: ' + (data.error || 'Error desconocido'));
            }
        } catch (error) {
            this.typingIndicator.classList.remove('show');
            alert('Error de conexión: ' + error.message);
        } finally {
            this.sendBtn.disabled = false;
            this.chatInput.focus();
        }
    }

    addMessageToUI(role, content, toolCalls = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;

        const avatarIcon = role === 'user' ? 'bi-person-fill' : 'bi-robot';

        // Render markdown content
        const renderedContent = typeof marked !== 'undefined'
            ? marked.parse(content)
            : content.replace(/\n/g, '<br>');

        let toolCallsHTML = '';
        if (toolCalls && toolCalls.length > 0) {
            toolCallsHTML = `<div class="tool-calls-badge">
                <i class="bi bi-tools me-1"></i>
                ${toolCalls.length} herramienta${toolCalls.length > 1 ? 's' : ''} usada${toolCalls.length > 1 ? 's' : ''}
            </div>`;
        }

        messageDiv.innerHTML = `
            ${role === 'user' ? '' : `<div class="message-avatar"><i class="bi ${avatarIcon}"></i></div>`}
            <div class="message-content">
                ${renderedContent}
                ${toolCallsHTML}
            </div>
            ${role === 'user' ? `<div class="message-avatar"><i class="bi ${avatarIcon}"></i></div>` : ''}
        `;

        this.chatMessages.insertBefore(messageDiv, this.typingIndicator);
        this.scrollToBottom();
    }

    async loadHistory() {
        try {
            const response = await fetch(this.apiUrls.history);
            const data = await response.json();

            if (data.exito && data.messages && data.messages.length > 0) {
                // Hide empty state
                this.emptyState.style.display = 'none';

                // Add messages to UI
                data.messages.forEach(msg => {
                    if (msg.role !== 'system') {
                        this.addMessageToUI(msg.role, msg.contenido);
                    }
                });
            }
        } catch (error) {
            console.error('Error loading history:', error);
        }
    }

    async clearChat() {
        if (!confirm('¿Estás seguro de que quieres comenzar una nueva conversación? El historial actual se archivará.')) {
            return;
        }

        try {
            const response = await fetch(this.apiUrls.clear, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                }
            });

            const data = await response.json();

            if (data.exito) {
                // Clear messages
                const messages = this.chatMessages.querySelectorAll('.message');
                messages.forEach(msg => msg.remove());

                // Show empty state
                this.emptyState.style.display = 'block';

                alert('Nueva conversación iniciada');
            }
        } catch (error) {
            alert('Error al limpiar el chat: ' + error.message);
        }
    }

    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    showConfirmationModal(propuesta) {
        // Crear el modal dinámicamente
        const modalId = 'confirmActionModal';

        // Remover modal anterior si existe
        const existingModal = document.getElementById(modalId);
        if (existingModal) {
            existingModal.remove();
        }

        // Generar tabla con los datos
        const dataTableHTML = this.generateDataTable(propuesta.datos, propuesta.tipo_registro);

        // Crear el HTML del modal
        const modalHTML = `
            <div class="modal fade" id="${modalId}" tabindex="-1" aria-labelledby="${modalId}Label" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="${modalId}Label">
                                <i class="bi bi-exclamation-circle text-warning me-2"></i>
                                Confirmación Requerida
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <p class="mb-3">${this.escapeHtml(propuesta.mensaje_confirmacion)}</p>
                            <div class="data-preview">
                                <h6 class="mb-2">Datos a registrar:</h6>
                                ${dataTableHTML}
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                <i class="bi bi-x-circle me-2"></i>Cancelar
                            </button>
                            <button type="button" class="btn btn-primary" id="confirmActionBtn">
                                <i class="bi bi-check-circle me-2"></i>Confirmar
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Agregar modal al DOM
        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // Obtener referencia al modal
        const modalElement = document.getElementById(modalId);
        const modal = new bootstrap.Modal(modalElement);

        // Event listener para el botón de confirmar
        const confirmBtn = document.getElementById('confirmActionBtn');
        confirmBtn.addEventListener('click', async () => {
            confirmBtn.disabled = true;
            confirmBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Procesando...';

            try {
                await this.confirmAction(propuesta.accion, propuesta.datos);
                modal.hide();
            } catch (error) {
                alert('Error al confirmar la acción: ' + error.message);
                confirmBtn.disabled = false;
                confirmBtn.innerHTML = '<i class="bi bi-check-circle me-2"></i>Confirmar';
            }
        });

        // Event listener para cuando se cierra el modal sin confirmar
        modalElement.addEventListener('hidden.bs.modal', () => {
            // Si se cancela, agregar mensaje al chat
            if (!confirmBtn.disabled || confirmBtn.textContent.includes('Confirmar')) {
                this.addMessageToUI('assistant', '❌ Acción cancelada por el usuario.');
            }
            modalElement.remove();
        });

        // Mostrar el modal
        modal.show();
    }

    generateDataTable(datos, tipoRegistro) {
        const labelMap = {
            // Condominio
            'nombre': 'Nombre',
            'rut': 'RUT',
            'direccion': 'Dirección',
            'comuna': 'Comuna',
            'region': 'Región',
            'mail_contacto': 'Email de Contacto',
            'telefono': 'Teléfono',

            // Usuario
            'nombres': 'Nombres',
            'apellido': 'Apellido',
            'correo': 'Correo',
            'tipo': 'Tipo de Usuario',
            'condominio_id': 'Condominio',

            // Reunión
            'tema': 'Tema',
            'fecha': 'Fecha',
            'hora': 'Hora',
            'ubicacion': 'Ubicación',
            'descripcion': 'Descripción',
            'estado': 'Estado',

            // Incidencia
            'titulo': 'Título',
            'prioridad': 'Prioridad',
            'tipo_incidencia_id': 'Categoría',
            'usuario_reporta_id': 'Usuario que Reporta',
            'latitud': 'Latitud',
            'longitud': 'Longitud',
            'direccion_incidencia': 'Dirección',

            // Amonestación
            'motivo': 'Motivo',
            'tipo_amonestacion': 'Tipo',
            'usuario_id': 'Usuario',
            'detalle': 'Detalle'
        };

        let tableHTML = '<table class="table table-bordered table-sm data-preview-table">';

        for (const [key, value] of Object.entries(datos)) {
            // Omitir valores null o undefined
            if (value === null || value === undefined) continue;

            const label = labelMap[key] || key;
            tableHTML += `
                <tr>
                    <th style="width: 35%;">${label}</th>
                    <td>${this.formatValue(value)}</td>
                </tr>
            `;
        }

        tableHTML += '</table>';
        return tableHTML;
    }

    formatValue(value) {
        if (value === null || value === undefined || value === '') {
            return '<em class="text-muted">No especificado</em>';
        }
        return this.escapeHtml(String(value));
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    async confirmAction(accion, datos) {
        try {
            const response = await fetch(this.apiUrls.confirm, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: JSON.stringify({
                    accion: accion,
                    datos: datos
                })
            });

            const result = await response.json();

            if (result.exito) {
                this.addMessageToUI('assistant', `✓ ${result.mensaje}`);
            } else {
                this.addMessageToUI('assistant', `✗ Error: ${result.error}`);
            }
        } catch (error) {
            this.addMessageToUI('assistant', `✗ Error de conexión: ${error.message}`);
            throw error;
        }
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    const chatManager = new AIChatManager();
    chatManager.init();
});
