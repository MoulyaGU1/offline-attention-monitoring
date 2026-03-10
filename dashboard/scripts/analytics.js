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
    // 1. Capture the ID from the dropdown
    const picker = document.getElementById('sessionPicker');
    selectedSessionId = picker.value;
    
    // 2. Refresh the Main Chart (Bars/Line/Wheel)
    // Detect which mode is active to keep the right chart type
    const activeBtn = document.querySelector('.selector-btn.active');
    const text = activeBtn ? activeBtn.innerText.toLowerCase() : 'bars';
    let type = text.includes('wheel') ? 'doughnut' : (text.includes('flow') ? 'line' : 'bar');
    
    fetchAndRender(type);

    // 3. TRIGGER THE RIVER (The missing part)
    const riverContainer = document.getElementById('river-container');
    if (selectedSessionId !== 'all') {
        updateAttentionRiver(selectedSessionId);
    } else {
        riverContainer.innerHTML = '<span style="color: #333;">Select a session to visualize flow...</span>';
    }
}

function switchPattern(pattern) {
    document.querySelectorAll('.selector-btn').forEach(btn => btn.classList.remove('active'));
    if (event && event.currentTarget) event.currentTarget.classList.add('active');
    fetchAndRender(pattern);
}

window.onload = () => fetchAndRender('bar');
// --- ATTENTION RIVER LOGIC ---
function updateAttentionRiver(sessionId) {
    fetch(`/api/history?id=${sessionId}`)
        .then(res => res.json())
        .then(data => {
            const s = data.raw_history.find(r => r[0] == sessionId);
            if (!s) return;

            // 1. Split the stored apps by the pipe '|' character
            const appString = s[8] || "System";
            const appList = appString.split('|').map(a => a.trim());
            
            // 2. The first app is the "Main Channel", others are "Branches"
            const mainApp = appList[0];
            const distractions = appList.slice(1); // Everything else

            const intensity = parseFloat(s[9]) || 1.0;
            const riverWidth = Math.min(intensity * 20, 100); 

            const container = document.getElementById('river-container');
            container.innerHTML = `
                <div class="river-wrapper">
                    <div class="main-flow" style="height: ${riverWidth}px; width: 300px;">
                        <span class="node-label">${mainApp.split('-').pop()}</span>
                        
                        ${distractions.map((appName, i) => {
                            const angle = (i - (distractions.length / 2)) * 30;
                            return `
                                <div class="leak-branch" style="width: 60px; transform: rotate(${angle}deg);">
                                    <small style="position: absolute; right: -40px; color: #ff0055; font-size: 8px; transform: rotate(${-angle}deg);">
                                        ${appName.split('-').pop()}
                                    </small>
                                </div>`;
                        }).join('')}
                    </div>
                </div>
            `;
        });
}

function generateBranches(count) {
    let branches = '';
    const maxDisplayed = Math.min(count, 10); 
    for (let i = 0; i < maxDisplayed; i++) {
        const angle = (i - (maxDisplayed / 2)) * 30; 
        branches += `<div class="leak-branch" style="width: 50px; transform: rotate(${angle}deg);"></div>`;
    }
    return branches;
}