// inventario.js

document.addEventListener('DOMContentLoaded', () => { // <--- LÍNEA CLAVE: SIN 'async'
    const inventoryTableBody = document.getElementById('inventory-table-body');
    const addButton = document.querySelector('.btn-nuevo-producto');
    
    // Elementos del Modal
    const modal = document.getElementById('product-modal'); 
    const modalTitle = document.getElementById('modal-title');
    const productForm = document.getElementById('product-form');
    const closeButton = document.querySelector('.close-button');
    const productIdInput = document.getElementById('product-id');

    // ----------------------------------------------------------------------
    // Función para obtener y renderizar el inventario
    // ----------------------------------------------------------------------
    async function loadInventory() { 
        try {
            const response = await fetch('/api/inventory');
            if (!response.ok) {
                throw new Error(`Error al obtener inventario: ${response.status}`);
            }

            const products = await response.json();
            
            // Limpiar la tabla antes de renderizar
            inventoryTableBody.innerHTML = ''; 

            products.forEach(product => {
                const row = createProductRow(product);
                inventoryTableBody.appendChild(row);
            });
            
            console.log('Inventario cargado exitosamente.');
            
        } catch (error) {
            console.error('Error al cargar el inventario:', error);
            inventoryTableBody.innerHTML = '<tr><td colspan="7">Error al conectar con el servidor para obtener el inventario.</td></tr>';
        }
    }
    
    // Función para crear la fila de la tabla
    function createProductRow(product) {
        const priceFormatted = parseFloat(product.price).toFixed(2);
        const stock = parseInt(product.stock);

        const stockClass = stock > 50 ? 'stock-high' : stock > 10 ? 'stock-in' : stock > 0 ? 'stock-warning' : 'stock-out';
        const status = stock > 0 ? 'En Stock' : 'Agotado';
        const statusClass = status === 'Agotado' ? 'status-out' : 'status-in';

        const row = document.createElement('tr');
        row.setAttribute('data-id', product.id); 
        
        row.innerHTML = `
            <td>${product.id}</td>
            <td>${product.name}</td>
            <td>${product.category}</td>
            <td class="${stockClass}">${stock}</td>
            <td>$${priceFormatted}</td>
            <td class="${statusClass}">${status}</td>
            <td>
                <button class="btn-action btn-edit" data-id="${product.id}"><i class="fas fa-edit"></i></button>
                <button class="btn-action btn-delete" data-id="${product.id}"><i class="fas fa-trash-alt"></i></button>
            </td>
        `;
        
        row.querySelector('.btn-edit').addEventListener('click', () => openModalForEdit(product));
        row.querySelector('.btn-delete').addEventListener('click', () => deleteProductHandler(product.id, product.name));
        
        return row;
    }
    
    // --- MANEJO DEL MODAL ---
    addButton.addEventListener('click', () => {
        modalTitle.textContent = 'Añadir Nuevo Producto';
        productForm.reset();
        productIdInput.value = ''; 
        modal.style.display = 'flex';
    });
    
    function openModalForEdit(product) {
        modalTitle.textContent = `Editar Producto: ${product.name}`;
        productIdInput.value = product.id; 
        document.getElementById('product-name').value = product.name;
        document.getElementById('product-category').value = product.category;
        document.getElementById('product-stock').value = product.stock;
        document.getElementById('product-price').value = product.price;
        modal.style.display = 'flex';
    }
    
    closeButton.addEventListener('click', () => {
        modal.style.display = 'none';
    });
    
    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
    
    // ----------------------------------------------------------------------
    // MANEJO DE ENVÍO DE FORMULARIO (Usa ASYNC y AWAIT)
    // ----------------------------------------------------------------------
    
    productForm.addEventListener('submit', async (event) => { // Función ASYNC
        event.preventDefault();
        
        const isEditing = productIdInput.value !== '';
        const url = isEditing ? `/api/inventory/${productIdInput.value}` : '/api/inventory';
        const method = isEditing ? 'PUT' : 'POST';

        const productData = {
            name: document.getElementById('product-name').value,
            category: document.getElementById('product-category').value,
            stock: document.getElementById('product-stock').value,
            price: document.getElementById('product-price').value,
        };

        try {
            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(productData),
            });

            const data = await response.json();

            if (data.success) {
                alert(data.message);
                modal.style.display = 'none';
                
                await loadInventory(); // Usa AWAIT DENTRO de la función ASYNC
            } else {
                alert(`Error: ${data.message}`);
            }
        } catch (error) {
            console.error('Error al enviar datos:', error);
            alert('Error de conexión con el servidor. No se pudo guardar el producto.');
        }
    });

    // ----------------------------------------------------------------------
    // MANEJO DE ELIMINACIÓN (Es ASYNC y usa AWAIT)
    // ----------------------------------------------------------------------
    async function deleteProductHandler(id, name) { // Función ASYNC
        if (confirm(`¿Estás seguro de que quieres eliminar el producto ${name} (${id})?`)) {
            try {
                const response = await fetch(`/api/inventory/${id}`, {
                    method: 'DELETE',
                });

                const data = await response.json();
                
                if (data.success) {
                    alert(data.message);
                    
                    await loadInventory(); // Usa AWAIT DENTRO de la función ASYNC
                } else {
                    alert(`Error: ${data.message}`);
                }
            } catch (error) {
                console.error('Error al eliminar producto:', error);
                alert('Error de conexión con el servidor. No se pudo eliminar el producto.');
            }
        }
    }

    // 3. CARGA INICIAL: SIN AWAIT
    loadInventory(); // <--- LÍNEA CLAVE: SIN 'await'
});