let currentChart = null;

async function fetchAndRender(type = 'bar') {
    try {
        // Use the direct IP to bypass local DNS issues
        const response = await fetch('http://127.0.0.1:5000/api/history');
        const data = await response.json();
        
        console.log("Data loaded:", data); // Check your F12 console for this!

        if (!data.distribution || data.distribution.length === 0) {
            document.getElementById('patternTitle').innerText = "AWAITING SAVED SESSION DATA...";
            return;
        }

        const labels = data.distribution.map(item => item.app_name);
        const values = data.distribution.map(item => item.total_duration);
        
        const ctx = document.getElementById('mainAnalyticsChart').getContext('2d');
        if (currentChart) currentChart.destroy();

        currentChart = new Chart(ctx, {
            type: type,
            data: {
                labels: labels,
                datasets: [{
                    label: 'Attention (Seconds)',
                    data: values,
                    backgroundColor: ['#00ff88', '#00ccff', '#ffcc00', '#ff4444', '#9b59b6'],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: type === 'doughnut' ? {} : {
                    y: { beginAtZero: true, ticks: { color: '#888' } },
                    x: { ticks: { color: '#888' } }
                }
            }
        });
    } catch (err) {
        console.error("Fetch failed:", err);
    }
}
function switchPattern(pattern) {
    // UI Update
    document.querySelectorAll('.selector-btn').forEach(btn => btn.classList.remove('active'));
    
    // Safety check for the event target
    if (event && event.target) {
        event.target.classList.add('active');
    }
    
    const titles = {
        'bar': 'ATTENTION INTENSITY (TIME-BASED)',
        'doughnut': 'COGNITIVE DISTRIBUTION WHEEL',
        'line': 'ATTENTION FLOW PATHWAY'
    };
    document.getElementById('patternTitle').innerText = titles[pattern] || "ANALYSIS";
    
    fetchAndRender(pattern);
}

// Initial Load
window.onload = () => fetchAndRender('bar');