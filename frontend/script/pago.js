document.addEventListener('DOMContentLoaded', () => {
    // Referencias
    const paymentOptions = document.querySelectorAll('input[name="metodo_pago"]');
    const paypalContainer = document.getElementById('paypal-button-container');
    const confirmButton = document.querySelector('.btn-final-pago');
    const cardDetails = document.querySelector('.card-details');

    let isPayPalRendered = false;

    function renderPayPalButtons() {
        if (isPayPalRendered) return;

        if (typeof paypal === 'undefined') {
            console.error('El SDK de PayPal no se cargó correctamente.');
            alert('Error: No se pudo cargar PayPal. Verifica tu conexión.');
            return;
        }

        paypal.Buttons({
            createOrder: function (data, actions) {
                const totalText = document.querySelector('.total-price').textContent;
                const totalAmount = parseFloat(totalText.replace(/[$,]/g, ''));
                return actions.order.create({
                    purchase_units: [{ amount: { value: totalAmount.toString() } }]
                });
            },

            onApprove: function (data, actions) {
                return actions.order.capture().then(async function (details) {
                    // 1. Recopilar datos del pedido
                    const cart = JSON.parse(localStorage.getItem('cart')) || [];
                    const user = JSON.parse(localStorage.getItem('user')) || { name: 'Invitado', email: 'invitado@mail.com' };
                    const totalText = document.querySelector('.total-price').textContent;

                    const orderData = {
                        customer: {
                            name: details.payer.name.given_name + ' ' + details.payer.name.surname,
                            email: details.payer.email_address,
                            payerId: details.payer.payer_id
                        },
                        items: cart, // Asegúrate que el carrito tenga ids que coincidan con la DB
                        total: parseFloat(totalText.replace(/[$,]/g, '')),
                        paymentMethod: 'PayPal'
                    };

                    // 2. Enviar al Backend
                    try {
                        const response = await fetch('/api/orders', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(orderData)
                        });

                        const result = await response.json();

                        if (result.success) {
                            alert(`¡Pago exitoso! ID de Orden: ${result.order.id}`);
                            localStorage.removeItem('cart');
                            window.location.href = 'index.html';
                        } else {
                            alert('Pago en PayPal exitoso, pero hubo error guardando la orden: ' + result.message);
                        }
                    } catch (error) {
                        console.error('Error al guardar la orden:', error);
                        alert('Error de conexión con el servidor.');
                    }
                });
            },

            onError: function (err) {
                console.error('Error en PayPal:', err);
                alert('Hubo un error al procesar el pago con PayPal.');
            }
        }).render('#paypal-button-container');

        isPayPalRendered = true;
    }

    // 1. Manejo de Selección de Método de Pago
    paymentOptions.forEach(option => {
        option.addEventListener('change', (e) => {
            const selected = e.target.value;

            // Reset visual
            document.querySelectorAll('.payment-option').forEach(el => el.classList.remove('active'));
            e.target.closest('.payment-option').classList.add('active');

            // Mostrar/Ocultar detalles según selección
            if (selected === 'paypal') {
                paypalContainer.style.display = 'block';
                confirmButton.style.display = 'none'; // Ocultar botón "Confirmar" normal
                if (cardDetails) cardDetails.style.display = 'none';

                // Renderizar botones de PayPal solo cuando se selecciona PayPal
                renderPayPalButtons();

            } else if (selected === 'tarjeta') {
                paypalContainer.style.display = 'none';
                confirmButton.style.display = 'block';
                if (cardDetails) cardDetails.style.display = 'block';
            } else {
                // Transferencia u otros
                paypalContainer.style.display = 'none';
                confirmButton.style.display = 'block';
                if (cardDetails) cardDetails.style.display = 'none';
            }
        });
    });
});
