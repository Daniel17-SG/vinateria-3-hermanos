// login.js - Autenticación simulada (cliente-side)
// Funciona sin backend, ideal para despliegue estático en Vercel

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('loginForm');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const errorMessage = document.getElementById('error-message');

    if (!form) return;

    // Credenciales simuladas
    const USERS = [
        { email: 'admin@3hermanos.com', password: 'admin123', role: 'admin', name: 'Admin' },
        { email: 'daniel@gmail.com', password: '1234', role: 'admin', name: 'Daniel' },
        { email: 'cliente@gmail.com', password: '1234', role: 'user', name: 'Cliente' }
    ];

    form.addEventListener('submit', (event) => {
        event.preventDefault();
        errorMessage.style.display = 'none';

        const email = emailInput.value.trim().toLowerCase();
        const password = passwordInput.value;

        // Buscar usuario
        const user = USERS.find(u => u.email === email && u.password === password);

        if (user) {
            // Guardar sesión en LocalStorage
            localStorage.setItem('user', JSON.stringify({
                email: user.email,
                role: user.role,
                name: user.name
            }));

            // Redirigir según el rol
            if (user.role === 'admin') {
                window.location.href = 'admi.html';
            } else {
                window.location.href = 'index.html';
            }
        } else {
            errorMessage.textContent = 'Correo o contraseña incorrectos.';
            errorMessage.style.display = 'block';
        }
    });
});