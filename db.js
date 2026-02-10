// db.js (Archivo de la base de datos simulada - ACTUALIZADO)

let products = [
    { id: 'TQL001', name: 'Tequila Don Julio 70', category: 'Tequila', stock: 45, price: 1550.00, status: 'En Stock' },
    { id: 'WSK005', name: 'Whisky Buchanans 18', category: 'Whisky', stock: 10, price: 1950.00, status: 'Stock Bajo' },
    { id: 'BND003', name: 'Brandy Torres 20', category: 'Brandy', stock: 0, price: 2450.00, status: 'Agotado' },
];

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

// --- FUNCIONES CRUD DEL INVENTARIO (NUEVAS Y MODIFICADAS) ---

// 1. LECTURA: Obtener todos los productos
const getInventory = () => {
    return products; 
};

// 2. CREACIÓN: Añadir nuevo producto
const addProduct = (newProduct) => {
    // Verificar si ya existe un producto con el mismo nombre (opcional)
    if (products.some(p => p.name === newProduct.name)) {
        return null; // O manejar el error de otra manera
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

    products.push(productToAdd);
    return productToAdd;
};

// 3. ACTUALIZACIÓN: Modificar un producto existente
const updateProduct = (updatedProduct) => {
    const index = products.findIndex(p => p.id === updatedProduct.id);
    
    if (index !== -1) {
        const stock = parseInt(updatedProduct.stock) || 0;
        
        products[index].name = updatedProduct.name;
        products[index].category = updatedProduct.category;
        products[index].stock = stock;
        products[index].price = parseFloat(updatedProduct.price) || 0;
        products[index].status = getStatus(stock);

        return products[index];
    }
    return null; // Producto no encontrado
};

// 4. ELIMINACIÓN: Borrar un producto
const deleteProduct = (id) => {
    const initialLength = products.length;
    products = products.filter(p => p.id !== id);
    return products.length < initialLength; // Retorna true si se eliminó, false si no se encontró
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