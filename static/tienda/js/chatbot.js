document.addEventListener('DOMContentLoaded', function () {
    const widget = document.getElementById('chatbot-widget');
    const toggle = document.getElementById('chatbot-toggle');
    const panel = document.getElementById('chatbot-panel');
    const closeBtn = document.getElementById('chatbot-close');
    const form = document.getElementById('chatbot-form');
    const input = document.getElementById('chatbot-input');
    const messages = document.getElementById('chatbot-messages');
    const sendBtn = document.getElementById('chatbot-send');

    if (!widget || !toggle || !panel || !closeBtn || !form || !input || !messages || !sendBtn) {
        return;
    }

    function getCookie(name) {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith(name + '='));
        return cookieValue ? decodeURIComponent(cookieValue.split('=')[1]) : '';
    }

    function appendMessage(text, who) {
        const node = document.createElement('article');
        node.className = 'chatbot-message ' + (who === 'user' ? 'chatbot-user' : 'chatbot-bot');
        node.textContent = text;
        messages.appendChild(node);
        messages.scrollTop = messages.scrollHeight;
    }

    function setOpenState(isOpen) {
        panel.classList.toggle('chatbot-hidden', !isOpen);
        widget.classList.toggle('chatbot-open', isOpen);
        if (isOpen) {
            input.focus();
        }
    }

    toggle.addEventListener('click', function () {
        setOpenState(panel.classList.contains('chatbot-hidden'));
    });

    closeBtn.addEventListener('click', function () {
        setOpenState(false);
    });

    form.addEventListener('submit', async function (event) {
        event.preventDefault();

        const mensaje = input.value.trim();
        if (mensaje.length < 2) {
            return;
        }

        appendMessage(mensaje, 'user');
        input.value = '';
        sendBtn.disabled = true;

        try {
            const response = await fetch('/api/chatbot/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ mensaje: mensaje })
            });

            const data = await response.json();
            if (response.ok && data.success && data.respuesta) {
                appendMessage(data.respuesta, 'bot');
            } else {
                appendMessage(data.error || 'No pude responder en este momento. Intenta de nuevo.', 'bot');
            }
        } catch (error) {
            appendMessage('Se perdió la conexión con el asistente. Intenta nuevamente.', 'bot');
        } finally {
            sendBtn.disabled = false;
            input.focus();
        }
    });
});
