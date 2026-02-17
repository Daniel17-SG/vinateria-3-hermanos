document.addEventListener('DOMContentLoaded', async () => {
    const gridProductos = document.querySelector('.grid-productos');
    const buttons = document.querySelectorAll('.filtro-btn');
    const notification = document.getElementById('notification-toast');

    // Función para renderizar productos
    const renderProducts = (products) => {
        gridProductos.innerHTML = ''; // Limpiar grilla

        if (products.length === 0) {
            gridProductos.innerHTML = '<p>No hay productos disponibles en este momento.</p>';
            return;
        }

        products.forEach(product => {
            // Mapear categoría a imagen (simple, para demo)
            let imgSrc = 'imagenes/vino.jpg'; // Default
            const cat = product.category.toLowerCase();
            if (cat.includes('tequila')) imgSrc = 'imagenes/tequila.jpg';
            else if (cat.includes('whisky')) imgSrc = 'imagenes/whiski.jpg';
            else if (cat.includes('brandy')) imgSrc = 'imagenes/brandy.jpg';
            else if (cat.includes('vodka')) imgSrc = 'imagenes/vodka.jpg';
            else if (cat.includes('ron')) imgSrc = 'imagenes/ron.png';

            // Crear elemento
            const productCard = document.createElement('div');
            productCard.classList.add('producto');
            productCard.setAttribute('data-category', cat); // Para filtrado

            productCard.innerHTML = `
                <img src="${imgSrc}" alt="${product.name}">
                <h3>${product.name}</h3>
                <p class="desc">${product.category} - ${product.status}</p>
                <p class="precio">$${product.price}</p>
                <button class="agregar-carrito" data-id="${product.id}">Agregar al Carrito</button>
            `;

            gridProductos.appendChild(productCard);
        });

        // Re-asignar listeners a botones de "Agregar al Carrito"
        attachCartListeners();
    };

    // Función para conectar listeners de carrito
    const attachCartListeners = () => {
        const agregarCarritoButtons = document.querySelectorAll('.agregar-carrito');
        agregarCarritoButtons.forEach(button => {
            button.addEventListener('click', () => {
                // Notificación visual
                notification.classList.remove('notification-hidden');
                notification.classList.add('notification-show');

                setTimeout(() => {
                    notification.classList.remove('notification-show');
                    notification.classList.add('notification-hidden');
                }, 3000);

                const originalText = button.textContent;
                button.textContent = "¡Agregado!";
                button.disabled = true;

                setTimeout(() => {
                    button.textContent = originalText;
                    button.disabled = false;
                }, 1500);
            });
        });
    };

    // Cargar productos desde API
    try {
        const response = await fetch('/api/inventory');
        const products = await response.json();

        // Guardar todos los productos para filtrar localmente
        window.allProducts = products;

        renderProducts(products);
    } catch (error) {
        console.error('Error al cargar catálogo:', error);
        gridProductos.innerHTML = '<p>Error al cargar el catálogo.</p>';
    }

    // Lógica de Filtrado
    buttons.forEach(button => {
        button.addEventListener('click', () => {
            buttons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');

            const filterValue = button.getAttribute('data-filter').toLowerCase();

            if (!window.allProducts) return;

            let filtered;
            if (filterValue === 'all') {
                filtered = window.allProducts;
            } else {
                filtered = window.allProducts.filter(p => p.category.toLowerCase().includes(filterValue));
            }

            renderProducts(filtered);
        });
    });
});
