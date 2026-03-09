// --- 1. GLOBAL STATE ---
let timerInterval = null;

/**
 * THE MASTER HEARTBEAT: Updates data and network status
 */
async function updateDashboard() {
    try {
        const response = await fetch('/status');
        const data = await response.json();

        if (data.status === 'active') {
            // 1. Timer logic
            const totalSeconds = Math.floor(data.duration || 0);
            const mins = Math.floor(totalSeconds / 60).toString().padStart(2, '0');
            const secs = Math.floor(totalSeconds % 60).toString().padStart(2, '0');
            document.getElementById('sessionTime').innerText = `${mins}:${secs}`;

            // 2. Hardware Stats update
            document.getElementById('keyboard').innerText = data.keyboard_events || 0;
            document.getElementById('mouseClicks').innerText = data.mouse_clicks || 0;
            document.getElementById('mouseMoves').innerText = Math.floor(data.mouse_moves || 0).toLocaleString();

            // 3. App Jumps & Alt+Tabs
            const appVal = document.getElementById('appSwitchVal');
            const tabVal = document.getElementById('tabSwitchVal');
            if (appVal) appVal.innerText = data.app_switches || 0;
            if (tabVal) tabVal.innerText = data.tab_switches || 0;

            // 4. Topology (Graph) & Gravity (Bars)
            if (window.updateChart && data.timeline) {
                updateChart(data.timeline);
            }
            if (window.updateGravityMap && data.gravity_map) {
                updateGravityMap(data.gravity_map);
            }

            // 5. Neuro-State & Idle Detection
            const stateEl = document.getElementById('focusState');
            if (data.is_idle) {
                stateEl.innerText = "IDLE / BREAK";
                stateEl.style.color = "#ffcc00"; // Alert Yellow for inactivity
            } else {
                stateEl.innerText = (data.state || "STABLE").toUpperCase();
                stateEl.style.color = "#00ff88"; // Standard Matrix Green
            }

            // 6. Zero-Cloud Compliance Real-time Check
            const statusText = document.getElementById('node-status');
            const statusDot = document.querySelector('.status-dot');

            if (navigator.onLine) {
                statusText.innerText = "LOCAL NODE: SYNCED TO DISK";
                statusDot.style.background = "#3498db"; 
                statusDot.style.boxShadow = "0 0 10px #3498db";
            } else {
                statusText.innerText = "SECURE OFFLINE NODE (AIR-GAPPED)";
                statusDot.style.background = "#00ff88"; 
                statusDot.style.boxShadow = "0 0 15px #00ff88";
            }
        }
    } catch (err) {
        console.log("Waiting for local backend on 127.0.0.1...");
    }
}function updateNetworkStatus() {
    const dot = document.querySelector('.status-dot');
    const text = document.getElementById('offline-status');

    if (navigator.onLine) {
        text.innerText = "LOCAL NODE: ONLINE (SYNCED)";
        dot.style.background = "#3498db"; // Blue
        dot.style.boxShadow = "0 0 10px #3498db";
    } else {
        text.innerText = "SECURE OFFLINE NODE (AIR-GAPPED)";
        dot.style.background = "#00ff88"; // Green
        dot.style.boxShadow = "0 0 10px #00ff88";
    }
}

/**
 * GRAVITY MAP RENDERER
 */
function updateGravityMap(gravityData) {
    const container = document.getElementById('gravity-list');
    if (!container) return;

    container.innerHTML = ''; // Clear old bars

    // Convert to array and sort by most used app
    const sortedApps = Object.entries(gravityData).sort((a, b) => b[1] - a[1]);

    sortedApps.forEach(([app, count]) => {
        const item = document.createElement('div');
        item.style.marginBottom = "10px";
        item.innerHTML = `
            <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                <small>${app}</small>
                <small>${count}</small>
            </div>
            <div style="height:4px; background:rgba(255,255,255,0.1); border-radius:2px;">
                <div style="height:100%; width:${Math.min(count * 5, 100)}%; background:#00ff88; box-shadow: 0 0 10px #00ff88;"></div>
            </div>
        `;
        container.appendChild(item);
    });
}

// --- 2. SESSION CONTROLS ---
async function startSession() {
    const response = await fetch('/start-session', { method: 'POST' });
    const result = await response.json();
    
    if (result.status === "session_started") {
        document.getElementById('startBtn').disabled = true;
        document.getElementById('startBtn').innerText = "TRACKING...";
        // Only one interval to prevent lag
        if (!timerInterval) timerInterval = setInterval(updateDashboard, 1000);
    }
}

async function endSession() {
    if (timerInterval) { clearInterval(timerInterval); timerInterval = null; }
    
    try {
        const response = await fetch('/end-session', { method: 'POST' });
        const report = await response.json();
        
        document.getElementById('startBtn').disabled = false;
        document.getElementById('startBtn').innerText = "START SESSION";
        document.getElementById('focusState').innerText = "COMPLETE";
        alert(`Session Ended Successfully!\nStability: ${report.stability_score || 'N/A'}`);
    } catch (err) {
        console.error("End session failed", err);
    }
}

// --- 3. INITIALIZE ---
document.getElementById('startBtn').addEventListener('click', startSession);
document.getElementById('endBtn').addEventListener('click', endSession);

// Run network check immediately on load
updateNetworkStatus();
// Inside your updateDashboard loop:
if (data.status === 'active') {
    // 1. Draw the Topology Line
    if (window.updateChart && data.timeline) {
        updateChart(data.timeline);
    }
    
    // 2. Draw the Gravity Bars
    if (window.updateGravityMap && data.gravity_map) {
        updateGravityMap(data.gravity_map);
    }
}
// Ensure this matches your end session button ID
document.getElementById('endBtn').onclick = async () => {
    const response = await fetch('/end-session', { method: 'POST' });
    const result = await response.json();
    if (result.status === 'stored') {
        alert("Session saved to local repository.");
        window.location.reload(); // Force refresh to show empty dashboard
    }
};
function toggleMenu() {
    const menu = document.getElementById("sideMenu");
    menu.classList.toggle("open");
}
async function loadHistory() {
    try {
        const response = await fetch('/api/history');
        const data = await response.json();
        const body = document.getElementById('historyBody');
        
        body.innerHTML = data.map(row => {
            // MATCH THESE TO YOUR SQL COLUMNS
            const startTime = row[1];
            const duration = Math.floor(row[3]) || 0;
            const jumps = row[7] || 0;
            const topApp = row[8] || "None";
            const intensity = parseFloat(row[9]) || 1.0;
            const idleTime = Math.floor(row[10]) || 0; // NEW COLUMN AT INDEX 10

            return `
                <tr>
                    <td>${startTime}</td>
                    <td>${duration}s</td>
                    <td style="color: #ffcc00; font-weight: bold;">${idleTime}s</td>
                    <td>${jumps}</td>
                    <td><span class="focus-app-name">${topApp}</span></td>
                    <td><div class="bar-graph-container">${generateTopologyBars(intensity)}</div></td>
                    <td style="color: #00ff88;">${intensity.toFixed(2)}x</td>
                </tr>
            `;
        }).join('');
    } catch (err) {
        console.error("History Load Error:", err);
    }
}