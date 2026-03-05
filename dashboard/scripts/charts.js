const ctx = document.getElementById('attentionChart').getContext('2d');
let attentionChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Attention Intensity',
            data: [],
            borderColor: '#00ff88',
            backgroundColor: 'rgba(0, 255, 136, 0.1)',
            fill: true,
            tension: 0.4
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: { beginAtZero: true, grid: { color: '#444' } },
            x: { grid: { color: '#444' } }
        },
        plugins: {
            legend: { labels: { color: '#fff' } }
        }
    }
});

function updateChart(timeline) {
    // Convert dictionary keys (timestamps) to labels and values to data points
    const labels = Object.keys(timeline).map(t => t.split(' ')[1]); // Extract HH:MM:SS
    const values = Object.values(timeline);

    attentionChart.data.labels = labels;
    attentionChart.data.datasets[0].data = values;
    attentionChart.update('none'); // 'none' prevents laggy animations during fast updates
}