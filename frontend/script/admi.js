// ====================================
// Admin Dashboard — Interactive KPI Cards
// ====================================
document.addEventListener('DOMContentLoaded', () => {

    // ---------- KPI Datasets ----------
    const KPI_DATA = {
        ventas: {
            title: '<i class="fas fa-dollar-sign"></i> Ventas del Mes — Desglose',
            chart: {
                type: 'bar',
                labels: ['Tequila', 'Whisky', 'Brandy', 'Vodka', 'Ron'],
                data: [42500, 38200, 15800, 21400, 17600],
                colors: ['#e76f21', '#3F90FF', '#FFC107', '#17A2B8', '#28A745']
            },
            table: {
                headers: ['Categoría', 'Ventas', 'Unidades', 'Variación'],
                rows: [
                    ['Tequila', '$42,500', '68', '+18%'],
                    ['Whisky', '$38,200', '42', '+8%'],
                    ['Brandy', '$15,800', '35', '-3%'],
                    ['Vodka', '$21,400', '33', '+22%'],
                    ['Ron', '$17,600', '44', '+5%']
                ]
            }
        },
        stock: {
            title: '<i class="fas fa-boxes"></i> Inventario por Categoría',
            chart: {
                type: 'doughnut',
                labels: ['Tequila', 'Whisky', 'Brandy', 'Vodka', 'Ron'],
                data: [220, 180, 140, 160, 156],
                colors: ['#e76f21', '#3F90FF', '#FFC107', '#17A2B8', '#28A745']
            },
            table: {
                headers: ['Producto', 'Stock', 'Mín. Req.', 'Estado'],
                rows: [
                    ['Tequila Maestro Dobel', '45', '20', '✅ OK'],
                    ['Whisky Buchanans 18', '12', '15', '⚠️ Bajo'],
                    ['Brandy Torres 10', '38', '15', '✅ OK'],
                    ['Vodka Absolut', '8', '10', '🔴 Crítico'],
                    ['Ron Matusalem', '52', '20', '✅ OK'],
                    ['Whisky Jack Daniels', '22', '15', '✅ OK']
                ]
            }
        },
        clientes: {
            title: '<i class="fas fa-users"></i> Nuevos Clientes — Últimos 6 Meses',
            chart: {
                type: 'line',
                labels: ['Sep', 'Oct', 'Nov', 'Dic', 'Ene', 'Feb'],
                data: [32, 45, 58, 72, 48, 45],
                colors: ['#17A2B8']
            },
            table: {
                headers: ['Cliente', 'Fecha Registro', 'Compras', 'Total'],
                rows: [
                    ['Ana García', '15 Feb 2024', '3', '$5,200'],
                    ['Jorge Ramírez', '12 Feb 2024', '1', '$1,850'],
                    ['Elena Martínez', '08 Feb 2024', '5', '$12,400'],
                    ['Carlos López', '03 Feb 2024', '2', '$3,600'],
                    ['María Sánchez', '28 Ene 2024', '4', '$8,900']
                ]
            }
        },
        pedidos: {
            title: '<i class="fas fa-shipping-fast"></i> Pedidos — Estado Actual',
            chart: {
                type: 'pie',
                labels: ['Entregado', 'Enviado', 'Pendiente', 'Cancelado'],
                data: [45, 18, 8, 3],
                colors: ['#28A745', '#17A2B8', '#FFC107', '#DC3545']
            },
            table: {
                headers: ['ID Pedido', 'Cliente', 'Total', 'Estado'],
                rows: [
                    ['#00123', 'Ana García', '$5,200', 'Entregado'],
                    ['#00124', 'Jorge Ramírez', '$1,850', 'Pendiente'],
                    ['#00125', 'Elena Martínez', '$12,400', 'Enviado'],
                    ['#00126', 'Carlos López', '$3,600', 'Pendiente'],
                    ['#00127', 'María Sánchez', '$8,900', 'Entregado'],
                    ['#00128', 'Luis Torres', '$2,150', 'Enviado'],
                    ['#00129', 'Rosa Hernández', '$4,300', 'Pendiente'],
                    ['#00130', 'Pedro Díaz', '$1,200', 'Cancelado']
                ]
            }
        }
    };

    // ---------- Elements ----------
    const cards = document.querySelectorAll('.kpi-card[data-kpi]');
    const panel = document.getElementById('kpi-detail-panel');
    const titleEl = document.getElementById('detail-title');
    const tableContainer = document.getElementById('detail-table-container');
    const extraActions = document.getElementById('extra-actions');
    const addClientFormBox = document.getElementById('add-client-form');
    const clientForm = document.getElementById('new-client-form');
    const btnCancelClient = document.getElementById('btn-cancel-client');

    let currentChart = null;
    let activeKpi = null;

    // ---------- Card Click Handler ----------
    cards.forEach(card => {
        card.addEventListener('click', () => handleCardClick(card));
        card.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                handleCardClick(card);
            }
        });
    });

    function handleCardClick(card) {
        const kpi = card.dataset.kpi;

        // Toggle: close if clicking same card
        if (activeKpi === kpi) {
            closePanel();
            return;
        }

        // Mark active
        cards.forEach(c => c.classList.remove('active-card'));
        card.classList.add('active-card');
        activeKpi = kpi;

        // Reset forms
        addClientFormBox.style.display = 'none';

        // Show panel
        const data = KPI_DATA[kpi];
        if (!data) return;

        titleEl.innerHTML = data.title;
        renderTable(data.table);
        renderChart(data.chart);

        // Handle extra actions (like Add Client button)
        extraActions.innerHTML = '';
        if (kpi === 'clientes') {
            const btnAdd = document.createElement('button');
            btnAdd.className = 'btn-add-item';
            btnAdd.innerHTML = '<i class="fas fa-plus"></i> Añadir Cliente';
            btnAdd.onclick = () => {
                addClientFormBox.style.display = addClientFormBox.style.display === 'none' ? 'block' : 'none';
                if (addClientFormBox.style.display === 'block') {
                    addClientFormBox.scrollIntoView({ behavior: 'smooth' });
                }
            };
            extraActions.appendChild(btnAdd);
        }

        panel.classList.add('visible');
        panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    function closePanel() {
        panel.classList.remove('visible');
        cards.forEach(c => c.classList.remove('active-card'));
        activeKpi = null;
        if (currentChart) { currentChart.destroy(); currentChart = null; }
        addClientFormBox.style.display = 'none';
    }

    // ---------- Client Form Handling ----------
    if (clientForm) {
        clientForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const name = document.getElementById('client-name').value;
            const dateInput = document.getElementById('client-date').value;
            const compras = document.getElementById('client-compras').value;
            const total = document.getElementById('client-total').value;

            // Format date for display
            const dateObj = new Date(dateInput);
            const months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
            const formattedDate = `${dateObj.getDate().toString().padStart(2, '0')} ${months[dateObj.getMonth()]} ${dateObj.getFullYear()}`;

            // Add to data
            KPI_DATA.clientes.table.rows.unshift([
                name,
                formattedDate,
                compras,
                `$${parseFloat(total).toLocaleString('es-MX', { minimumFractionDigits: 0 })}`
            ]);

            // Update UI
            renderTable(KPI_DATA.clientes.table);
            addClientFormBox.style.display = 'none';
            clientForm.reset();
            alert('¡Cliente añadido exitosamente!');
        });
    }

    if (btnCancelClient) {
        btnCancelClient.addEventListener('click', () => {
            addClientFormBox.style.display = 'none';
        });
    }

    // ---------- Render Table ----------
    function renderTable(tableData) {
        const headerHtml = tableData.headers.map(h => `<th>${h}</th>`).join('');
        const rowsHtml = tableData.rows.map(row => {
            const cells = row.map(cell => {
                let cls = '';
                if (cell === 'Entregado') cls = ' style="color:#28A745;font-weight:600"';
                else if (cell === 'Pendiente') cls = ' style="color:#FFC107;font-weight:600"';
                else if (cell === 'Enviado') cls = ' style="color:#17A2B8;font-weight:600"';
                else if (cell === 'Cancelado') cls = ' style="color:#DC3545;font-weight:600"';
                return `<td${cls}>${cell}</td>`;
            }).join('');
            return `<tr>${cells}</tr>`;
        }).join('');

        tableContainer.innerHTML = `
            <table>
                <thead><tr>${headerHtml}</tr></thead>
                <tbody>${rowsHtml}</tbody>
            </table>`;
    }

    // ---------- Render Chart ----------
    function renderChart(chartData) {
        if (currentChart) currentChart.destroy();

        const ctx = document.getElementById('detailChart');
        const isLine = chartData.type === 'line';

        const dataset = {
            label: 'Datos',
            data: chartData.data,
            backgroundColor: isLine ? 'rgba(23,162,184,0.15)' : chartData.colors,
            borderColor: isLine ? '#17A2B8' : chartData.colors,
            borderWidth: 2
        };

        if (isLine) {
            dataset.fill = true;
            dataset.tension = 0.35;
            dataset.pointRadius = 5;
            dataset.pointBackgroundColor = '#17A2B8';
        } else if (chartData.type === 'bar') {
            dataset.borderRadius = 6;
        }

        const isCircular = chartData.type === 'pie' || chartData.type === 'doughnut';

        currentChart = new Chart(ctx, {
            type: chartData.type,
            data: {
                labels: chartData.labels,
                datasets: [dataset]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: isCircular, position: 'bottom' },
                    tooltip: {
                        backgroundColor: '#212529',
                        titleFont: { size: 13 },
                        bodyFont: { size: 12 }
                    }
                },
                ...(isCircular ? {} : {
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: { color: 'rgba(0,0,0,0.05)' }
                        },
                        x: { grid: { display: false } }
                    }
                })
            }
        });
    }

    // ---------- Logout ----------
    const logoutBtn = document.querySelector('.logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            localStorage.removeItem('userSession');
            window.location.href = 'index.html';
        });
    }
});