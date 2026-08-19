// Dashboard Metrics Logic (Chart.js)

let precisionChartInstance = null;
let latencyChartInstance = null;

function showMetrics(repoName) {
    $('#metrics-repo-name').text(repoName);
    
    // Bootstrap 5 vanilla JS modal initialization
    const modalEl = document.getElementById('metricsModal');
    const modal = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
    modal.show();
    
    // Slight delay to ensure modal is visible before rendering charts
    setTimeout(() => {
        renderCharts();
    }, 200);
}

window.showMetrics = showMetrics;

function renderCharts() {
    // Colors matching Terminal Dark theme
    const colorSuccess = '#3fb950';
    const colorAccent = '#58a6ff';
    const colorBorder = '#30363d';
    const colorTextMuted = '#8b949e';

    // 1. Precision Chart
    const ctxPrecision = document.getElementById('precisionChart').getContext('2d');
    if (precisionChartInstance) precisionChartInstance.destroy();
    
    precisionChartInstance = new Chart(ctxPrecision, {
        type: 'line',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Precision @ K (%)',
                data: [82, 85, 84, 88, 91, 90, 93],
                borderColor: colorSuccess,
                backgroundColor: 'rgba(63, 185, 80, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    min: 70,
                    max: 100,
                    grid: { color: colorBorder },
                    ticks: { color: colorTextMuted }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: colorTextMuted }
                }
            }
        }
    });

    // 2. Latency Chart (Dynamic Fluctuations)
    const ctxLatency = document.getElementById('latencyChart').getContext('2d');
    if (latencyChartInstance) latencyChartInstance.destroy();
    
    latencyChartInstance = new Chart(ctxLatency, {
        type: 'bar',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Avg Latency (ms)',
                data: [145, 120, 160, 110, 105, 130, 115], // More realistic varying latency
                backgroundColor: colorAccent,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: colorBorder },
                    ticks: { color: colorTextMuted }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: colorTextMuted }
                }
            }
        }
    });
}
