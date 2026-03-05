let timerInterval;
let startTime;

async function startSession() {
    const response = await fetch('/start-session', { method: 'POST' });
    const result = await response.json();
    
    if (result.status === "session_started") {
        startTime = Date.now();
        timerInterval = setInterval(updateDashboard, 1000);
        document.getElementById('startBtn').disabled = true;
    }
}

async function updateDashboard() {
    try {
        const response = await fetch('/status');
        const data = await response.json();

        if (data.status === 'inactive') return;

        // Update Counter Cards
        document.getElementById('keyboard').innerText = data.keyboard_events;
        document.getElementById('mouseMoves').innerText = data.mouse_moves;
        document.getElementById('mouseClicks').innerText = data.mouse_clicks;
        document.getElementById('appSwitch').innerText = data.app_switches;
        
        // Update Timer
        document.getElementById('sessionTime').innerText = Math.floor(data.duration);

        // Update Patterns Raw Display
        document.getElementById('patterns').innerText = JSON.stringify(data.patterns, null, 2);

        // Update the Chart (Calling function from charts.js)
        updateChart(data.timeline);

    } catch (err) {
        console.error("Dashboard Sync Error:", err);
    }
}

async function endSession() {
    clearInterval(timerInterval);
    const response = await fetch('/end-session', { method: 'POST' });
    const report = await response.json();
    console.log("Final Session Report:", report);
    document.getElementById('startBtn').disabled = false;
    alert("Session Ended. Check console for final report.");
}

document.getElementById('startBtn').addEventListener('click', startSession);
document.getElementById('endBtn').addEventListener('click', endSession);