// Initialize the Chart.js instance
const ctx = document.getElementById('attentionChart').getContext('2d');

let attentionChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [], 
        datasets: [{
            label: 'Cognitive Intensity',
            data: [],
            borderColor: '#00ff88', // Matrix Green
            backgroundColor: 'rgba(0, 255, 136, 0.1)',
            fill: true,
            tension: 0.4, 
            pointRadius: 0, // Remove dots for a clean waveform
            borderWidth: 2
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: false, // CRITICAL: Disable animation for real-time performance
        scales: {
            y: { 
                beginAtZero: true, 
                min: 0,
                max: 2, 
                grid: { color: '#333' },
                ticks: { color: '#888' }
            },
            x: { 
                grid: { display: false },
                ticks: { 
                    color: '#888',
                    maxRotation: 0,
                    autoSkip: true,
                    maxTicksLimit: 10 
                }
            }
        },
        plugins: {
            legend: { display: false }
        }
    }
});

/**
 * Updates the chart using a sliding window logic
 */
function updateChart(timeline) {
    if (!timeline || Object.keys(timeline).length === 0) return;

    // Convert Dictionary to Arrays and extract HH:MM:SS
    const allLabels = Object.keys(timeline).map(t => t.split(' ')[1]); 
    const allValues = Object.values(timeline);

    // SLIDING WINDOW: Only show the last 50 data points
    const windowSize = 50;
    const labels = allLabels.slice(-windowSize);
    const values = allValues.slice(-windowSize);

    attentionChart.data.labels = labels;
    attentionChart.data.datasets[0].data = values;
    attentionChart.update('none'); 
}