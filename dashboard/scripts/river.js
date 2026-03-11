function generateAttentionRiver(intensity, breachCount) {
    const canvas = document.getElementById('riverCanvas');
    const ctx = canvas.getContext('2d');
    const container = document.getElementById('river-container');

    // Set canvas resolution
    canvas.width = container.offsetWidth;
    canvas.height = container.offsetHeight;

    const w = canvas.width;
    const h = canvas.height;
    const midY = h / 2;

    // Clear background
    ctx.fillStyle = "#050505";
    ctx.fillRect(0, 0, w, h);

    // Update stability UI
    document.getElementById('stability-val').innerText = intensity + "%";

    // Create Gradient
    const grad = ctx.createLinearGradient(0, 0, w, 0);
    grad.addColorStop(0, "#00ff88"); // Neon Green
    grad.addColorStop(1, "#00e5ff"); // Cyan

    // Draw the River
    ctx.beginPath();
    ctx.moveTo(0, midY);

    const points = 20;
    const segmentW = w / points;
    const riverThickness = (intensity / 100) * 80; // Scale thickness by focus intensity

    // Top edge of the river (wavy)
    for (let i = 0; i <= points; i++) {
        let x = i * segmentW;
        // If breachCount is high, make the river more "turbulent" (jittery)
        let jitter = (Math.random() - 0.5) * (breachCount * 2);
        let y = midY - riverThickness + jitter;
        ctx.lineTo(x, y);
    }

    // Bottom edge of the river (closing the shape)
    for (let i = points; i >= 0; i--) {
        let x = i * segmentW;
        let jitter = (Math.random() - 0.5) * (breachCount * 2);
        let y = midY + riverThickness + jitter;
        ctx.lineTo(x, y);
    }

    ctx.closePath();
    ctx.fillStyle = grad;
    ctx.shadowBlur = 20;
    ctx.shadowColor = "#00ff88";
    ctx.fill();

    // Draw "Breach Splinters" - Red lines breaking away
    if (breachCount > 0) {
        ctx.shadowBlur = 10;
        ctx.shadowColor = "#ff0055";
        ctx.strokeStyle = "#ff0055";
        ctx.lineWidth = 2;

        for (let i = 0; i < breachCount; i++) {
            let bX = Math.random() * w;
            let bY = midY + (Math.random() > 0.5 ? riverThickness : -riverThickness);
            
            ctx.beginPath();
            ctx.moveTo(bX, bY);
            ctx.lineTo(bX + 30, bY + (Math.random() * 60 - 30));
            ctx.stroke();
        }
    }
}