// registro.js (Crea este archivo)

document.addEventListener('DOMContentLoaded', () => {
    // 1. Obtener los elementos del DOM
    const form = document.getElementById('register-form');
    const nameInput = document.getElementById('name-input');
    const emailInput = document.getElementById('email-input');
    const passwordInput = document.getElementById('pass-input');
    const errorMessage = document.getElementById('register-error-message');

    if (!form) return; // Salir si el formulario no se encuentra

    // 2. Agregar el listener para el envío del formulario
    form.addEventListener('submit', async (event) => {
        event.preventDefault(); 
        
        errorMessage.style.display = 'none';
        
        const name = nameInput.value;
        const email = emailInput.value;
        const password = passwordInput.value;

        try {
            // 3. Llamada al API del Back-End (ruta /register)
            const response = await fetch('/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, password }),
            });

            const data = await response.json();

            // 4. Manejo de la respuesta
            if (data.success) {
                alert(data.message); // Muestra un mensaje de éxito
                window.location.href = data.redirect; // Redirige a login.html
            } else {
                // Muestra el mensaje de error del servidor (ej: usuario ya existe)
                errorMessage.textContent = data.message;
                errorMessage.style.display = 'block';
            }
        } catch (error) {
            console.error('Error de conexión:', error);
            errorMessage.textContent = 'Error al intentar registrarse. ¿Está corriendo el servidor?';
            errorMessage.style.display = 'block';
        }
    });
});