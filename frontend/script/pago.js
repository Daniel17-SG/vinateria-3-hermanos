// ====================================
// Checkout & Payment — Validation + Dynamic Summary
// ====================================
document.addEventListener('DOMContentLoaded', () => {
    // ---------- 0. Session Check ----------
    if (window.cartUtils && typeof window.cartUtils.verificarSesion === 'function') {
        if (!window.cartUtils.verificarSesion()) return;
    } else {
        const user = localStorage.getItem('user');
        if (!user) {
            alert("✋ ¡Espera! Para tu seguridad, debes iniciar sesión antes de realizar el pago.");
            window.location.href = "login.html";
            return;
        }
    }

    // ---------- Elements ----------
    const paymentOptions = document.querySelectorAll('input[name="metodo_pago"]');
    const cardDetails = document.getElementById('card-details');
    const paypalContainer = document.getElementById('paypal-button-container');

    const cardNumberInput = document.getElementById('card-number');
    const cardExpiryInput = document.getElementById('card-expiry');
    const cardCvvInput = document.getElementById('card-cvv');
    const btnConfirm = document.getElementById('btn-confirm-pay');

    // ---------- 1. Payment Method Toggle ----------
    paymentOptions.forEach(option => {
        option.addEventListener('change', (e) => {
            const method = e.target.value;

            // Hide all details first
            if (cardDetails) cardDetails.style.display = 'none';
            if (paypalContainer) paypalContainer.style.display = 'none';

            // Show relevant section
            if (method === 'tarjeta' && cardDetails) {
                cardDetails.style.display = 'block';
            } else if (method === 'paypal' && paypalContainer) {
                paypalContainer.style.display = 'block';
                renderPayPalButtons();
            }

            // Toggle active class on parents
            document.querySelectorAll('.payment-option').forEach(opt => opt.classList.remove('active'));
            e.target.closest('.payment-option')?.classList.add('active');
        });
    });

    // ---------- 2. Card Number Mask (4-digit groups) ----------
    if (cardNumberInput) {
        cardNumberInput.addEventListener('input', (e) => {
            let v = e.target.value.replace(/\D/g, '').substring(0, 16);
            v = v.replace(/(.{4})/g, '$1 ').trim();
            e.target.value = v;
            validateCardNumber(v);
        });
    }

    function validateCardNumber(value) {
        const digits = value.replace(/\s/g, '');
        const msgEl = document.getElementById('card-number-msg');
        if (!msgEl) return false;

        if (digits.length === 0) {
            setMsg(msgEl, '', '');
            cardNumberInput.classList.remove('field-valid', 'field-error');
            return false;
        }
        if (digits.length < 16) {
            setMsg(msgEl, `Faltan ${16 - digits.length} dígitos`, 'error');
            cardNumberInput.classList.remove('field-valid');
            cardNumberInput.classList.add('field-error');
            return false;
        }
        // Luhn check
        if (!luhnCheck(digits)) {
            setMsg(msgEl, 'Número de tarjeta inválido', 'error');
            cardNumberInput.classList.remove('field-valid');
            cardNumberInput.classList.add('field-error');
            return false;
        }
        setMsg(msgEl, '✓ Tarjeta válida', 'success');
        cardNumberInput.classList.remove('field-error');
        cardNumberInput.classList.add('field-valid');
        return true;
    }

    function luhnCheck(num) {
        let sum = 0, alt = false;
        for (let i = num.length - 1; i >= 0; i--) {
            let n = parseInt(num[i], 10);
            if (alt) { n *= 2; if (n > 9) n -= 9; }
            sum += n;
            alt = !alt;
        }
        return sum % 10 === 0;
    }

    // ---------- 3. Expiry Date Mask (MM/YY) ----------
    if (cardExpiryInput) {
        cardExpiryInput.addEventListener('input', (e) => {
            let v = e.target.value.replace(/\D/g, '').substring(0, 4);
            if (v.length > 2) v = v.substring(0, 2) + '/' + v.substring(2);
            e.target.value = v;
            validateExpiry(v);
        });
    }

    function validateExpiry(value) {
        const msgEl = document.getElementById('card-expiry-msg');
        if (!msgEl) return false;

        if (value.length === 0) {
            setMsg(msgEl, '', '');
            cardExpiryInput.classList.remove('field-valid', 'field-error');
            return false;
        }
        const parts = value.split('/');
        if (parts.length !== 2 || parts[1].length < 2) {
            setMsg(msgEl, 'Formato: MM/AA', 'error');
            cardExpiryInput.classList.remove('field-valid');
            cardExpiryInput.classList.add('field-error');
            return false;
        }
        const month = parseInt(parts[0], 10);
        const year = parseInt('20' + parts[1], 10);
        const now = new Date();
        const expiry = new Date(year, month);
        if (month < 1 || month > 12) {
            setMsg(msgEl, 'Mes inválido', 'error');
            cardExpiryInput.classList.remove('field-valid');
            cardExpiryInput.classList.add('field-error');
            return false;
        }
        if (expiry < now) {
            setMsg(msgEl, 'Tarjeta expirada', 'error');
            cardExpiryInput.classList.remove('field-valid');
            cardExpiryInput.classList.add('field-error');
            return false;
        }
        setMsg(msgEl, '✓ Válida', 'success');
        cardExpiryInput.classList.remove('field-error');
        cardExpiryInput.classList.add('field-valid');
        return true;
    }

    // ---------- 4. CVV Validation ----------
    if (cardCvvInput) {
        cardCvvInput.addEventListener('input', (e) => {
            e.target.value = e.target.value.replace(/\D/g, '').substring(0, 4);
            validateCvv(e.target.value);
        });
    }

    function validateCvv(value) {
        const msgEl = document.getElementById('card-cvv-msg');
        if (!msgEl) return false;

        if (value.length === 0) {
            setMsg(msgEl, '', '');
            cardCvvInput.classList.remove('field-valid', 'field-error');
            return false;
        }
        if (value.length < 3) {
            setMsg(msgEl, '3–4 dígitos requeridos', 'error');
            cardCvvInput.classList.remove('field-valid');
            cardCvvInput.classList.add('field-error');
            return false;
        }
        setMsg(msgEl, '✓ CVV OK', 'success');
        cardCvvInput.classList.remove('field-error');
        cardCvvInput.classList.add('field-valid');
        return true;
    }

    // ---------- 5. Helper ----------
    function setMsg(el, text, type) {
        el.textContent = text;
        el.className = 'validation-msg' + (type ? ' ' + type : '');
    }

    // ---------- 6. Dynamic Order Summary from localStorage ----------
    function loadOrderSummary() {
        const cart = JSON.parse(localStorage.getItem('carrito')) || [];
        const subtotalEl = document.getElementById('checkout-subtotal');
        const taxEl = document.getElementById('checkout-tax');
        const totalEl = document.getElementById('checkout-total');

        if (!subtotalEl || !taxEl || !totalEl) return;

        const subtotal = cart.reduce((acc, item) => acc + (item.price * item.quantity), 0);
        const tax = subtotal * 0.16;
        const total = subtotal + tax;

        subtotalEl.textContent = '$' + subtotal.toLocaleString('es-MX', { minimumFractionDigits: 2 });
        taxEl.textContent = '$' + tax.toLocaleString('es-MX', { minimumFractionDigits: 2 });
        totalEl.textContent = '$' + total.toLocaleString('es-MX', { minimumFractionDigits: 2 });
    }
    loadOrderSummary();

    // ---------- 7. Form Submission ----------
    if (btnConfirm) {
        btnConfirm.addEventListener('click', (e) => {
            e.preventDefault();
            const selectedPayment = document.querySelector('input[name="metodo_pago"]:checked')?.value;

            if (selectedPayment === 'tarjeta') {
                const cardOk = validateCardNumber(cardNumberInput?.value || '');
                const expOk = validateExpiry(cardExpiryInput?.value || '');
                const cvvOk = validateCvv(cardCvvInput?.value || '');
                const holderEl = document.getElementById('card-holder');

                if (!cardOk || !expOk || !cvvOk || !holderEl?.value.trim()) {
                    alert('Por favor, corrige los campos marcados en rojo antes de continuar.');
                    return;
                }
            }

            alert('¡Pedido confirmado! 🎉\nRecibirás un correo con los detalles de tu compra.');
            localStorage.removeItem('carrito');
            window.location.href = 'index.html';
        });
    }

    // ---------- 8. PayPal Buttons ----------
    let paypalRendered = false;
    function renderPayPalButtons() {
        if (paypalRendered || typeof paypal === 'undefined') return;
        paypalRendered = true;
        paypal.Buttons({
            createOrder: function (data, actions) {
                const cart = JSON.parse(localStorage.getItem('carrito')) || [];
                const total = cart.reduce((a, i) => a + (i.price * i.quantity), 0);
                return actions.order.create({
                    purchase_units: [{ amount: { value: total.toFixed(2) } }]
                });
            },
            onApprove: function (data, actions) {
                return actions.order.capture().then(function (details) {
                    alert('Pago completado por ' + details.payer.name.given_name + '. ¡Gracias!');
                    localStorage.removeItem('carrito');
                    window.location.href = 'index.html';
                });
            }
        }).render('#paypal-button-container');
    }
});
