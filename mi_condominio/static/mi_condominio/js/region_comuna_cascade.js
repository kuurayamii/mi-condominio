/**
 * Gestión de selección en cascada: Región → Comuna
 *
 * Este script maneja la dependencia entre los selectores de región y comuna,
 * cargando dinámicamente las comunas según la región seleccionada.
 */

class RegionComunaCascade {
    constructor(regionSelectId = 'id_region', comunaSelectId = 'id_comuna') {
        this.regionSelect = document.getElementById(regionSelectId);
        this.comunaSelect = document.getElementById(comunaSelectId);

        if (!this.regionSelect || !this.comunaSelect) {
            console.warn('No se encontraron los selectores de región o comuna');
            return;
        }

        this.comunaOriginalValue = this.comunaSelect.value; // Guardar valor original para modo edición
        this.init();
    }

    init() {
        // Configurar evento de cambio en región
        this.regionSelect.addEventListener('change', () => {
            this.loadComunas();
        });

        // Si hay una región seleccionada al cargar la página, cargar sus comunas
        if (this.regionSelect.value) {
            this.loadComunas(this.comunaOriginalValue);
        } else {
            // Si no hay región seleccionada, limpiar comunas
            this.clearComunas();
        }
    }

    async loadComunas(selectedComunaId = null) {
        const regionId = this.regionSelect.value;

        if (!regionId) {
            this.clearComunas();
            return;
        }

        try {
            // Mostrar indicador de carga
            this.comunaSelect.disabled = true;
            this.comunaSelect.innerHTML = '<option value="">Cargando comunas...</option>';

            // Hacer petición al API
            const response = await fetch(`/api/comunas/${regionId}/`);

            if (!response.ok) {
                throw new Error('Error al cargar las comunas');
            }

            const data = await response.json();

            // Limpiar select de comunas
            this.comunaSelect.innerHTML = '<option value="">Seleccione una comuna</option>';

            // Agregar opciones de comunas
            data.comunas.forEach(comuna => {
                const option = document.createElement('option');
                option.value = comuna.id;
                option.textContent = comuna.nombre;

                // Seleccionar la comuna original si estamos en modo edición
                if (selectedComunaId && comuna.id == selectedComunaId) {
                    option.selected = true;
                }

                this.comunaSelect.appendChild(option);
            });

            // Habilitar select
            this.comunaSelect.disabled = false;

            // Si no hay comunas, mostrar mensaje
            if (data.comunas.length === 0) {
                this.comunaSelect.innerHTML = '<option value="">No hay comunas disponibles</option>';
            }

        } catch (error) {
            console.error('Error al cargar comunas:', error);
            this.comunaSelect.innerHTML = '<option value="">Error al cargar comunas</option>';
            this.comunaSelect.disabled = false;
        }
    }

    clearComunas() {
        this.comunaSelect.innerHTML = '<option value="">Primero seleccione una región</option>';
        this.comunaSelect.disabled = true;
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    new RegionComunaCascade();
});
