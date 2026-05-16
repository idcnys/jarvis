const cursor = document.getElementById('cursor');

document.addEventListener('mousemove', (e) => {
    cursor.style.left = `${e.clientX}px`;
    cursor.style.top = `${e.clientY}px`;
});

document.addEventListener('mouseup', () => {
    cursor.style.transform = 'translate(-50%, -50%) scale(1)';
});


document.addEventListener('mousedown', (e) => {
    const effectColor = '#06b6d4'; 

    createShockwave(e.clientX, e.clientY, effectColor);
    createParticles(e.clientX, e.clientY, effectColor);
});

function createShockwave(x, y, color) {
    const wave = document.createElement('div');
    wave.classList.add('shockwave');
    wave.style.left = `${x}px`;
    wave.style.top = `${y}px`;
    wave.style.borderColor = color;
    wave.style.boxShadow = `0 0 20px ${color}, inset 0 0 10px ${color}`;
    
    document.body.appendChild(wave);
    setTimeout(() => wave.remove(), 500); // Matches CSS animation duration
}

function createParticles(x, y, color) {
    const particleCount = 12;

    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.classList.add('click-particle');
        
        // Randomize size for realism (4px to 10px)
        const size = Math.random() * 6 + 4; 
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        
        particle.style.background = color;
        particle.style.boxShadow = `0 0 10px ${color}`;
        particle.style.left = `${x}px`;
        particle.style.top = `${y}px`;
        const angle = Math.random() * Math.PI * 2;
        const distance = Math.random() * 80 + 40; 
        const targetX = Math.cos(angle) * distance;
        const targetY = Math.sin(angle) * distance;

        particle.style.setProperty('--move-x', `${targetX}px`);
        particle.style.setProperty('--move-y', `${targetY}px`);

        document.body.appendChild(particle);

        setTimeout(() => particle.remove(), 600);
    }
}