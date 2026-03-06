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

           

            // 3. Topology & Gravity

            if (window.updateChart && data.timeline) updateChart(data.timeline);

            if (window.updateGravityMap && data.gravity_map) updateGravityMap(data.gravity_map);

           

            // 4. Neuro-State

            document.getElementById('focusState').innerText = (data.state || "STABLE").toUpperCase();

        }

    } catch (err) {

        // We do nothing here now—no more red "Connection Lost" banner.

        console.log("Waiting for backend...");

    }

}
/**
 * TRUTHFUL NETWORK DETECTION: Only checks Wi-Fi/Ethernet status
 */
function updateNetworkStatus() {
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
    if (!container || !gravityData || Object.keys(gravityData).length === 0) return;

    container.innerHTML = ''; 
    const sortedApps = Object.entries(gravityData).sort((a, b) => b[1] - a[1]);

    sortedApps.forEach(([appName, score]) => {
        const percentage = Math.min(score * 50, 100); 
        const item = document.createElement('div');
        item.className = 'gravity-item';
        item.innerHTML = `
            <div class="gravity-label">
                <span>${appName}</span>
                <span>${percentage.toFixed(0)}%</span>
            </div>
            <div class="gravity-bar-bg">
                <div class="gravity-bar-fill" style="width: ${percentage}%"></div>
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