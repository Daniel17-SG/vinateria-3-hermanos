// pago.js - middleware de autenticación para proceso de pago
document.addEventListener('DOMContentLoaded', ()=>{
    const session = localStorage.getItem('sessionUser');
    if(!session){
        const next = encodeURIComponent(window.location.pathname.split('/').pop() || 'pago.html');
        window.location.href = `login.html?next=${next}`;
    }
});
