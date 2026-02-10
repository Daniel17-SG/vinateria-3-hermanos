const express = require('express');
const mongoose = require('mongoose');
const path = require('path');
const app = express();

// Middleware para leer datos de formularios y JSON
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

// Servir archivos estáticos (tus HTML, CSS y JS actuales)
app.use(express.static(__dirname));

// Conexión a la Base de Datos (MongoDB)
mongoose.connect('mongodb://127.0.0.1:27017/vinateria_db')
    .then(() => console.log('✅ Conectado a MongoDB'))
    .catch(err => console.error('❌ Error de conexión:', err));

// Iniciar servidor
const PORT = 3000;
app.listen(PORT, () => {
    console.log(`🚀 Servidor funcionando en http://localhost:${PORT}`);
});