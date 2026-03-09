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
            // 1. Timer
            const totalSeconds = Math.floor(data.duration || 0);
            const mins = Math.floor(totalSeconds / 60).toString().padStart(2, '0');
            const secs = Math.floor(totalSeconds % 60).toString().padStart(2, '0');
            document.getElementById('sessionTime').innerText = `${mins}:${secs}`;

            // 2. Hardware Stats
            document.getElementById('keyboard').innerText = data.keyboard_events || 0;
            document.getElementById('mouseClicks').innerText = data.mouse_clicks || 0;
            document.getElementById('mouseMoves').innerText = Math.floor(data.mouse_moves || 0).toLocaleString();

            // 3. Separate Card: App Jumps & Alt+Tabs
            const appVal = document.getElementById('appSwitchVal');
            const tabVal = document.getElementById('tabSwitchVal');
            
            if (appVal) appVal.innerText = data.app_switches || 0;
            if (tabVal) tabVal.innerText = data.tab_switches || 0;

            // 4. Topology (Graph) & Gravity (Bars)
            if (window.updateChart && data.timeline) {
                // DEBUG: If your graph is blank, check if this appears in Console (F12)
                console.log("Pushing to Topology:", data.timeline); 
                updateChart(data.timeline);
            }
            
            if (window.updateGravityMap && data.gravity_map) {
                updateGravityMap(data.gravity_map);
            }

            // 5. Neuro-State
            document.getElementById('focusState').innerText = (data.state || "STABLE").toUpperCase();
        }
    } catch (err) {
        console.log("Waiting for backend...");
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
    const response = await fetch('/api/history');
    const data = await response.json();
    const body = document.getElementById('historyBody');
    
    body.innerHTML = data.map(row => {
        const intensity = parseFloat(row[4]) || 1.0;
        
        // Generate bars representing the Attention Topology
        let barsHtml = '';
        for (let i = 0; i < 10; i++) {
            const height = Math.min(Math.max((Math.random() * 0.4 + (intensity - 0.2)) * 20, 5), 30);
            barsHtml += `<div class="attention-bar" style="height: ${height}px;"></div>`;
        }

        return `
            <tr>
                <td>${row[0]}</td> <td>${Math.floor(row[1])}s</td> <td>${row[2]}</td> <td><span class="focus-app-name" title="${row[3]}">${row[3]}</span></td>
                <td><div class="bar-graph-container">${barsHtml}</div></td>
                <td style="color: #00ff88; font-weight: bold;">${intensity.toFixed(2)}x</td>
            </tr>
        `;
    }).join('');
}