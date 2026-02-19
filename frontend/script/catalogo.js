// catalogo.js - Catálogo con productos locales y carrito con localStorage

document.addEventListener('DOMContentLoaded', () => {
    const gridProductos = document.querySelector('.grid-productos');
    const buttons = document.querySelectorAll('.filtro-btn');
    const notification = document.getElementById('notification-toast');
    const badge = document.getElementById('cart-badge');

    // Productos locales (sin depender de backend)
    const PRODUCTS = [
        { id: 1, name: 'Tequila Maestro Dobel Diamante', category: 'Tequila', price: 1250, status: 'Disponible', img: 'imagenes/tequila.jpg', tag: '20% OFF' },
        { id: 2, name: 'Tequila Don Julio 70', category: 'Tequila', price: 980, status: 'Disponible', img: 'imagenes/tequila.jpg' },
        { id: 3, name: 'Tequila José Cuervo Reserva', category: 'Tequila', price: 750, status: 'Disponible', img: 'imagenes/tequila.jpg', tag: 'Nuevo' },
        { id: 4, name: 'Whisky Buchanans 18', category: 'Whisky', price: 1950, status: 'Disponible', img: 'imagenes/18.jpg' },
        { id: 5, name: 'Whisky Blue Label Escocés', category: 'Whisky', price: 4850, status: 'Disponible', img: 'imagenes/whiski.jpg', tag: 'Mejor venta' },
        { id: 6, name: 'Whisky Jack Daniels', category: 'Whisky', price: 620, status: 'Disponible', img: 'imagenes/whiski.jpg' },
        { id: 7, name: 'Brandy Torres 10', category: 'Brandy', price: 450, status: 'Disponible', img: 'imagenes/brandy.jpg' },
        { id: 8, name: 'Brandy Don Pedro', category: 'Brandy', price: 280, status: 'Disponible', img: 'imagenes/brandy.jpg' },
        { id: 9, name: 'Vodka Absolut Original', category: 'Vodka', price: 650, status: 'Disponible', img: 'imagenes/vodka.jpg' },
        { id: 10, name: 'Vodka Grey Goose', category: 'Vodka', price: 890, status: 'Disponible', img: 'imagenes/vodka.jpg' },
        { id: 11, name: 'Ron Matusalem Gran Reserva', category: 'Ron', price: 520, status: 'Disponible', img: 'imagenes/ron.png' },
        { id: 12, name: 'Ron Bacardí Añejo', category: 'Ron', price: 380, status: 'Disponible', img: 'imagenes/ron.png' }
    ];

    // ---------- FUNCIONES DEL CARRITO (localStorage) ----------

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
        if (badge) {
            badge.textContent = total;
            badge.style.display = total > 0 ? 'inline-flex' : 'none';
        }
    }

    function addToCart(product) {
        const cart = getCart();
        const existing = cart.find(item => item.id === product.id);

        if (existing) {
            existing.quantity += 1;
        } else {
            cart.push({
                id: product.id,
                name: product.name,
                price: product.price,
                img: product.img,
                quantity: 1
            });
        }

        saveCart(cart);
    }

    // ---------- RENDERIZADO DE PRODUCTOS ----------

    const renderProducts = (products) => {
        gridProductos.innerHTML = '';

        if (products.length === 0) {
            gridProductos.innerHTML = '<p>No hay productos disponibles en esta categoría.</p>';
            return;
        }

        products.forEach(product => {
            const productCard = document.createElement('div');
            productCard.classList.add('producto');
            productCard.setAttribute('data-category', product.category.toLowerCase());

            const tagHtml = product.tag ? `<span class="product-tag">${product.tag}</span>` : '';

            productCard.innerHTML = `
                ${tagHtml}
                <img src="${product.img}" alt="${product.name}">
                <h3>${product.name}</h3>
                <p class="desc">${product.category} - ${product.status}</p>
                <p class="precio">$${product.price.toLocaleString('es-MX')}</p>
                <button class="agregar-carrito" data-id="${product.id}">Agregar al Carrito</button>
                <i class="fas fa-shopping-cart hover-cart"></i>
            `;

            gridProductos.appendChild(productCard);
        });

        attachCartListeners();
        observeProducts();
        attachModalListeners();
    };

    // ---------- LISTENERS DE CARRITO ----------

    const attachCartListeners = () => {
        const agregarCarritoButtons = document.querySelectorAll('.agregar-carrito');
        agregarCarritoButtons.forEach(button => {
            button.addEventListener('click', () => {
                const productId = parseInt(button.getAttribute('data-id'));
                const product = PRODUCTS.find(p => p.id === productId);

                if (product) {
                    addToCart(product);

                    // Notificación visual
                    if (notification) {
                        notification.classList.remove('notification-hidden');
                        notification.classList.add('notification-show');
                        setTimeout(() => {
                            notification.classList.remove('notification-show');
                            notification.classList.add('notification-hidden');
                        }, 3000);
                    }

                    button.textContent = "¡Agregado!";
                    button.disabled = true;
                    setTimeout(() => {
                        button.textContent = "Agregar al Carrito";
                        button.disabled = false;
                    }, 1500);
                }
            });
        });
    };

    // Renderizar todos los productos al inicio
    renderProducts(PRODUCTS);
    updateBadge();

    // OBSERVER PARA ANIMACIÓN DE ENTRADA
    function observeProducts() {
        const items = document.querySelectorAll('.producto');
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        items.forEach(el => observer.observe(el));
    }

    // MODAL DETALLE
    function createModal() {
        let modal = document.getElementById('product-modal');
        if (modal) return modal;
        modal = document.createElement('div');
        modal.id = 'product-modal';
        modal.className = 'modal-overlay';
        modal.style.display = 'none';
        modal.innerHTML = `
            <div class="modal-content">
                <span class="modal-close">&times;</span>
                <img src="" alt="" id="modal-img">
                <h2 id="modal-title"></h2>
                <p id="modal-category"></p>
                <p id="modal-price" class="precio"></p>
                <p id="modal-status"></p>
                <button id="modal-add" class="agregar-carrito">Agregar al Carrito</button>
            </div>
        `;
        document.body.appendChild(modal);
        return modal;
    }

    function showProductModal(product) {
        const modal = createModal();
        modal.querySelector('#modal-img').src = product.img;
        modal.querySelector('#modal-title').textContent = product.name;
        modal.querySelector('#modal-category').textContent = product.category;
        modal.querySelector('#modal-price').textContent = `$${product.price.toLocaleString('es-MX')}`;
        modal.querySelector('#modal-status').textContent = product.status;
        const addBtn = modal.querySelector('#modal-add');
        addBtn.onclick = () => {
            addToCart(product);
            modal.style.display = 'none';
        };
        modal.style.display = 'flex';
    }

    function attachModalListeners() {
        document.querySelectorAll('.producto').forEach(el => {
            el.addEventListener('click', (e) => {
                // ignore click on add-to-cart button
                if (e.target.closest('.agregar-carrito')) return;
                const id = parseInt(el.querySelector('.agregar-carrito').getAttribute('data-id'));
                const product = PRODUCTS.find(p => p.id === id);
                if (product) showProductModal(product);
            });
        });
        // close when clicking outside content or on close
        document.body.addEventListener('click', (e) => {
            const modal = document.getElementById('product-modal');
            if (modal && e.target === modal || e.target.classList.contains('modal-close')) {
                modal.style.display = 'none';
            }
        });
    }

    // ---------- FILTRADO ----------

    // Leer el parámetro de categoría de la URL
    const urlParams = new URLSearchParams(window.location.search);
    const categoryParam = urlParams.get('categoria');

    if (categoryParam) {
        const filtered = PRODUCTS.filter(p => p.category.toLowerCase().includes(categoryParam.toLowerCase()));
        renderProducts(filtered);

        // Marcar el botón activo
        buttons.forEach(btn => {
            btn.classList.remove('active');
            if (btn.getAttribute('data-filter') === categoryParam.toLowerCase()) {
                btn.classList.add('active');
            }
        });
    }

    buttons.forEach(button => {
        button.addEventListener('click', () => {
            buttons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');

            const filterValue = button.getAttribute('data-filter').toLowerCase();

            if (filterValue === 'all') {
                renderProducts(PRODUCTS);
            } else {
                const filtered = PRODUCTS.filter(p => p.category.toLowerCase().includes(filterValue));
                renderProducts(filtered);
            }
        });
    });
});
