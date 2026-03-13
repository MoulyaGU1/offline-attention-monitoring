/**
 * THE ATTENTION BRIDGE: 
 * This script intercepts the existing 'sessionHistory' and 'data' 
 * to calculate DNA without modifying the original source files.
 */

// We use an interval to check for changes every second
setInterval(() => {
    // Check if the session is active and we have history
    if (typeof sessionHistory !== 'undefined' && sessionHistory.length > 0) {
        
        // 1. GENERATE DNA SIGNATURE
        let pattern = [];
        let currentBlock = { state: null, count: 0 };
        let focusPoints = 0;

        sessionHistory.forEach((point) => {
            let val = point.val || 0;
            let state = val >= 0.8 ? "Focus" : val >= 0.3 ? "Switch" : "Idle";
            
            if (val >= 0.8) focusPoints++;

            if (state === currentBlock.state) {
                currentBlock.count++;
            } else {
                if (currentBlock.state) {
                    pattern.push(`${currentBlock.state} (${currentBlock.count}s)`);
                }
                currentBlock = { state: state, count: 1 };
            }
        });
        pattern.push(`${currentBlock.state} (${currentBlock.count}s)`);

        // 2. UPDATE UI
        const patternEl = document.getElementById('patternText');
        const effEl = document.getElementById('dnaEfficiency');
        const typeEl = document.getElementById('dnaType');

        if (patternEl) patternEl.innerText = pattern.join(" ➔ ");
        
        if (effEl) {
            let efficiency = Math.round((focusPoints / sessionHistory.length) * 100);
            effEl.innerText = efficiency + "%";
        }

        if (typeEl) {
            const lastVal = sessionHistory[sessionHistory.length - 1].val;
            typeEl.innerText = lastVal >= 0.8 ? "DEEP FLOW" : (lastVal >= 0.3 ? "SWITCHING" : "DRIFTING");
        }
    }
}, 1000);