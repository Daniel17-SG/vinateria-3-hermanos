document.addEventListener('DOMContentLoaded', () => {
    // Referencias a elementos del DOM
    const cartItemsContainer = document.getElementById('cart-items-container');
    const subtotalElement = document.getElementById('cart-subtotal');
    const totalElement = document.getElementById('cart-total');

    // Función para actualizar el total
    function updateCartTotal() {
        let total = 0;
        const cartItems = document.querySelectorAll('.carrito-item');

        cartItems.forEach(item => {
            const price = parseFloat(item.getAttribute('data-price'));
            const quantityInput = item.querySelector('.qty-input');
            const quantity = parseInt(quantityInput.value);

            if (!isNaN(price) && !isNaN(quantity)) {
                total += price * quantity;
            }
        });

        // Formatear moneda
        const formattedTotal = '$' + total.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');

        // Actualizar DOM
        subtotalElement.textContent = formattedTotal;
        totalElement.textContent = formattedTotal + ' MXN';
    }

    // Event Delegation para manejar clicks (eliminar) y cambios (cantidad)
    cartItemsContainer.addEventListener('click', (event) => {
        // Manejar botón de eliminar
        if (event.target.closest('.btn-remove')) {
            const item = event.target.closest('.carrito-item');
            if (confirm('¿Estás seguro de eliminar este producto del carrito?')) {
                item.remove();
                updateCartTotal();
            }
        }
    });

    cartItemsContainer.addEventListener('input', (event) => {
        // Manejar cambio en input de cantidad
        if (event.target.classList.contains('qty-input')) {
            const input = event.target;
            if (input.value < 1) {
                input.value = 1; // Mínimo 1
            }
            updateCartTotal();
        }
    });

    // Calcular total inicial
    updateCartTotal();
});

// Función global para verificar sesión desde el botón de pago
function verificarSesion() {
    const user = localStorage.getItem('user');

    if (!user) {
        // Si NO hay usuario guardado, pedimos iniciar sesión
        const confirmacion = confirm("✋ ¡Alto ahí! Debes iniciar sesión para proceder al pago.");

        if (confirmacion) {
            window.location.href = "login.html";
        }
    } else {
        // Si SÍ hay usuario, procedemos
        window.location.href = "pago.html";
    }
}
