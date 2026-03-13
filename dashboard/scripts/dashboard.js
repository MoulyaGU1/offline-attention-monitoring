// --- 1. GLOBAL STATE (Consolidated Declarations) ---
let sessionHistory = []; 
let timerInterval = null;
let isCameraOn = false;

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
                stateEl.style.color = "#ffcc00"; 
            } else {
                stateEl.innerText = (data.state || "STABLE").toUpperCase();
                stateEl.style.color = "#00ff88"; 
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
}

function updateNetworkStatus() {
    const dot = document.querySelector('.status-dot');
    const text = document.getElementById('offline-status');

    if (navigator.onLine) {
        text.innerText = "LOCAL NODE: ONLINE (SYNCED)";
        dot.style.background = "#3498db"; 
        dot.style.boxShadow = "0 0 10px #3498db";
    } else {
        text.innerText = "SECURE OFFLINE NODE (AIR-GAPPED)";
        dot.style.background = "#00ff88"; 
        dot.style.boxShadow = "0 0 10px #00ff88";
    }
}

/**
 * GRAVITY MAP RENDERER
 */
function updateGravityMap(gravityData) {
    const container = document.getElementById('gravity-list');
    if (!container) return;

    container.innerHTML = ''; 

    const totalUsage = Object.values(gravityData).reduce((a, b) => a + b, 0);
    const sortedApps = Object.entries(gravityData).sort((a, b) => b[1] - a[1]);

    sortedApps.forEach(([app, count]) => {
        const item = document.createElement('div');
        const gravityWidth = Math.min(count * 5, 100); 
        const usagePercentage = totalUsage > 0 ? ((count / totalUsage) * 100).toFixed(1) : 0;

        item.innerHTML = `
            <div class="gravity-item" style="margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 2px;">
                    <small style="font-weight: bold; color: #00ff88;">${app}</small>
                    <small style="color: #888;">${usagePercentage}% Focus</small>
                </div>
                <div class="offline-progress-bg" style="height: 6px; background: #222; border-radius: 3px; overflow: hidden;">
                    <div class="offline-progress-fill" style="width: ${gravityWidth}%; height: 100%; background: #00ff88; transition: width 0.3s;"></div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 2px;">
                    <small style="font-size: 10px; color: #555;">Pulls/Switches: ${count}</small>
                </div>
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

        if (report.timeline) {
            sessionHistory = report.timeline; // Assigned, not redeclared
            const slider = document.getElementById('replaySlider');
            slider.max = sessionHistory.length - 1;
            slider.value = 0; 
        }

        alert(`Session Ended Successfully!\nStability: ${report.stability_score || 'N/A'}`);
    } catch (err) {
        console.error("End session failed", err);
    }
}

// --- 3. INITIALIZE ---
document.getElementById('startBtn').addEventListener('click', startSession);
document.getElementById('endBtn').addEventListener('click', endSession);

updateNetworkStatus();

// Ensure this matches your end session button ID
document.getElementById('endBtn').onclick = async () => {
    const response = await fetch('/end-session', { method: 'POST' });
    const result = await response.json();
    if (result.status === 'stored') {
        alert("Session saved to local repository.");
        window.location.reload(); 
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
        const sessions = data.raw_history || data; 

        if (!body) return;
        body.innerHTML = ''; 

        body.innerHTML = sessions.map(row => {
            const startTime = row[1];
            const duration = Math.floor(row[3]) || 0;
            const jumps = row[7] || 0;
            const topApp = row[8] || "None";
            const intensity = parseFloat(row[9]) || 1.0;
            const idleTime = Math.floor(row[10]) || 0;

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

function renderGravityOffline(gravityData) {
    const container = document.getElementById('gravity-list');
    if (!container) return;

    container.innerHTML = ''; 
    const sortedApps = Object.entries(gravityData).sort((a, b) => b[1] - a[1]);

    sortedApps.forEach(([app, count]) => {
        const item = document.createElement('div');
        item.className = "gravity-item-container";
        const gravityWidth = Math.min(count * 5, 100); 

        item.innerHTML = `
            <div style="display:flex; justify-content:space-between; color:#00ff88; font-size:12px;">
                <span>${app}</span>
                <span>${count}</span>
            </div>
            <div style="height:2px; background:rgba(0,255,136,0.1); width:100%; margin:4px 0 12px 0;">
                <div style="height:100%; width:${gravityWidth}%; background:#00ff88; box-shadow:0 0 8px #00ff88;"></div>
            </div>
        `;
        container.appendChild(item);
    });
}

function updateChartOffline(timeline) {
    const labels = Object.keys(timeline).map(t => t.split(' ').pop()); 
    const values = Object.values(timeline);
    attentionChart.data.labels = labels.slice(-30);
    attentionChart.data.datasets[0].data = values.slice(-30);
    attentionChart.update('none'); 
}


function generateAttentionPattern() {
    if (!sessionHistory || sessionHistory.length === 0) return "Awaiting Pattern...";

    let pattern = [];
    let currentBlock = { state: null, startTime: 0 };

    sessionHistory.forEach((point, index) => {
        // Categorize the state
        let state = point.val > 0.7 ? "Focus" : point.val > 0.3 ? "Switch" : "Idle";

        if (state !== currentBlock.state) {
            // If the state changed, save the previous block
            if (currentBlock.state !== null) {
                let duration = index - currentBlock.startTime;
                // Only record blocks longer than 5 seconds to avoid "noise"
                if (duration > 5) {
                    pattern.push(`${currentBlock.state} ${Math.floor(duration / 60)}m ${duration % 60}s`);
                }
            }
            // Start a new block
            currentBlock = { state: state, startTime: index };
        }
    });

    // Add the final block
    let finalDuration = sessionHistory.length - currentBlock.startTime;
    pattern.push(`${currentBlock.state} ${Math.floor(finalDuration / 60)}m ${finalDuration % 60}s`);

    return pattern.join(" → ");
}
// Add this inside your endSession() function after you get the report
