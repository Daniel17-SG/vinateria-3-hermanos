// cart-badge.js - utilidades compartidas para el badge del carrito
(function () {
    const TOAST_ID = 'cart-count-toast';
    function getCart() {
        return JSON.parse(localStorage.getItem('carrito')) || [];
    }

    function saveCart(cart) {
        localStorage.setItem('carrito', JSON.stringify(cart));
        updateBadge();
    }

    function formatNumber(n) {
        return n;
    }

    function getTotalQuantity(cart) {
        return (cart || getCart()).reduce((s, it) => s + (it.quantity || 0), 0);
    }

    function createToastIfNeeded() {
        let toast = document.getElementById(TOAST_ID);
        if (!toast) {
            toast = document.createElement('div');
            toast.id = TOAST_ID;
            toast.style.position = 'fixed';
            toast.style.right = '16px';
            toast.style.top = '16px';
            toast.style.zIndex = 9999;
            toast.style.pointerEvents = 'none';
            document.body.appendChild(toast);
        }
        return toast;
    }

    function showCountChangeToast(message) {
        const container = createToastIfNeeded();
        const el = document.createElement('div');
        el.textContent = message;
        el.style.background = 'rgba(0,0,0,0.8)';
        el.style.color = '#fff';
        el.style.padding = '10px 14px';
        el.style.borderRadius = '6px';
        el.style.marginTop = '8px';
        el.style.boxShadow = '0 4px 12px rgba(0,0,0,0.3)';
        el.style.opacity = '0';
        el.style.transition = 'opacity 0.25s, transform 0.3s';
        el.style.transform = 'translateY(-6px)';
        container.appendChild(el);
        requestAnimationFrame(() => {
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        });
        setTimeout(() => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(-6px)';
            setTimeout(() => container.removeChild(el), 300);
        }, 1800);
    }

    function updateAuthUI() {
        const userStr = localStorage.getItem('user');
        let user = null;
        try {
            user = (userStr && userStr !== "null" && userStr !== "undefined") ? JSON.parse(userStr) : null;
        } catch (e) { user = null; }

        const authContainers = document.querySelectorAll('.auth-nav, .header-icons');
        authContainers.forEach(container => {
            // Check if we already have a logout link
            let logoutLink = container.querySelector('.logout-link');
            if (user) {
                if (!logoutLink) {
                    logoutLink = document.createElement('a');
                    logoutLink.href = "#";
                    logoutLink.className = "icon-link logout-link";
                    logoutLink.innerHTML = '<i class="fas fa-sign-out-alt"></i> Salir';
                    logoutLink.style.marginLeft = "10px";
                    logoutLink.style.color = "#dc3545"; // Red color for logout
                    logoutLink.onclick = (e) => {
                        e.preventDefault();
                        cerrarSesion();
                    };
                    container.appendChild(logoutLink);
                }
                // Update user link if exists
                const userLink = container.querySelector('a[href="login.html"]');
                if (userLink) {
                    userLink.innerHTML = `<i class="fas fa-user-circle"></i> Holas, ${user.name.split(' ')[0]}`;
                    userLink.href = "#"; // Disable login link when logged in
                }
            } else {
                if (logoutLink) logoutLink.remove();
                const userLink = container.querySelector('a[href="login.html"], .icon-link:not(.cart-link):not(.logout-link):not(.nav-toggle)');
                if (userLink) {
                    userLink.innerHTML = '<i class="fas fa-user-circle"></i>';
                    userLink.href = "login.html";
                }
            }
        });
    }

    function updateBadge() {
        const cart = getCart();
        const total = getTotalQuantity(cart);

        // Update auth UI too
        updateAuthUI();

        // Update all badges with id cart-badge or class cart-badge
        const byId = document.querySelectorAll('#cart-badge');
        const byClass = document.querySelectorAll('.cart-badge');
        const nodes = new Set([...byId, ...byClass]);
        nodes.forEach(node => {
            if (node) {
                node.textContent = formatNumber(total);
                node.style.display = total > 0 ? 'inline-flex' : 'none';
            }
        });

        // Dispatch event if changed
        const prev = parseInt(document.documentElement.getAttribute('data-cart-total') || '0', 10);
        if (prev !== total) {
            document.documentElement.setAttribute('data-cart-total', String(total));
            const ev = new CustomEvent('cart:changed', { detail: { previous: prev, total } });
            window.dispatchEvent(ev);
            // Show a small toast for user feedback
            if (total > prev) {
                showCountChangeToast(`Carrito: +${total - prev} (total ${total})`);
            } else if (total < prev) {
                showCountChangeToast(`Carrito: −${prev - total} (total ${total})`);
            }
        }
    }

    function verificarSesion(redirectToPago = false) {
        const userStr = localStorage.getItem('user');
        let user = null;
        try {
            user = (userStr && userStr !== "null" && userStr !== "undefined") ? JSON.parse(userStr) : null;
        } catch (e) {
            user = null;
        }

        if (!user) {
            alert("✋ ¡Espera! Para tu seguridad, debes iniciar sesión antes de continuar.");
            window.location.href = "login.html";
            return false;
        }
        if (redirectToPago) {
            window.location.href = "pago.html";
        }
        return true;
    }

    function cerrarSesion() {
        localStorage.removeItem('user');
        alert("Has cerrado sesión exitosamente.");
        window.location.href = "index.html";
    }

    // Expose utilities
    window.cartUtils = {
        getCart,
        saveCart,
        updateBadge,
        getTotalQuantity,
        verificarSesion,
        cerrarSesion
    };

    // Auto run after DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', updateBadge);
    } else {
        updateBadge();
    }

})();
