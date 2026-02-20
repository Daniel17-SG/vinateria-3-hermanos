// carrito.js - Carrito dinámico con localStorage
// Maneja: renderizado, cantidades, eliminación, totales y persistencia

document.addEventListener('DOMContentLoaded', () => {
    const cartItemsContainer = document.getElementById('cart-items-container');
    const subtotalElement = document.getElementById('cart-subtotal');
    const totalElement = document.getElementById('cart-total');
    const cartCountBadge = document.getElementById('cart-count');

    // ---------- FUNCIONES DE LOCALSTORAGE ----------

    // Use shared cart utilities if available (cart-badge.js)
    function getCart() {
        if (window.cartUtils && typeof window.cartUtils.getCart === 'function') {
            return window.cartUtils.getCart();
        }
        return JSON.parse(localStorage.getItem('carrito')) || [];
    }

    function saveCart(cart) {
        if (window.cartUtils && typeof window.cartUtils.saveCart === 'function') {
            return window.cartUtils.saveCart(cart);
        }
        localStorage.setItem('carrito', JSON.stringify(cart));
        updateBadge();
    }

    function updateBadge() {
        const cart = getCart();
        const total = cart.reduce((sum, item) => sum + item.quantity, 0);
        const badge = document.getElementById('cart-badge');
        if (badge) {
            badge.textContent = total;
            badge.style.display = total > 0 ? 'inline-flex' : 'none';
        }
    }

    // ---------- FORMATEO DE MONEDA ----------

    function formatMoney(amount) {
        return '$' + amount.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
    }

    // ---------- RENDERIZADO DEL CARRITO ----------

    function renderCart() {
        const cart = getCart();
        cartItemsContainer.innerHTML = '';

        if (cart.length === 0) {
            cartItemsContainer.innerHTML = `
                <div class="carrito-vacio">
                    <i class="fas fa-shopping-cart" style="font-size: 3rem; color: #ccc; margin-bottom: 15px;"></i>
                    <h3>Tu carrito está vacío</h3>
                    <p>Agrega productos desde nuestro <a href="catalogo.html">catálogo</a></p>
                </div>
            `;
            updateTotals(0);
            return;
        }

        let total = 0;

        cart.forEach((item, index) => {
            const itemTotal = item.price * item.quantity;
            total += itemTotal;

            const article = document.createElement('article');
            article.classList.add('carrito-item');
            article.setAttribute('data-index', index);

            article.innerHTML = `
                <img src="${item.img}" alt="${item.name}" class="item-img">
                <div class="item-details">
                    <h3 class="item-name">${item.name}</h3>
                    <p class="item-price">${formatMoney(item.price)} MXN</p>
                    <div class="item-quantity">
                        <button class="qty-btn qty-minus" data-index="${index}">−</button>
                        <span class="qty-display">${item.quantity}</span>
                        <button class="qty-btn qty-plus" data-index="${index}">+</button>
                    </div>
                    <p class="item-subtotal">Subtotal: ${formatMoney(itemTotal)}</p>
                </div>
                <button class="btn-remove" data-index="${index}" title="Eliminar">
                    <i class="fas fa-trash-alt"></i>
                </button>
            `;

            cartItemsContainer.appendChild(article);
        });

        updateTotals(total);
    }

    // ---------- ACTUALIZAR TOTALES ----------

    function updateTotals(total) {
        const formatted = formatMoney(total);
        if (subtotalElement) subtotalElement.textContent = formatted;
        if (totalElement) totalElement.textContent = formatted + ' MXN';
    }

    // ---------- EVENT DELEGATION ----------

    cartItemsContainer.addEventListener('click', (event) => {
        const target = event.target;
        const cart = getCart();

        // Eliminar producto
        if (target.closest('.btn-remove')) {
            const index = parseInt(target.closest('.btn-remove').getAttribute('data-index'));
            if (confirm('¿Eliminar este producto del carrito?')) {
                cart.splice(index, 1);
                saveCart(cart);
                renderCart();
            }
        }

        // Aumentar cantidad
        if (target.closest('.qty-plus')) {
            const index = parseInt(target.closest('.qty-plus').getAttribute('data-index'));
            cart[index].quantity += 1;
            saveCart(cart);
            renderCart();
        }

        // Disminuir cantidad
        if (target.closest('.qty-minus')) {
            const index = parseInt(target.closest('.qty-minus').getAttribute('data-index'));
            if (cart[index].quantity > 1) {
                cart[index].quantity -= 1;
                saveCart(cart);
                renderCart();
            }
        }
    });

    // ---------- RENDER INICIAL ----------
    renderCart();
});

// Función global para verificar sesión desde el botón de pago
function verificarSesion() {
    const user = localStorage.getItem('user');

    if (!user) {
        alert("✋ ¡Espera! Para tu seguridad, debes iniciar sesión antes de realizar el pago.");
        window.location.href = "login.html";
    } else {
        window.location.href = "pago.html";
    }
}
