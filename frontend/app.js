document.addEventListener('DOMContentLoaded', () => {
    const cursorGlow = document.getElementById('cursor-glow');
    if (cursorGlow) {
        document.addEventListener('mousemove', (e) => {
            cursorGlow.style.transform = `translate(calc(${e.clientX}px - 50%), calc(${e.clientY}px - 50%))`;
        });
    }
});
