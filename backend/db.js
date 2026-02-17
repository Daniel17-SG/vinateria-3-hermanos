// db.js (Archivo de la base de datos simulada - CON PERSISTENCIA)
const fs = require('fs');
const path = require('path');

const productsFilePath = path.join(__dirname, 'products.json');

// Función para cargar productos desde el archivo
const loadProducts = () => {
    try {
        const data = fs.readFileSync(productsFilePath, 'utf8');
        return JSON.parse(data);
    } catch (err) {
        // Si el archivo no existe o está vacío, retorna un array vacío.
        // Si hay un error de parseo, también retorna un array vacío y loggea el error.
        if (err.code === 'ENOENT' || err.message.includes('Unexpected end of JSON input')) {
            return [];
        }
        console.error("Error al cargar productos:", err);
        return [];
    }
};

// Función para guardar productos en el archivo
const saveProducts = (products) => {
    try {
        fs.writeFileSync(productsFilePath, JSON.stringify(products, null, 4));
        return true;
    } catch (err) {
        console.error("Error al guardar productos:", err);
        return false;
    }
};

// Cargar productos al iniciar (simulación de caché, aunque lo leeremos fresco en cada op para seguridad simple)
let products = loadProducts();

let users = [
    { email: 'admin@3hermanos.com', password: 'admin123', role: 'admin' },
    { email: 'daniel@gmail.com', password: '1234', role: 'admin' },
    { email: 'usuario@mail.com', password: 'password', role: 'user' },
];

// --- FUNCIONES INTERNAS ---

const generateProductId = () => {
    // Genera un ID corto basado en el tiempo
    return 'PRD' + Date.now().toString().slice(-6);
};

const getStatus = (stock) => {
    if (stock > 50) return 'Abundante';
    if (stock > 0) return 'En Stock';
    return 'Agotado';
};

// --- FUNCIÓN DE AUTENTICACIÓN ---
const findUser = (email, password) => {
    return users.find(u => u.email === email && u.password === password);
};

const registerUser = (name, email, password) => {
    if (users.some(u => u.email === email)) {
        return null;
    }
    const newUser = { name, email, password, role: 'user' };
    users.push(newUser);
    return newUser;
};

// --- FUNCIONES CRUD DEL INVENTARIO (CON PERSISTENCIA) ---

// 1. LECTURA: Obtener todos los productos
const getInventory = () => {
    return loadProducts(); // Leer siempre la versión más reciente del disco
};

// 2. CREACIÓN: Añadir nuevo producto
const addProduct = (newProduct) => {
    const currentProducts = loadProducts();

    // Verificar si ya existe un producto con el mismo nombre (opcional)
    if (currentProducts.some(p => p.name === newProduct.name)) {
        return null;
    }

    const stock = parseInt(newProduct.stock) || 0;
    const productToAdd = {
        id: generateProductId(),
        name: newProduct.name,
        category: newProduct.category,
        stock: stock,
        price: parseFloat(newProduct.price) || 0,
        status: getStatus(stock),
    };

    currentProducts.push(productToAdd);
    saveProducts(currentProducts); // Guardar cambios
    return productToAdd;
};

// 3. ACTUALIZACIÓN: Modificar un producto existente
const updateProduct = (updatedProduct) => {
    const currentProducts = loadProducts();
    const index = currentProducts.findIndex(p => p.id === updatedProduct.id);

    if (index !== -1) {
        const stock = parseInt(updatedProduct.stock) || 0;

        currentProducts[index].name = updatedProduct.name;
        currentProducts[index].category = updatedProduct.category;
        currentProducts[index].stock = stock;
        currentProducts[index].price = parseFloat(updatedProduct.price) || 0;
        currentProducts[index].status = getStatus(stock);

        saveProducts(currentProducts); // Guardar cambios
        return currentProducts[index];
    }
    return null; // Producto no encontrado
};

// 4. ELIMINACIÓN: Borrar un producto
const deleteProduct = (id) => {
    let currentProducts = loadProducts();
    const initialLength = currentProducts.length;

    currentProducts = currentProducts.filter(p => p.id !== id);

    if (currentProducts.length < initialLength) {
        saveProducts(currentProducts); // Guardar cambios
        return true;
    }
    return false;
};


// Exportar las funciones
module.exports = {
    findUser,
    registerUser,
    getInventory,
    addProduct,
    updateProduct,
    deleteProduct
};