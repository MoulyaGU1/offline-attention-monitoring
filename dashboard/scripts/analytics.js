let currentChart = null;
let selectedSessionId = 'all'; 

async function fetchAndRender(type = 'bar') {
    try {
        const response = await fetch(`http://127.0.0.1:5000/api/history?id=${selectedSessionId}`);
        const data = await response.json();
        
        // 1. Update Dropdown List
        const picker = document.getElementById('sessionPicker');
        if (picker && data.session_list) {
            const currentVal = picker.value;
            picker.innerHTML = '<option value="all">ALL-TIME OVERVIEW</option>';
            data.session_list.forEach(s => {
                const opt = document.createElement('option');
                opt.value = s.id;
                opt.innerText = `Session #${s.id} - ${s.time.split(' ')[1]}`;
                picker.appendChild(opt);
            });
            picker.value = currentVal;
        }

        const titleEl = document.getElementById('patternTitle');
        let labels, values;

        // --- THE FIX: SWITCHING LOGIC ---
        if (selectedSessionId === 'all') {
            titleEl.innerText = "ALL-TIME ATTENTION TOPOLOGY";
            // Show Apps vs Time (Overview)
            labels = data.distribution.map(item => item.app_name);
            values = data.distribution.map(item => item.total_duration);
        } else {
            titleEl.innerText = `FULL SESSION METRICS: ID #${selectedSessionId}`;
            
            // Get the specific 11-column row for this ID from raw_history
            const sessionRow = data.raw_history.find(r => r[0] == selectedSessionId);
            
            if (sessionRow) {
                // Map the exact SQLite columns to the bars
                // Index mapping: 3=Duration, 4=Keys, 5=Clicks, 7=Switches, 10=Idle
                labels = ['Total Time (s)', 'Keys', 'Clicks', 'Switches', 'Idle (s)'];
                values = [
                    sessionRow[3], // duration
                    sessionRow[4], // keyboard
                    sessionRow[5], // mouse
                    sessionRow[7], // app_switches
                    sessionRow[10] // idle_time
                ];
            }
        }

        if (!values || values.length === 0) return;

        const ctx = document.getElementById('mainAnalyticsChart').getContext('2d');
        if (currentChart) currentChart.destroy();

        const matrixColors = ['#00ff88', '#00e5ff', '#ffcc00', '#ff0055', '#9d00ff'];

        currentChart = new Chart(ctx, {
            type: type,
            data: {
                labels: labels,
                datasets: [{
                    label: selectedSessionId === 'all' ? 'Seconds' : 'Activity Count',
                    data: values,
                    backgroundColor: matrixColors,
                    borderColor: '#00ff88',
                    borderWidth: 2,
                    borderRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: type === 'doughnut' ? {} : {
                    y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#888' } },
                    x: { ticks: { color: '#00ff88', font: { weight: 'bold' } } }
                }
            }
        });
    } catch (err) { console.error("Update Error:", err); }
}

function updateSessionId() {
    selectedSessionId = document.getElementById('sessionPicker').value;
    // Force refresh with currently active button type
    const activeBtn = document.querySelector('.selector-btn.active');
    const type = activeBtn ? (activeBtn.innerText.toLowerCase().includes('wheel') ? 'doughnut' : 'bar') : 'bar';
    fetchAndRender(type);
}

function switchPattern(pattern) {
    document.querySelectorAll('.selector-btn').forEach(btn => btn.classList.remove('active'));
    if (event && event.currentTarget) event.currentTarget.classList.add('active');
    fetchAndRender(pattern);
}

window.onload = () => fetchAndRender('bar');