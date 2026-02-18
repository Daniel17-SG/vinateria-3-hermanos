// contact.js - handle contact form: validate, save to localStorage, show feedback
document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('contact-form');
    const clearBtn = document.getElementById('contact-clear');

    function getMessages() {
        return JSON.parse(localStorage.getItem('contactMessages') || '[]');
    }
    function saveMessages(list) {
        localStorage.setItem('contactMessages', JSON.stringify(list));
    }

    function showToast(text) {
        let t = document.getElementById('contact-toast');
        if (!t) {
            t = document.createElement('div');
            t.id = 'contact-toast';
            t.style.position = 'fixed';
            t.style.right = '20px';
            t.style.bottom = '20px';
            t.style.zIndex = 9999;
            document.body.appendChild(t);
        }
        t.textContent = text;
        t.style.background = 'rgba(0,0,0,0.8)';
        t.style.color = '#fff';
        t.style.padding = '12px 16px';
        t.style.borderRadius = '8px';
        t.style.boxShadow = '0 6px 20px rgba(0,0,0,0.6)';
        t.style.opacity = '1';
        setTimeout(() => { if (t) t.style.opacity = '0'; }, 2200);
    }

    if (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            const name = (document.getElementById('contact-name') || {}).value?.trim();
            const email = (document.getElementById('contact-email') || {}).value?.trim();
            const message = (document.getElementById('contact-message') || {}).value?.trim();

            if (!name || !email || !message) {
                showToast('Por favor completa todos los campos.');
                return;
            }

            const messages = getMessages();
            messages.push({ name, email, message, date: new Date().toISOString() });
            saveMessages(messages);

            form.reset();
            showToast('Gracias — tu mensaje fue enviado.');
        });
    }

    if (clearBtn) {
        clearBtn.addEventListener('click', function () {
            if (form) form.reset();
        });
    }
});
