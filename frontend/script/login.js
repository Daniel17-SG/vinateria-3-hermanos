// login.js (Crea este archivo en tu carpeta de scripts)

document.addEventListener('DOMContentLoaded', () => {
    // 1. Obtener los elementos del DOM (Inputs y Formulario)
    const form = document.getElementById('login-form');
    const emailInput = document.getElementById('email-input');
    const passwordInput = document.getElementById('password-input');
    const errorMessage = document.getElementById('login-error-message');

    if (!form) return; // Salir si el formulario no se encuentra

    // 2. Agregar el listener para el envío del formulario
    form.addEventListener('submit', async (event) => {
        event.preventDefault(); 
        
        errorMessage.style.display = 'none';

        const email = emailInput.value;
        const password = passwordInput.value;

        try {
            // 3. Llamada al API del Back-End (ruta /login)
            const response = await fetch('/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password }),
            });

            const data = await response.json();

            // 4. Manejo de la respuesta
            if (data.success) {
                // Redirecciona a la página que indique el servidor (admi.html o index.html)
                window.location.href = data.redirect; 
            } else {
                // Muestra el mensaje de error del servidor
                errorMessage.textContent = data.message;
                errorMessage.style.display = 'block';
            }
        } catch (error) {
            console.error('Error de conexión:', error);
            errorMessage.textContent = 'Error al conectar con el servidor. ¿Está corriendo?';
            errorMessage.style.display = 'block';
        }
    });
});