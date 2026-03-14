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

            // Mapping: r[7] = Total Switches (19), r[8] = App String, r[9] = Intensity
            const totalSwitches = s[7] || 0;
            const appString = s[8] || "System";
            const appList = appString.split('|').map(a => a.trim());
            
            const mainApp = appList[0];
            const distractions = appList.slice(1); // Actual named apps

            const intensity = parseFloat(s[9]) || 1.0;
            const riverWidth = Math.min(intensity * 20, 100); 

            const container = document.getElementById('river-container');
            container.innerHTML = `
                <div class="river-wrapper">
                    <div class="main-flow" style="height: ${riverWidth}px; width: 300px;">
                        <span class="node-label">${mainApp.split('-').pop()}</span>
                        
                        ${distractions.map((appName, i) => {
                            const angle = (i - (totalSwitches / 2)) * 20;
                            return `
                                <div class="leak-branch" style="width: 70px; transform: rotate(${angle}deg); border-top: 2px solid #ff0055;">
                                    <small style="position: absolute; right: -45px; color: #ff0055; font-size: 8px; transform: rotate(${-angle}deg);">
                                        ${appName.split('-').pop()}
                                    </small>
                                </div>`;
                        }).join('')}

                        ${generateRemainingLeaks(totalSwitches, distractions.length)}
                    </div>
                </div>
            `;
        });
}

function generateRemainingLeaks(total, namedCount) {
    let branches = '';
    const remaining = total - namedCount;
    if (remaining <= 0) return '';

    // Show up to 15 generic branches so it doesn't clutter the UI
    const toShow = Math.min(remaining, 15); 
    for (let i = 0; i < toShow; i++) {
        const angle = ((i + namedCount) - (total / 2)) * 20; 
        branches += `<div class="leak-branch" style="width: 40px; transform: rotate(${angle}deg); opacity: 0.4;"></div>`;
    }
    return branches;
}
let mainChart = null; // Global variable to track the chart instance

async function refreshVisuals(sessionId = 'all') {
    const response = await fetch(`/api/history?id=${sessionId}`);
    const data = await response.json();

    if (data.status === "success") {
        // 1. Update the Header (Shifts, Efficiency)
        document.getElementById('fragmentationCount').innerText = data.distribution.length;
        
        // 2. Render the Graph
        // If 'all', we show sessions. If specific ID, we show apps within that session.
        renderMainChart(data.distribution);

        // 3. Update Heatmap
        renderHeatmap(data.selected_session);
    }
}

function renderMainChart(distData) {
    const ctx = document.getElementById('mainAnalyticsChart').getContext('2d');

    // Prepare labels and values
    const labels = distData.map(d => d.app_name);
    const values = distData.map(d => d.total_duration);

    // CRITICAL: Destroy the old chart before creating a new one
    if (mainChart) {
        mainChart.destroy();
    }

    // Create the new chart
    mainChart = new Chart(ctx, {
        type: 'bar', // You can change this to 'line' or 'doughnut'
        data: {
            labels: labels,
            datasets: [{
                label: 'Attention Duration (Seconds)',
                data: values,
                backgroundColor: 'rgba(0, 255, 136, 0.2)',
                borderColor: '#00ff88',
                borderWidth: 2,
                borderRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 500 // Smooth transition when switching
            },
            scales: {
                y: { 
                    beginAtZero: true,
                    grid: { color: '#1a1a1a' },
                    ticks: { color: '#00ff88' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#888' }
                }
            }
        }
    });
}
// 1. Global variables to track chart instances
let barChart = null;
let wheelChart = null;
let flowChart = null;

async function refreshVisuals(sessionId = 'all') {
    const response = await fetch(`/api/history?id=${sessionId}`);
    const data = await response.json();

    if (data.status === "success") {
        // Clear all graphs and redraw with new data
        updateIntensityBars(data.distribution);
        updateDistributionWheel(data.distribution);
        updateAttentionFlow(data.selected_session);
        
        // Update the Heatmap image
        renderHeatmap(data.selected_session);
    }
}

/**
 * INTENSITY BARS
 */
function updateIntensityBars(distData) {
    const ctx = document.getElementById('mainAnalyticsChart').getContext('2d');
    
    // Destroy existing instance to force the switch
    if (barChart) barChart.destroy();

    barChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: distData.map(d => d.app_name),
            datasets: [{
                label: 'Duration (s)',
                data: distData.map(d => d.total_duration),
                backgroundColor: 'rgba(0, 255, 136, 0.2)',
                borderColor: '#00ff88',
                borderWidth: 2
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });
}

/**
 * DISTRIBUTION WHEEL
 */
function updateDistributionWheel(distData) {
    const ctx = document.getElementById('wheelChartCanvas').getContext('2d');
    
    if (wheelChart) wheelChart.destroy();

    wheelChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: distData.map(d => d.app_name),
            datasets: [{
                data: distData.map(d => d.total_duration),
                backgroundColor: ['#00ff88', '#00ccff', '#ffcc00', '#ff0055']
            }]
        }
    });
}
// 1. Initialize the Heatmap Canvas (Memory-only)
const heatmapCanvas = document.createElement('canvas');
heatmapCanvas.width = window.screen.width;
heatmapCanvas.height = window.screen.height;
const hCtx = heatmapCanvas.getContext('2d');

/**
 * CAPTURE HEAT: Call this inside your mouse move/click listeners
 */
function recordInteraction(x, y, intensity = 0.2) {
    // Create a radial gradient (the 'heat' circle)
    const gradient = hCtx.createRadialGradient(x, y, 0, x, y, 30);
    gradient.addColorStop(0, `rgba(0, 255, 136, ${intensity})`); // Matrix Green
    gradient.addColorStop(1, 'rgba(0, 255, 136, 0)');

    hCtx.fillStyle = gradient;
    hCtx.fillRect(x - 30, y - 30, 60, 60);
}

/**
 * SAVE HEATMAP: Call this when 'End Session' is clicked
 */
async function finalizeHeatmap(sessionId) {
    return new Promise((resolve) => {
        heatmapCanvas.toBlob(async (blob) => {
            const formData = new FormData();
            formData.append('image', blob);
            formData.append('session_id', sessionId);

            const response = await fetch('/api/store_heatmap_blob', {
                method: 'POST',
                body: formData
            });
            resolve(await response.json());
        }, 'image/png');
    });
}
function renderHeatmap(sessionData) {
    const canvas = document.getElementById('heatmapRiverChart');
    const ctx = canvas.getContext('2d');

    if (sessionData && sessionData.heatmap_url) {
        const img = new Image();
        img.onload = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            // Apply a high-contrast filter to make it look like a thermal map
            ctx.filter = 'contrast(1.5) brightness(1.2) hue-rotate(180deg)'; 
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            ctx.filter = 'none';
        };
        img.src = sessionData.heatmap_url;
    }
}
// Hidden canvas to store the 'heat' data during the session
const persistenceCanvas = document.createElement('canvas');
persistenceCanvas.width = window.innerWidth;
persistenceCanvas.height = window.innerHeight;
const pCtx = persistenceCanvas.getContext('2d');

/**
 * Record a 'Heat Point'
 * @param {number} x - Mouse X coordinate
 * @param {number} y - Mouse Y coordinate
 * @param {string} type - 'move' or 'click'
 */
function recordInteraction(x, y, type = 'move') {
    const radius = type === 'click' ? 40 : 25; // Clicks create larger heat spots
    const intensity = type === 'click' ? 0.4 : 0.15; // Clicks are 'hotter'
    
    const gradient = pCtx.createRadialGradient(x, y, 0, x, y, radius);
    gradient.addColorStop(0, `rgba(0, 255, 136, ${intensity})`); // Matrix Green
    gradient.addColorStop(1, 'rgba(0, 255, 136, 0)');

    pCtx.fillStyle = gradient;
    pCtx.globalCompositeOperation = 'screen'; // Layers colors to increase 'heat'
    pCtx.beginPath();
    pCtx.arc(x, y, radius, 0, Math.PI * 2);
    pCtx.fill();
}
async function saveInteractionHeatmap(sessionId) {
    return new Promise((resolve) => {
        persistenceCanvas.toBlob(async (blob) => {
            const formData = new FormData();
            formData.append('image', blob);
            formData.append('session_id', sessionId);

            const res = await fetch('/api/store_heatmap_blob', {
                method: 'POST',
                body: formData
            });
            resolve(await res.json());
        }, 'image/png');
    });
}
function displayInteractionHeatmap(sessionData) {
    const canvas = document.getElementById('heatmapRiverChart');
    const ctx = canvas.getContext('2d');

    if (sessionData && sessionData.heatmap_url) {
        const img = new Image();
        img.onload = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Apply thermal-style filters
            ctx.filter = 'contrast(150%) brightness(120%) saturate(200%)';
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            ctx.filter = 'none'; // Reset for other drawings
        };
        img.src = sessionData.heatmap_url;
    }
}
let myChartInstance = null; // Track the chart to allow destroying it

async function updateSessionId() {
    const id = document.getElementById('sessionPicker').value;
    const response = await fetch(`/api/history?id=${id}`);
    const data = await response.json();

    if (data.status === "success" && data.selected_session) {
        const session = data.selected_session;

        // 1. FIX THE HEATMAP
        const canvas = document.getElementById('heatmapRiverChart');
        const ctx = canvas.getContext('2d');
        if (session.heatmap_url) {
            const img = new Image();
            img.onload = () => {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            };
            img.src = session.heatmap_url;
        }

        // 2. FIX THE CHART REFRESH
        const chartCtx = document.getElementById('mainAnalyticsChart').getContext('2d');
        if (myChartInstance) myChartInstance.destroy(); // Remove old data

        myChartInstance = new Chart(chartCtx, {
            type: 'line', // or 'bar'
            data: {
                labels: ["Start", "Q1", "Mid", "Q3", "End"], // Define your X-Axis segments
                datasets: [{
                    label: 'Attention Intensity (Seconds)',
                    data: [5, 10, 15, session.duration, 0], // Map your data points here
                    borderColor: '#00ff88',
                    tension: 0.4
                }]
            }
        });
    }
}