// server.js

// 1. Importar Express y Body-Parser
const express = require('express');
const bodyParser = require('body-parser');
// Importar las funciones de la base de datos simulada
const db = require('./db');

const app = express();
const PORT = 3000; // Puerto donde correrá el servidor

// 2. Configuración de Middlewares
// Permite que Express lea datos JSON enviados en peticiones POST
app.use(bodyParser.json());
const path = require('path');
// Sirve archivos estáticos (HTML, CSS, JS del Front-End) desde la carpeta frontend
app.use(express.static(path.join(__dirname, '../frontend')));

// 3. RUTAS API (Endpoints)

// 3.1. LOGIN (POST /login)
app.post('/login', (req, res) => {
    const { email, password } = req.body;
    const user = db.findUser(email, password);

    if (user && user.role === 'admin') {
        // Si es administrador (ej: daniel@gmail.com, 1234), redirige a admi.html
        return res.json({ success: true, redirect: 'admi.html' });
    } else if (user) {
        // Si es usuario normal, redirige a index.html
        return res.json({ success: true, redirect: 'index.html' });
    } else {
        // Credenciales incorrectas
        return res.status(401).json({ success: false, message: 'Correo o contraseña incorrectos.' });
    }
});

// 3.2. REGISTRO (POST /register)
app.post('/register', (req, res) => {
    const { name, email, password } = req.body;

    const newUser = db.registerUser(name, email, password);

    if (newUser) {
        return res.json({
            success: true,
            message: '¡Registro exitoso! Ya puedes iniciar sesión.',
            redirect: 'login.html' // Redirige al usuario a la página de login
        });
    } else {
        // Error: El correo ya existe
        return res.status(409).json({ success: false, message: 'El correo electrónico ya está registrado.' });
    }
});
// server.js (AGREGAR ESTAS RUTAS)
// ... (código existente de imports y app.use) ...

// 3.3. OBTENER INVENTARIO (GET /api/inventory)
app.get('/api/inventory', (req, res) => {
    const inventory = db.getInventory();
    return res.json(inventory);
});

// 3.4. AÑADIR PRODUCTO (POST /api/inventory)
app.post('/api/inventory', (req, res) => {
    const newProduct = req.body;
    const addedProduct = db.addProduct(newProduct);

    if (addedProduct) {
        return res.json({ success: true, product: addedProduct, message: 'Producto añadido con éxito.' });
    } else {
        return res.status(400).json({ success: false, message: 'Error al añadir el producto.' });
    }
});

// 3.5. ACTUALIZAR PRODUCTO (PUT /api/inventory/:id)
app.put('/api/inventory/:id', (req, res) => {
    const productId = req.params.id;
    const updatedData = { ...req.body, id: productId }; // Aseguramos que el ID esté en los datos
    const updatedProduct = db.updateProduct(updatedData);

    if (updatedProduct) {
        return res.json({ success: true, product: updatedProduct, message: 'Producto actualizado con éxito.' });
    } else {
        return res.status(404).json({ success: false, message: 'Producto no encontrado.' });
    }
});

// 3.6. ELIMINAR PRODUCTO (DELETE /api/inventory/:id)
app.delete('/api/inventory/:id', (req, res) => {
    const productId = req.params.id;
    const deleted = db.deleteProduct(productId);

    if (deleted) {
        return res.json({ success: true, message: 'Producto eliminado con éxito.' });
    } else {
        return res.status(404).json({ success: false, message: 'Producto no encontrado.' });
    }
});

// 3.7. CREAR PEDIDO (POST /api/orders)
app.post('/api/orders', (req, res) => {
    const orderData = req.body;
    const result = db.createOrder(orderData);

    if (result.success) {
        return res.json({ success: true, order: result.order, message: 'Pedido creado exitosamente.' });
    } else {
        return res.status(400).json({ success: false, message: result.message });
    }
});

// ... (código existente del app.listen) ...

// 4. Iniciar el servidor
// Modificación para Vercel: Exportar la app
if (require.main === module) {
    app.listen(PORT, () => {
        console.log(`Servidor Back-End corriendo en http://localhost:${PORT}`);
        console.log(`Accede a tu proyecto en: http://localhost:${PORT}/index.html`);
    });
}

module.exports = app;