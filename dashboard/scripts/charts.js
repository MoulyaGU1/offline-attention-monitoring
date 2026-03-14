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
/**
 * Updates the chart using a sliding window logic.
 * Handles both "2026-03-08 17:31:05" and "17:31:05" formats.
 */
/**
 * Updates the topology chart using a sliding window.
 * Handles both "ISO Date Time" and "HH:MM:SS" formats safely.
 */
function updateChart(timeline) {
    if (!timeline || Object.keys(timeline).length === 0) return;

    // Safe Label Extraction: handles "2026-03-08 17:42:01" vs "17:42:01"
    const labels = Object.keys(timeline).map(t => {
        return t.includes(' ') ? t.split(' ')[1] : t;
    }); 
    
    const values = Object.values(timeline);

    // Only show the last 35 points to keep the waveform clear
    const windowSize = 35;
    attentionChart.data.labels = labels.slice(-windowSize);
    attentionChart.data.datasets[0].data = values.slice(-windowSize);

    // Update with 'none' to skip internal re-calculations for speed
    attentionChart.update('none'); 
}
async function renderCharts() {
    const response = await fetch('http://localhost:5000/api/data');
    const data = await response.json();

    const labels = data.distribution.map(item => item.app_name);
    const values = data.distribution.map(item => item.count);

    const ctx = document.getElementById('attentionChart').getContext('2d');
    
    // Default Chart: Bar Graph (as per your request)
    let chartType = 'bar'; 

    let myChart = new Chart(ctx, {
        type: chartType,
        data: {
            labels: labels,
            datasets: [{
                label: 'Attention Intensity (Seconds)',
                data: values,
                backgroundColor: ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });

    // Function to switch patterns dynamically
    window.updateChartPattern = function(newType) {
        myChart.destroy();
        myChart = new Chart(ctx, {
            type: newType, // 'bar', 'doughnut' (Radial), or 'line'
            data: {
                labels: labels,
                datasets: [{
                    label: 'Attention Distribution',
                    data: values,
                    backgroundColor: ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e']
                }]
            }
        });
    };
}

renderCharts();
function renderHeatmap(sessionData) {
    const container = document.querySelector('.interaction-density-heatmap');
    if (sessionData && sessionData.heatmap_url) {
        container.innerHTML = `<img src="${sessionData.heatmap_url}" style="width:100%; height:100%; object-fit:contain; border: 1px solid #00ff88; box-shadow: 0 0 15px rgba(0,255,136,0.2);">`;
    } else {
        container.innerHTML = `<p style="color:#444; padding-top:100px; text-align:center;">No heatmap recorded for this session.</p>`;
    }
}