/**
 * GLOBAL VARIABLES
 */
let mainChart = null;     // Handles Bar, Pie, and Line
let heatmapChart = null;  // Dedicated instance for the Heatmap River
let selectedId = 'all';

/**
 * 1. THE TRIGGER: This function must be linked to your HTML:
 * <select id="sessionPicker" onchange="updateSessionId()">
 */
async function updateSessionId() {
    const picker = document.getElementById('sessionPicker');
    
    // CRITICAL FIX: Ensure we only take the string/number value, not an object
    selectedId = picker.value; 

    console.log("Switching to Session ID:", selectedId);

    // Detect current pattern to keep UI consistent
    const activeBtn = document.querySelector('.selector-btn.active');
    const modeText = activeBtn ? activeBtn.innerText.toLowerCase() : 'bar';
    
    let type = 'bar';
    if (modeText.includes('wheel')) type = 'doughnut';
    if (modeText.includes('flow')) type = 'line';

    // Call the fetch function with the CLEAN ID
    await fetchAndSynchronize(type);
}

/**
 * 2. MASTER DATA SYNC
 */
async function fetchAndSynchronize(chartType) {
    try {
        const response = await fetch(`/api/history?id=${selectedId}`);
        const data = await response.json();

        // --- DROPDOWN POPULATION FIX ---
        const picker = document.getElementById('sessionPicker');
        if (picker && data.session_list) {
            // Only rebuild the list if it's empty (prevents flickering)
            if (picker.options.length <= 1) { 
                picker.innerHTML = '<option value="all">ALL-TIME OVERVIEW</option>';
                data.session_list.forEach(s => {
                    const opt = document.createElement('option');
                    opt.value = s.id;
                    opt.innerText = `Session #${s.id} - ${s.time.split(' ')[1]}`;
                    picker.appendChild(opt);
                });
                // Maintain the current selection
                picker.value = selectedId;
            }
        }

        // Proceed with rendering charts...
        updateHeaderStats(data);
        renderHeatmap(data.formatted_history);
        renderMainGraph(data, chartType);

    } catch (err) {
        console.error("Sync Error:", err);
    }
}

/**
 * 3. HEATMAP RIVER (Interaction Density)
 */
// Global instance tracker
let heatmapChartInstance = null;

async function renderHeatmap(sessionId) {
    const canvas = document.getElementById('heatmapRiverChart');
    
    // Safety Check: If the canvas doesn't exist yet, stop execution
    if (!canvas) {
        console.error("Heatmap Canvas 'heatmapRiverChart' not found in HTML!");
        return;
    }

    const ctx = canvas.getContext('2d');

    try {
        const response = await fetch(`/api/history?id=${sessionId}`);
        const data = await response.json();

        // Map the interaction density from the backend
        const displayData = [...data.formatted_history].reverse();
        const labels = displayData.map(item => item.time);
        const values = displayData.map(item => item.interaction_density);
        const colors = displayData.map(item => {
            if (item.attention_state === "FRAGMENTED") return '#ff0055';
            if (item.attention_state === "IDLE") return '#222222';
            return '#00ff88';
        });

        // 🛠️ THE FIX: Clear old data properly
        if (heatmapChartInstance) {
            heatmapChartInstance.destroy();
        }

        // Create new Chart instance
        heatmapChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: colors,
                    borderRadius: 2,
                    barPercentage: 0.9
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { display: true, ticks: { color: '#444', font: { size: 8 } }, grid: { display: false } },
                    y: { beginAtZero: true, grid: { color: '#111' }, ticks: { display: false } }
                },
                plugins: { legend: { display: false } }
            }
        });

    } catch (error) {
        console.error("Critical Heatmap Render Error:", error);
    }
}

/**
 * 4. MAIN TOPOLOGY GRAPH (Bar / Pie / Distributed Line)
 */
function renderMainGraph(data, type) {
    const ctx = document.getElementById('mainAnalyticsChart').getContext('2d');
    const titleEl = document.getElementById('patternTitle');
    
    let labels, values, labelTag;

    if (selectedId === 'all') {
        titleEl.innerText = "ALL-TIME ATTENTION TOPOLOGY";
        labels = data.distribution.map(item => item.app_name);
        values = data.distribution.map(item => item.total_duration);
        labelTag = 'Seconds Spent';
    } else {
        titleEl.innerText = `SESSION METRICS: ID #${selectedId}`;
        const session = data.raw_history.find(r => r[0] == selectedId);
        if (session) {
            labels = ['Total Time', 'Keyboard', 'Clicks', 'App Jumps', 'Idle Time'];
            values = [session[3], session[4], session[5], session[7], session[10]];
            labelTag = 'Activity Units';
        }
    }

    if (mainChart) mainChart.destroy();

    const colors = ['#00ff88', '#00d4ff', '#ff0055', '#7d2ae8', '#ffcc00'];

    mainChart = new Chart(ctx, {
        type: type,
        data: {
            labels: labels,
            datasets: [{
                label: labelTag,
                data: values,
                backgroundColor: type === 'line' ? 'transparent' : colors,
                borderColor: '#00ff88',
                borderWidth: 2,
                pointBackgroundColor: '#00ff88',
                tension: 0.4, // Smooths the 'Attention Flow' line
                fill: type === 'line'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: type === 'doughnut', position: 'bottom' } },
            scales: type === 'doughnut' ? {} : {
                x: { ticks: { color: '#00ff88' }, grid: { display: false } },
                y: { beginAtZero: true, grid: { color: '#111' }, ticks: { color: '#555' } }
            }
        }
    });
}

/**
 * 5. HEADER STATS (Fragmentation Index)
 */
function updateHeaderStats(data) {
    const history = data.formatted_history;
    const totalShifts = history.reduce((acc, curr) => acc + (curr.fragmentation_index || 0), 0);
    
    const shiftEl = document.getElementById('fragmentationCount');
    const stateEl = document.getElementById('attentionState');

    if (shiftEl) {
        shiftEl.innerText = totalShifts;
        shiftEl.style.color = totalShifts > 5 ? '#ff0055' : '#00ff88';
    }
    if (stateEl) {
        stateEl.innerText = totalShifts > 5 ? "FRAGMENTED" : "DEEP FOCUS";
    }
}

/**
 * 6. PATTERN SWITCHER
 */
function switchPattern(pattern) {
    document.querySelectorAll('.selector-btn').forEach(btn => btn.classList.remove('active'));
    if (event && event.currentTarget) event.currentTarget.classList.add('active');
    
    let chartType = 'bar';
    if (pattern === 'doughnut') chartType = 'doughnut';
    if (pattern === 'line') chartType = 'line';

    fetchAndSynchronize(chartType);
}

// Initial Load
window.onload = () => fetchAndSynchronize('bar');
