// carrito.js - middleware de autenticación para acceder al carrito
// Provide a helper function that pages can call when user tries to checkout
window.verificarSesion = function(){
    const session = localStorage.getItem('sessionUser');
    if(!session){
        const next = encodeURIComponent('pago.html');
        window.location.href = `login.html?next=${next}`;
        return false;
    }
    // user logged in: proceed to payment
    window.location.href = 'pago.html';
    return true;
};
