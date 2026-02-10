document.addEventListener('DOMContentLoaded', () => {
    // 1. Manejo del botón de Cerrar Sesión (Logout)
    const logoutButton = document.querySelector('.logout-btn');

    if (logoutButton) {
        logoutButton.addEventListener('click', (event) => {
            // Previene la navegación inmediata del enlace <a>
            event.preventDefault(); 
            
            // Opcional: Si tu servidor tuviera una ruta /logout, la llamarías aquí.
            // fetch('/logout', { method: 'POST' }).then(() => {
            //     window.location.href = 'index.html';
            // });
            
            // Redirección simple al index.html
            window.location.href = 'index.html';
        });
    }

    // 2. Lógica Futura para Cargar Datos Dinámicos del Dashboard (KPIs y Tablas)
    // Cuando el Back-End esté listo, esta función cargará datos.
    async function loadDashboardData() {
        console.log("Intentando cargar datos del dashboard...");
        
        try {
            // EJEMPLO: Si tuvieras una API para obtener KPIs:
            // const response = await fetch('/api/dashboard/kpis');
            // const data = await response.json();
            
            // Aquí actualizarías los elementos con los IDs o clases correctas:
            // document.querySelector('.kpi-value-sales').textContent = data.sales;
            
        
            console.log("Datos cargados. (KPIs y Tablas usan datos estáticos en el HTML por ahora).");
            
        } catch (error) {
            console.error('Error al cargar datos del dashboard:', error);
            
            
        }
    }

   
    loadDashboardData();
});