// Aria Visual Command Controller
const aria = document.getElementById('aria');
const ariaMouth = document.getElementById('ariaMouth');
const ariaArmLeft = document.getElementById('ariaArmLeft');
const ariaArmRight = document.getElementById('ariaArmRight');
const ariaLegLeft = document.getElementById('ariaLegLeft');
const ariaLegRight = document.getElementById('ariaLegRight');
const stage = document.getElementById('stage');
const commandInput = document.getElementById('commandInput');
const logContainer = document.getElementById('logContainer');

const expressions = {
    'smile': '😊',
    'happy': '😃',
    'sad': '😢',
    'surprised': '😲',
    'confused': '😕',
    'thinking': '🤔',
    'wink': '😉'
};

function log(message, isError = false) {
    const entry = document.createElement('div');
    entry.className = 'log-entry';
    entry.style.borderLeftColor = isError ? '#e74c3c' : '#667eea';
    entry.style.color = isError ? '#e74c3c' : '#555';
    entry.textContent = `${new Date().toLocaleTimeString()}: ${message}`;
    logContainer.insertBefore(entry, logContainer.firstChild);
    
    // Keep only last 10 entries
    while (logContainer.children.length > 10) {
        logContainer.removeChild(logContainer.lastChild);
    }
}

async function sendCommand() {
    const command = commandInput.value.trim();
    if (!command) return;
    
    log(`Command: "${command}"`);
    commandInput.value = '';
    
    try {
        // Call backend API
        const response = await fetch('/api/aria/command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: command })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.tags && data.tags.length > 0) {
            log(`✅ ${data.model}: ${data.tags.join(' ')}`);
            executeTags(data.tags);
        } else if (data.error) {
            log(`⚠️ API Error: ${data.error}`, true);
            executeLocalCommand(command);
        } else {
            log('⚠️ Using fallback parser');
            executeLocalCommand(command);
        }
    } catch (error) {
        log(`⚠️ Network error, using fallback`, true);
        // Fallback: parse command locally without AI
        executeLocalCommand(command);
    }
}

function executeLocalCommand(command) {
    // Simple local fallback without AI model
    const cmd = command.toLowerCase();
    let executed = false;
    
    if (cmd.includes('smile') || cmd.includes('happy')) {
        changeExpression('smile');
        executed = true;
    }
    if (cmd.includes('sad')) {
        changeExpression('sad');
        executed = true;
    }
    if (cmd.includes('surprised')) {
        changeExpression('surprised');
        executed = true;
    }
    if (cmd.includes('jump')) {
        animate('jumping');
        executed = true;
    }
    if (cmd.includes('dance')) {
        animate('dancing');
        executed = true;
    }
    if (cmd.includes('spin')) {
        animate('spinning');
        executed = true;
    }
    if (cmd.includes('wave')) {
        animate('waving');
        executed = true;
    }
    if (cmd.includes('sparkle')) {
        createEffect('sparkle');
        executed = true;
    }
    if (cmd.includes('hearts')) {
        createEffect('hearts');
        executed = true;
    }
    if (cmd.includes('left')) {
        const speed = cmd.includes('run') ? 'run' : 'normal';
        move('left', speed);
        executed = true;
    }
    if (cmd.includes('right')) {
        const speed = cmd.includes('run') ? 'run' : 'normal';
        move('right', speed);
        executed = true;
    }
    if (cmd.includes('walk')) {
        const direction = cmd.includes('left') ? 'left' : cmd.includes('right') ? 'right' : null;
        if (direction) move(direction, 'normal');
        executed = true;
    }
    if (cmd.includes('run')) {
        const direction = cmd.includes('left') ? 'left' : cmd.includes('right') ? 'right' : null;
        if (direction) move(direction, 'run');
        executed = true;
    }
    
    if (!executed) {
        log('❌ Command not recognized', true);
    }
}

function executeTags(tags) {
    tags.forEach((tag, index) => {
        // Parse tag format: [aria:category:action:param]
        const match = tag.match(/\[aria:([^:]+):([^:\]]+)(?::([^:\]]+))?\]/);
        if (!match) return;
        
        const [, category, action, param] = match;
        
        setTimeout(() => {
            switch (category) {
                case 'expression':
                    changeExpression(action);
                    break;
                case 'animate':
                    animate(getAnimationClass(action));
                    break;
                case 'gesture':
                    animate('waving');
                    break;
                case 'move':
                    move(action, 'normal');
                    break;
                case 'walk':
                    move(action, 'normal');
                    break;
                case 'run':
                    move(action, 'run');
                    break;
                case 'effect':
                    createEffect(action);
                    break;
                case 'camera':
                    if (action === 'center') centerAria();
                    break;
                case 'pose':
                    changePose(action);
                    break;
            }
        }, index * 500); // Stagger multiple commands
    });
}

function changeExpression(emotion) {
    ariaMouth.className = 'aria-mouth';
    
    switch(emotion) {
        case 'smile':
        case 'happy':
            ariaMouth.classList.add('smile');
            break;
        case 'sad':
            ariaMouth.classList.add('sad');
            break;
        case 'surprised':
            ariaMouth.style.borderRadius = '50%';
            ariaMouth.style.width = '15px';
            ariaMouth.style.height = '15px';
            ariaMouth.style.borderTop = '2px solid #333';
            break;
        case 'wink':
            document.querySelectorAll('.aria-eye')[1].style.height = '4px';
            setTimeout(() => {
                document.querySelectorAll('.aria-eye')[1].style.height = '12px';
            }, 500);
            break;
        default:
            ariaMouth.classList.add('smile');
    }
    
    aria.style.transform = 'translateX(-50%) scale(1.1)';
    setTimeout(() => {
        aria.style.transform = 'translateX(-50%) scale(1)';
    }, 300);
}

function animate(className) {
    aria.classList.remove('jumping', 'dancing', 'spinning', 'waving');
    void aria.offsetWidth; // Force reflow
    
    if (className === 'waving') {
        ariaArmRight.style.transition = 'transform 0.3s';
        ariaArmRight.style.transform = 'rotate(60deg)';
        setTimeout(() => {
            ariaArmRight.style.transform = 'rotate(-20deg)';
            setTimeout(() => {
                ariaArmRight.style.transform = 'rotate(20deg)';
            }, 300);
        }, 300);
    } else if (className === 'jumping') {
        aria.classList.add(className);
        ariaLegLeft.style.transition = 'transform 0.2s';
        ariaLegRight.style.transition = 'transform 0.2s';
        ariaLegLeft.style.transform = 'rotate(-15deg)';
        ariaLegRight.style.transform = 'rotate(15deg)';
        setTimeout(() => {
            ariaLegLeft.style.transform = 'rotate(0deg)';
            ariaLegRight.style.transform = 'rotate(0deg)';
        }, 500);
        setTimeout(() => aria.classList.remove(className), 1000);
    } else {
        aria.classList.add(className);
        setTimeout(() => {
            aria.classList.remove(className);
        }, className === 'dancing' ? 2000 : 1000);
    }
}

function getAnimationClass(action) {
    const animations = {
        'jump': 'jumping',
        'dance': 'dancing',
        'spin': 'spinning',
        'wave': 'waving',
        'bow': 'waving',
        'flip': 'spinning',
        'backflip': 'spinning'
    };
    return animations[action] || 'jumping';
}

function move(direction, speed = 'normal') {
    const currentLeft = aria.style.left || '50%';
    const current = parseFloat(currentLeft);
    
    let newPos = current;
    let distance = speed === 'run' ? 20 : 15;
    
    switch (direction) {
        case 'left':
            newPos = Math.max(10, current - distance);
            break;
        case 'right':
            newPos = Math.min(90, current + distance);
            break;
    }
    
    // Add walking leg animation
    if (direction === 'left' || direction === 'right') {
        ariaLegLeft.style.transition = 'transform 0.3s';
        ariaLegRight.style.transition = 'transform 0.3s';
        
        // Alternate leg movement
        ariaLegLeft.style.transform = 'rotate(-10deg)';
        ariaLegRight.style.transform = 'rotate(10deg)';
        
        setTimeout(() => {
            ariaLegLeft.style.transform = 'rotate(10deg)';
            ariaLegRight.style.transform = 'rotate(-10deg)';
            
            setTimeout(() => {
                ariaLegLeft.style.transform = 'rotate(0deg)';
                ariaLegRight.style.transform = 'rotate(0deg)';
            }, 150);
        }, 150);
    }
    
    aria.style.transition = 'left 0.5s ease';
    aria.style.left = newPos + '%';
}

function createEffect(type) {
    const effects = {
        'sparkle': '✨',
        'glow': '💫',
        'hearts': '💕'
    };
    
    const emoji = effects[type] || '✨';
    
    for (let i = 0; i < 5; i++) {
        setTimeout(() => {
            const effect = document.createElement('div');
            effect.className = `effect ${type}`;
            effect.textContent = emoji;
            effect.style.left = (Math.random() * 80 + 10) + '%';
            effect.style.top = (Math.random() * 80 + 10) + '%';
            stage.appendChild(effect);
            
            setTimeout(() => effect.remove(), 1500);
        }, i * 100);
    }
}

function centerAria() {
    aria.style.left = '50%';
    aria.style.transform = 'translateX(-50%) scale(1)';
}

function changePose(pose) {
    // Visual feedback for poses
    const poses = {
        'sit': { bottom: '20px', transform: 'translateX(-50%) scale(0.8)' },
        'stand': { bottom: '50px', transform: 'translateX(-50%) scale(1)' },
        'crouch': { bottom: '30px', transform: 'translateX(-50%) scale(0.9)' },
        'lie': { bottom: '10px', transform: 'translateX(-50%) scale(0.7) rotate(90deg)' }
    };
    
    const poseStyle = poses[pose];
    if (poseStyle) {
        aria.style.bottom = poseStyle.bottom;
        aria.style.transform = poseStyle.transform;
    }
}

function quickCommand(cmd) {
    commandInput.value = cmd;
    sendCommand();
}

// Initialize
log('🎨 Aria Visual System Ready!');
log('Type commands or use quick buttons');
