/**
 * Módulo de Geolocalización para Mi Condominio
 * Permite obtener la ubicación actual del dispositivo y convertirla en dirección
 */

class GeolocationManager {
    constructor() {
        this.btnObtenerUbicacion = null;
        this.inputLatitud = null;
        this.inputLongitud = null;
        this.inputDireccion = null;
        this.ubicacionStatus = null;
    }

    /**
     * Inicializa el gestor de geolocalización
     */
    init() {
        // Obtener elementos del DOM
        this.btnObtenerUbicacion = document.getElementById('btnObtenerUbicacion');
        this.inputLatitud = document.getElementById('ubicacion_latitud');
        this.inputLongitud = document.getElementById('ubicacion_longitud');
        this.inputDireccion = document.getElementById('direccion_incidencia');
        this.ubicacionStatus = document.getElementById('ubicacionStatus');

        // Verificar que existan los elementos necesarios
        if (!this.btnObtenerUbicacion) {
            console.warn('GeolocationManager: Botón de geolocalización no encontrado');
            return;
        }

        // Registrar evento del botón
        this.btnObtenerUbicacion.addEventListener('click', () => this.obtenerUbicacion());
    }

    /**
     * Obtiene la ubicación actual del dispositivo
     */
    obtenerUbicacion() {
        // Verificar si el navegador soporta geolocalización
        if (!navigator.geolocation) {
            this.mostrarError('Tu navegador no soporta geolocalización');
            return;
        }

        // Mostrar mensaje de carga
        this.mostrarEstado('Obteniendo ubicación...', 'info', 'hourglass-split');
        this.btnObtenerUbicacion.disabled = true;

        // Opciones para obtener ubicación
        const options = {
            enableHighAccuracy: true, // Usar GPS si está disponible (mayor precisión)
            timeout: 10000, // Timeout de 10 segundos
            maximumAge: 0 // No usar ubicación en caché (siempre obtener nueva)
        };

        // Obtener ubicación actual
        navigator.geolocation.getCurrentPosition(
            (position) => this.onUbicacionExito(position),
            (error) => this.onUbicacionError(error),
            options
        );
    }

    /**
     * Callback cuando se obtiene la ubicación exitosamente
     * @param {GeolocationPosition} position - Objeto con la ubicación
     */
    onUbicacionExito(position) {
        // Extraer coordenadas con 6 decimales de precisión (~11cm)
        const latitud = position.coords.latitude.toFixed(6);
        const longitud = position.coords.longitude.toFixed(6);
        const precision = position.coords.accuracy.toFixed(0);

        // Actualizar campos de coordenadas
        this.inputLatitud.value = latitud;
        this.inputLongitud.value = longitud;

        // Mostrar mensaje de éxito
        this.mostrarEstado(
            `Ubicación obtenida (precisión: ${precision}m)`,
            'success',
            'check-circle'
        );

        // Habilitar botón nuevamente
        this.btnObtenerUbicacion.disabled = false;

        // Intentar obtener dirección mediante reverse geocoding
        this.obtenerDireccion(latitud, longitud);
    }

    /**
     * Callback cuando hay un error al obtener la ubicación
     * @param {GeolocationPositionError} error - Objeto con el error
     */
    onUbicacionError(error) {
        let mensajeError = '';

        switch(error.code) {
            case error.PERMISSION_DENIED:
                mensajeError = 'Permiso denegado. Por favor, permite el acceso a tu ubicación.';
                break;
            case error.POSITION_UNAVAILABLE:
                mensajeError = 'Información de ubicación no disponible.';
                break;
            case error.TIMEOUT:
                mensajeError = 'Tiempo de espera agotado al obtener la ubicación.';
                break;
            default:
                mensajeError = 'Error desconocido al obtener la ubicación.';
        }

        this.mostrarError(mensajeError);
        this.btnObtenerUbicacion.disabled = false;
    }

    /**
     * Obtiene la dirección mediante reverse geocoding usando Nominatim (OpenStreetMap)
     * @param {string} lat - Latitud
     * @param {string} lon - Longitud
     */
    obtenerDireccion(lat, lon) {
        // URL del servicio de Nominatim (OpenStreetMap) - Gratuito
        const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}&zoom=18&addressdetails=1`;

        // Realizar petición
        fetch(url, {
            headers: {
                'User-Agent': 'MiCondominio/1.0' // Nominatim requiere User-Agent
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data && data.display_name) {
                // Si el campo de dirección está vacío, llenarlo automáticamente
                if (!this.inputDireccion.value) {
                    this.inputDireccion.value = data.display_name;
                }

                // Agregar mensaje de éxito
                this.agregarEstado('Dirección obtenida', 'success', 'house-check');
            }
        })
        .catch(error => {
            console.warn('No se pudo obtener la dirección:', error);
            // No mostramos error al usuario ya que la dirección es opcional
        });
    }

    /**
     * Muestra un mensaje de estado
     * @param {string} mensaje - Mensaje a mostrar
     * @param {string} tipo - Tipo de mensaje (info, success, danger, warning)
     * @param {string} icono - Icono de Bootstrap Icons
     */
    mostrarEstado(mensaje, tipo, icono) {
        if (!this.ubicacionStatus) return;

        const iconoHTML = icono ? `<i class="bi bi-${icono} me-1"></i>` : '';
        this.ubicacionStatus.innerHTML = `<span class="text-${tipo}">${iconoHTML}${mensaje}</span>`;
    }

    /**
     * Agrega un mensaje adicional al estado actual
     * @param {string} mensaje - Mensaje a agregar
     * @param {string} tipo - Tipo de mensaje (info, success, danger, warning)
     * @param {string} icono - Icono de Bootstrap Icons
     */
    agregarEstado(mensaje, tipo, icono) {
        if (!this.ubicacionStatus) return;

        const iconoHTML = icono ? `<i class="bi bi-${icono} me-1"></i>` : '';
        this.ubicacionStatus.innerHTML += ` <span class="text-${tipo}">${iconoHTML}${mensaje}</span>`;
    }

    /**
     * Muestra un mensaje de error
     * @param {string} mensaje - Mensaje de error
     */
    mostrarError(mensaje) {
        this.mostrarEstado(mensaje, 'danger', 'x-circle');
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    const geoManager = new GeolocationManager();
    geoManager.init();
});
