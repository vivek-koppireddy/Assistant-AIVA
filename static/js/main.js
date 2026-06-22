// Speech API References
let recognition = null;
let speechSynth = window.speechSynthesis;
let availableVoices = [];

// App State
let activeTab = 'chat';
let isListening = false;

// DOM Elements
const chatMessagesContainer = document.getElementById('chat-messages-container');
const inputCommandText = document.getElementById('input-command-text');
const btnMicToggle = document.getElementById('btn-mic-toggle');
const btnSendCommand = document.getElementById('btn-send-command');
const micOverlay = document.getElementById('mic-overlay');
const micIcon = document.getElementById('mic-icon');
const selectVoice = document.getElementById('select-voice');
const chkSpeechOutput = document.getElementById('chk-speech-output');

// Initial setup
document.addEventListener('DOMContentLoaded', () => {
    // 1. Initial State Sync
    syncState();
    loadKnowledgeBase();
    loadCustomCommands();
    
    // 2. Initialize Voices
    initSpeechSynthesis();

    // 3. Initialize Speech Recognition
    initSpeechRecognition();

    // 4. Input events
    inputCommandText.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            submitCommand();
        }
    });

    btnSendCommand.addEventListener('click', submitCommand);
    btnMicToggle.addEventListener('click', toggleSpeechRecognition);

    // 5. Setup Live Time for mock phone
    updatePhoneTime();
    setInterval(updatePhoneTime, 30000);
});

// Update mockup phone status time indicator
function updatePhoneTime() {
    const timeEl = document.getElementById('phone-time');
    if (timeEl) {
        const now = new Date();
        const hrs = String(now.getHours()).padStart(2, '0');
        const mins = String(now.getMinutes()).padStart(2, '0');
        timeEl.textContent = `${hrs}:${mins}`;
    }
}

// Navigation Tabs Manager
function switchTab(tabName) {
    // Hide active tabs
    document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
    
    // Show new tab
    document.getElementById(`tab-content-${tabName}`).classList.add('active');
    document.getElementById(`btn-tab-${tabName}`).classList.add('active');
    
    // Update headers
    const titleEl = document.getElementById('current-tab-title');
    const descEl = document.getElementById('current-tab-desc');
    
    if (tabName === 'chat') {
        titleEl.textContent = 'Assistant Chat';
        descEl.textContent = 'Interact with AIVA using speech-to-text or typed console commands.';
    } else if (tabName === 'settings') {
        titleEl.textContent = 'Device Control Console';
        descEl.textContent = 'Monitor and control the simulated Android hardware state, levels, and notification inputs.';
    } else if (tabName === 'training') {
        titleEl.textContent = 'Training & Knowledge Center';
        descEl.textContent = 'Train custom questions and mapping phrases to expand AIVA\'s abilities.';
    }
    
    activeTab = tabName;
}

// Initialize TTS
function initSpeechSynthesis() {
    if (!speechSynth) return;
    
    function populateVoiceList() {
        availableVoices = speechSynth.getVoices();
        selectVoice.innerHTML = '<option value="none">Browser Default Voice</option>';
        
        availableVoices.forEach((voice, index) => {
            const option = document.createElement('option');
            option.value = index;
            option.textContent = `${voice.name} (${voice.lang})`;
            if (voice.default) {
                option.textContent += ' -- DEFAULT';
            }
            selectVoice.appendChild(option);
        });
    }

    populateVoiceList();
    if (speechSynth.onvoiceschanged !== undefined) {
        speechSynth.onvoiceschanged = populateVoiceList;
    }
}

// Speaks AIVA response back to user
function speakAloud(text) {
    if (!speechSynth || !chkSpeechOutput.checked) return;
    
    // Cancel currently speaking voices
    speechSynth.cancel();
    
    const utterance = new SpeechSynthesisUtterance(text);
    const selectedIdx = selectVoice.value;
    
    if (selectedIdx !== 'none' && availableVoices[selectedIdx]) {
        utterance.voice = availableVoices[selectedIdx];
    }
    
    speechSynth.speak(utterance);
}

// Initialize Speech Recognition (STT)
function initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognitionLog = document.getElementById('speech-recognition-log');
    
    if (!SpeechRecognition) {
        if (recognitionLog) {
            recognitionLog.innerHTML = `
                <h3 style="color:var(--warn-color);"><i class="fa-solid fa-triangle-exclamation"></i> Voice Unsupported</h3>
                <p>Speech recognition is not fully supported in this browser. Please use Chrome, Edge, or Safari, or type command prompts directly in the console.</p>
            `;
        }
        btnMicToggle.style.opacity = '0.5';
        btnMicToggle.disabled = true;
        return;
    }

    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
        isListening = true;
        btnMicToggle.classList.add('listening');
        micIcon.className = 'fa-solid fa-microphone-lines';
        micOverlay.classList.add('active');
        if (recognitionLog) {
            recognitionLog.innerHTML = `
                <h3><i class="fa-solid fa-circle-dot" style="color:var(--danger-color); animation: flash 1s infinite alternate;"></i> Listening...</h3>
                <p>Speak clearly into your microphone. Say standard commands like "turn on wifi" or custom trainings like "train who created you is vivek".</p>
            `;
        }
    };

    recognition.onerror = (event) => {
        console.error('Speech error:', event.error);
        logActivity(`Speech recognition error: ${event.error}`, 'system');
        stopListeningState();
        if (recognitionLog) {
            recognitionLog.innerHTML = `
                <h3 style="color:var(--danger-color);"><i class="fa-solid fa-xmark"></i> Listening Error</h3>
                <p>Failed to capture audio (${event.error}). Verify browser mic permissions are enabled.</p>
            `;
        }
    };

    recognition.onend = () => {
        stopListeningState();
    };

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        inputCommandText.value = transcript;
        if (recognitionLog) {
            recognitionLog.innerHTML = `
                <h3><i class="fa-solid fa-square-check" style="color:var(--accent-color);"></i> Captured Transcript</h3>
                <p style="font-weight: 500; color: #fff;">"${transcript}"</p>
            `;
        }
        submitCommand();
    };
}

function toggleSpeechRecognition() {
    if (!recognition) return;
    
    if (isListening) {
        recognition.stop();
    } else {
        try {
            recognition.start();
        } catch (e) {
            console.error(e);
        }
    }
}

function stopListeningState() {
    isListening = false;
    btnMicToggle.classList.remove('listening');
    micIcon.className = 'fa-solid fa-microphone';
    micOverlay.classList.remove('active');
}

// Submits Command (Typed or Spoken)
async function submitCommand() {
    const cmd = inputCommandText.value.trim();
    if (!cmd) return;
    
    // Clear input
    inputCommandText.value = '';
    
    // Render user speech bubble
    appendMessage(cmd, 'user');
    logActivity(`Command sent: "${cmd}"`, 'user');

    try {
        const response = await fetch('/api/command', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({command: cmd})
        });
        
        const data = await response.json();
        
        // Render assistant responses
        if (data.responses) {
            data.responses.forEach(text => {
                appendMessage(text, 'assistant');
                logActivity(`AIVA response: "${text}"`, 'system');
                speakAloud(text);
            });
        }
        
        // Update state widget indicators
        if (data.state) {
            renderState(data.state);
        }

    } catch (err) {
        console.error(err);
        appendMessage('Sorry, I couldn\'t communicate with the server.', 'assistant');
        logActivity('Failed to process command: Server communication error.', 'system');
    }
}

// Append Chat Bubbles
function appendMessage(text, sender) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}-msg`;
    
    const bubble = document.createElement('div');
    bubble.className = 'msg-bubble';
    bubble.textContent = text;
    
    msgDiv.appendChild(bubble);
    chatMessagesContainer.appendChild(msgDiv);
    
    // Scroll to bottom
    chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
}

// Sync Device State from Server
async function syncState() {
    try {
        const response = await fetch('/api/state');
        const state = await response.json();
        renderState(state);
    } catch (err) {
        console.error('Error syncing state:', err);
    }
}

// Renders state values to widgets and mock phone status bar
function renderState(state) {
    // 1. Wi-Fi
    const isWifiOn = state.wifi === 'ON';
    document.getElementById('switch-wifi').checked = isWifiOn;
    document.getElementById('val-wifi').textContent = state.wifi;
    const phoneWifiIcon = document.getElementById('phone-icon-wifi');
    if (isWifiOn) {
        phoneWifiIcon.style.opacity = '1';
        phoneWifiIcon.className = 'fa-solid fa-wifi';
    } else {
        phoneWifiIcon.style.opacity = '0.3';
        phoneWifiIcon.className = 'fa-solid fa-wifi';
    }

    // 2. Bluetooth
    const isBtOn = state.bluetooth === 'ON';
    document.getElementById('switch-bluetooth').checked = isBtOn;
    document.getElementById('val-bluetooth').textContent = state.bluetooth;
    const phoneBtIcon = document.getElementById('phone-icon-bt');
    if (isBtOn) {
        phoneBtIcon.style.opacity = '1';
        phoneBtIcon.className = 'fa-solid fa-bluetooth-b';
    } else {
        phoneBtIcon.style.opacity = '0.3';
        phoneBtIcon.className = 'fa-solid fa-bluetooth';
    }

    // 3. Flashlight
    const isFlashOn = state.flashlight === 'ON';
    document.getElementById('switch-flashlight').checked = isFlashOn;
    document.getElementById('val-flashlight').textContent = state.flashlight;
    
    const phoneFlashIcon = document.getElementById('phone-icon-flashlight');
    const flashlightBeam = document.getElementById('flashlight-beam');
    if (isFlashOn) {
        phoneFlashIcon.style.display = 'inline-block';
        flashlightBeam.classList.add('active');
    } else {
        phoneFlashIcon.style.display = 'none';
        flashlightBeam.classList.remove('active');
    }

    // 4. Levels
    const volVal = parseInt(state.volume);
    const brightVal = parseInt(state.brightness);
    document.getElementById('slider-volume').value = volVal;
    document.getElementById('label-volume').textContent = state.volume;
    document.getElementById('slider-brightness').value = brightVal;
    document.getElementById('label-brightness').textContent = state.brightness;

    // 5. Activity Log lists
    if (state.logs) {
        const logDisplay = document.getElementById('activity-log-display');
        logDisplay.innerHTML = '';
        state.logs.forEach(log => {
            const entry = document.createElement('div');
            entry.className = 'log-entry';
            if (log.includes('Simulated')) {
                entry.classList.add('system-entry');
            } else {
                entry.classList.add('user-entry');
            }
            entry.textContent = log;
            logDisplay.appendChild(entry);
        });
        logDisplay.scrollTop = logDisplay.scrollHeight;
    }
}

// Manual Toggle Widgets
async function toggleState(field) {
    const el = document.getElementById(`switch-${field}`);
    const val = el.checked ? 'ON' : 'OFF';
    
    try {
        const response = await fetch('/api/state', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({[field]: val})
        });
        const state = await response.json();
        renderState(state);
        logActivity(`Simulated device widget toggle: ${field} set to ${val}`, 'system');
    } catch (err) {
        console.error(err);
    }
}

// Level slider changes
async function updateLevel(field, val) {
    document.getElementById(`label-${field}`).textContent = `${val}%`;
    try {
        const response = await fetch('/api/state', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({[field]: `${val}%`})
        });
        const state = await response.json();
        renderState(state);
    } catch (err) {
        console.error(err);
    }
}

// Clear state log API
async function clearLogs() {
    try {
        await fetch('/api/state', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({clear_notifications: true})
        });
        // We also want to locally reset activity log view
        document.getElementById('activity-log-display').innerHTML = '<div class="log-entry system-entry">Logs cleared.</div>';
    } catch (err) {
        console.error(err);
    }
}

// Spawns simulated alert/notification
async function spawnNotification(e) {
    e.preventDefault();
    const appVal = document.getElementById('select-notif-app').value;
    const fromVal = document.getElementById('input-notif-from').value.trim();
    const msgVal = document.getElementById('input-notif-msg').value.trim();
    
    if (!fromVal || !msgVal) return;
    
    try {
        const response = await fetch('/api/state', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                add_notification: {
                    app: appVal,
                    from: fromVal,
                    message: msgVal
                }
            })
        });
        const state = await response.json();
        renderState(state);
        
        // Reset message form input
        document.getElementById('input-notif-msg').value = '';
        logActivity(`Notification spawned: ${appVal} message from ${fromVal}`, 'system');
        
        // Append small notification alert to phone chat directly
        appendMessage(`[NOTIFICATION] ${appVal} message from ${fromVal}: "${msgVal}"`, 'assistant');
        speakAloud(`Incoming message from ${fromVal} on ${appVal}`);
    } catch (err) {
        console.error(err);
    }
}

// Log activities
function logActivity(text, sender) {
    const logDisplay = document.getElementById('activity-log-display');
    if (!logDisplay) return;
    
    const entry = document.createElement('div');
    entry.className = `log-entry ${sender}-entry`;
    const time = new Date().toLocaleTimeString();
    entry.textContent = `[${time}] ${text}`;
    
    logDisplay.appendChild(entry);
    logDisplay.scrollTop = logDisplay.scrollHeight;
}

// ==========================================
// KNOWLEDGE BASE TRAINING OPERATIONS
// ==========================================
async function loadKnowledgeBase() {
    try {
        const response = await fetch('/api/knowledge');
        const data = await response.json();
        const tbody = document.getElementById('list-kb-tbody');
        tbody.innerHTML = '';
        
        data.forEach(item => {
            const tr = document.createElement('tr');
            
            const tdQ = document.createElement('td');
            tdQ.textContent = item.question;
            
            const tdA = document.createElement('td');
            tdA.textContent = item.answer;
            
            const tdDel = document.createElement('td');
            const btnDel = document.createElement('button');
            btnDel.className = 'btn-delete-row';
            btnDel.innerHTML = '<i class="fa-solid fa-trash"></i>';
            btnDel.onclick = () => deleteKnowledge(item.question);
            tdDel.appendChild(btnDel);
            
            tr.appendChild(tdQ);
            tr.appendChild(tdA);
            tr.appendChild(tdDel);
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error(err);
    }
}

async function addKnowledge(e) {
    e.preventDefault();
    const qEl = document.getElementById('input-kb-q');
    const aEl = document.getElementById('input-kb-a');
    const question = qEl.value.trim();
    const answer = aEl.value.trim();
    
    if (!question || !answer) return;
    
    try {
        const response = await fetch('/api/knowledge', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({question, answer})
        });
        
        if (response.ok) {
            qEl.value = '';
            aEl.value = '';
            loadKnowledgeBase();
            logActivity(`Trained Knowledge added via UI: "${question}"`, 'system');
        }
    } catch (err) {
        console.error(err);
    }
}

async function deleteKnowledge(question) {
    try {
        const response = await fetch('/api/knowledge', {
            method: 'DELETE',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({question})
        });
        
        if (response.ok) {
            loadKnowledgeBase();
            logActivity(`Trained Knowledge deleted: "${question}"`, 'system');
        }
    } catch (err) {
        console.error(err);
    }
}

// ==========================================
// CUSTOM COMMAND TRAINING OPERATIONS
// ==========================================
async function loadCustomCommands() {
    try {
        const response = await fetch('/api/commands');
        const data = await response.json();
        const tbody = document.getElementById('list-cmd-tbody');
        tbody.innerHTML = '';
        
        data.forEach(item => {
            const tr = document.createElement('tr');
            
            const tdPhrase = document.createElement('td');
            tdPhrase.textContent = item.phrase;
            
            const tdAction = document.createElement('td');
            tdAction.textContent = item.action;
            
            const tdDel = document.createElement('td');
            const btnDel = document.createElement('button');
            btnDel.className = 'btn-delete-row';
            btnDel.innerHTML = '<i class="fa-solid fa-trash"></i>';
            btnDel.onclick = () => deleteCommand(item.phrase);
            tdDel.appendChild(btnDel);
            
            tr.appendChild(tdPhrase);
            tr.appendChild(tdAction);
            tr.appendChild(tdDel);
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error(err);
    }
}

async function addCommand(e) {
    e.preventDefault();
    const pEl = document.getElementById('input-cmd-phrase');
    const aEl = document.getElementById('input-cmd-action');
    const phrase = pEl.value.trim();
    const action = aEl.value.trim();
    
    if (!phrase || !action) return;
    
    try {
        const response = await fetch('/api/commands', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({phrase, action})
        });
        
        if (response.ok) {
            pEl.value = '';
            aEl.value = '';
            loadCustomCommands();
            logActivity(`Custom Command shortcut trained via UI: "${phrase}" -> "${action}"`, 'system');
        }
    } catch (err) {
        console.error(err);
    }
}

async function deleteCommand(phrase) {
    try {
        const response = await fetch('/api/commands', {
            method: 'DELETE',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({phrase})
        });
        
        if (response.ok) {
            loadCustomCommands();
            logActivity(`Custom Command deleted: "${phrase}"`, 'system');
        }
    } catch (err) {
        console.error(err);
    }
}
