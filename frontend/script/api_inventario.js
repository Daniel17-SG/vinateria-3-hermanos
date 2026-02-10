// La URL de tu API de Django
const urlApi = 'http://127.0.0.1:8000/api/productos/';

async function cargarProductos() {
    try {
        const respuesta = await fetch(urlApi);
        const productos = await respuesta.json();

        const tabla = document.getElementById('cuerpo-tabla-inventario');
tabla.innerHTML = ''; // Limpiamos ejemplos viejos

productos.forEach(p => {
    tabla.innerHTML += `
        <tr>
            <td>API-${p.id}</td> 
            <td>${p.nombre}</td>
            <td>General</td>
            <td>${p.existencias}</td>
            <td>$${p.precio}</td>
            <td><span class="badge ${p.existencias > 0 ? 'bg-success' : 'bg-danger'}">
                ${p.existencias > 0 ? 'En Stock' : 'Agotado'}
            </span></td>
            <td>
                <button class="btn btn-sm btn-info">📝</button>
            </td>
        </tr>
    `;
});
    } catch (error) {
        console.error('Error conectando con Django:', error);
    }
}

// Llamar a la función al cargar la página
document.addEventListener('DOMContentLoaded', cargarProductos);