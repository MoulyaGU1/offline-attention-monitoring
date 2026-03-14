/**
 * THE ATTENTION BRIDGE: 
 * Translates raw intensity values into a readable "Attention DNA" stream.
 */

setInterval(() => {
    // We look for 'timeline' data from our API response
    // If you are on the Analytics page, this is usually 'data.distribution' or 'sessionHistory'
    if (typeof sessionHistory !== 'undefined' && sessionHistory.length > 0) {
        
        let pattern = [];
        let currentBlock = { state: null, count: 0 };
        let focusPoints = 0;

        // 1. GENERATE DNA SIGNATURE (Pattern Mapping)
        sessionHistory.forEach((point) => {
            let val = point.val || 0;
            let state = val >= 0.8 ? "Focus" : (val >= 0.3 ? "Switch" : "Idle");
            
            if (val >= 0.8) focusPoints++;

            if (state === currentBlock.state) {
                currentBlock.count++;
            } else {
                if (currentBlock.state) {
                    // Create a styled HTML span for the DNA node
                    pattern.push(`<span class="dna-node ${currentBlock.state.toLowerCase()}">${currentBlock.state} (${currentBlock.count}s)</span>`);
                }
                currentBlock = { state: state, count: 1 };
            }
        });
        
        // Push the final block
        pattern.push(`<span class="dna-node ${currentBlock.state.toLowerCase()}">${currentBlock.state} (${currentBlock.count}s)</span>`);

        // 2. UPDATE UI ELEMENTS
        const patternEl = document.getElementById('patternText');
        const effEl = document.getElementById('dnaEfficiency');
        const typeEl = document.getElementById('dnaType');
        const fragEl = document.getElementById('fragmentationCount');

        // Render with arrows
        if (patternEl) {
            patternEl.innerHTML = pattern.join('<span class="dna-arrow"> ➔ </span>');
        }
        
        // Efficiency Score
        if (effEl) {
            let efficiency = Math.round((focusPoints / sessionHistory.length) * 100);
            effEl.innerText = efficiency + "%";
            effEl.style.color = efficiency > 70 ? "#00ff88" : (efficiency > 40 ? "#ffcc00" : "#ff0055");
        }

        // Current State Type
        if (typeEl) {
            const lastVal = sessionHistory[sessionHistory.length - 1].val || 0;
            typeEl.innerText = lastVal >= 0.8 ? "DEEP FLOW" : (lastVal >= 0.3 ? "SWITCHING" : "DRIFTING");
        }
    }
}, 1000);