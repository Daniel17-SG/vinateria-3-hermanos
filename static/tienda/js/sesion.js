// sesion.js - Gestión de estados de sesión para Django
(function() {
    'use strict';

    const PROFILE_DROPDOWN_ID = 'profile-dropdown';

    function attachDropdownEvents() {
        const trigger = document.getElementById('profile-trigger');
        const menu = document.getElementById('profile-menu');
        const dropdown = document.getElementById(PROFILE_DROPDOWN_ID);
        const editarBtn = document.getElementById('editar-datos');
        const cerrarBtn = document.getElementById('cerrar-sesion');

        if (!trigger || !menu) return;

        trigger.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            dropdown.classList.toggle('active');
            menu.classList.toggle('show');
        });

        document.addEventListener('click', function(e) {
            if (!dropdown.contains(e.target)) {
                dropdown.classList.remove('active');
                menu.classList.remove('show');
            }
        });

        document.addEventListener('touchstart', function(e) {
            if (!dropdown.contains(e.target)) {
                dropdown.classList.remove('active');
                menu.classList.remove('show');
            }
        });
    }

    // Función global para verificar sesión antes del checkout
    window.verificarSesionCheckout = function() {
        fetch('/api/verificar-sesion/')
            .then(response => response.json())
            .then(data => {
                if (!data.autenticado) {
                    const next = encodeURIComponent('/pago/');
                    window.location.href = `/login/?next=${next}`;
                } else {
                    window.location.href = '/pago/';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                window.location.href = '/login/';
            });
        return false;
    };

    // Inicializar eventos del dropdown si existe
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            const dropdown = document.getElementById(PROFILE_DROPDOWN_ID);
            if (dropdown && document.getElementById('profile-trigger')) {
                attachDropdownEvents();
            }
        });
    } else {
        const dropdown = document.getElementById(PROFILE_DROPDOWN_ID);
        if (dropdown && document.getElementById('profile-trigger')) {
            attachDropdownEvents();
        }
    }

})();
