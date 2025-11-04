let lastGeminiMessageEl = null;

const elements = {
  connectBtn: document.getElementById('connectControlBtn'),
  stopBtn: document.getElementById('stopCaptureBtn'),
  userIdInput: document.getElementById('user_id_input'),
  leagueIdInput: document.getElementById('league_id_input'),
  draftIdInput: document.getElementById('draft_id_input'),
  superflexInput: document.getElementById('superflex_input'),
  statusText: document.getElementById('status'),
  connectionIndicator: document.querySelector('#connectionStatus .indicator'),
  connectionStatusText:
      document.querySelector('#connectionStatus span:last-child'),
  audioModeRadio: document.getElementById('audioMode'),
  textModeRadio: document.getElementById('textMode'),
  chatContainer: document.getElementById('chatContainer'),
  messages: document.getElementById('messages'),
  chatInput: document.getElementById('chatInput'),
  sendChatBtn: document.getElementById('sendChatBtn'),
};


chrome.runtime.onMessage.addListener((message) => {
  if (message.type === 'update-status') {
    elements.statusText.textContent = `Status: ${message.status}`;

    if (message.status.startsWith('Connected')) {
      setUiState('connected');
    } else if (
        message.error || message.status === 'Stopped.' ||
        message.status.includes('error')) {
      setUiState('stopped');
    }
  } else if (message.type === 'text-message-from-server') {
    addMessageToChat('gemini', message.text);
  } else if (message.type === 'turn-complete') {
    lastGeminiMessageEl = null;
  }
});

elements.connectBtn.addEventListener('click', () => {
  const {
    userIdInput,
    leagueIdInput,
    draftIdInput,
    superflexInput,
    audioModeRadio
  } = elements;
  if (!userIdInput.value || !leagueIdInput.value || !draftIdInput.value) {
    alert('Please enter a Sleeper User ID, League ID, and Draft ID.');
    return;
  }

  const config = {
    userId: userIdInput.value,
    leagueId: leagueIdInput.value,
    draftId: draftIdInput.value,
    isSuperflex: superflexInput.checked,
    isAudio: audioModeRadio.checked,
  };

  chrome.runtime.sendMessage({type: 'connect-and-start', config: config});
  setUiState('connecting');
});

elements.stopBtn.addEventListener('click', () => {
  chrome.runtime.sendMessage({type: 'stop-everything'});
  setUiState('stopped');
});

/**
 * Central function to manage the UI state.
 * @param {'initial' | 'connecting' | 'connected' | 'stopped'} state
 */
function setUiState(state) {
  const {
    connectBtn,
    stopBtn,
    statusText,
    userIdInput,
    leagueIdInput,
    draftIdInput,
    superflexInput,
    audioModeRadio,
    textModeRadio,
    chatContainer,
    chatInput,
    sendChatBtn,
  } = elements;

  const inputs = [
    userIdInput, leagueIdInput, draftIdInput, superflexInput, audioModeRadio,
    textModeRadio
  ];
  const isTextMode = textModeRadio.checked;

  switch (state) {
    case 'connecting':
      statusText.textContent = 'Status: Starting...';
      connectBtn.disabled = true;
      stopBtn.disabled = false;
      inputs.forEach(input => input.disabled = true);
      updateConnectionIndicator(false);
      chatContainer.style.display = 'none';
      break;
    case 'connected':
      connectBtn.disabled = true;
      stopBtn.disabled = false;
      inputs.forEach(input => input.disabled = true);
      updateConnectionIndicator(true);
      if (isTextMode) {
        chatContainer.style.display = 'block';
        chatInput.disabled = false;
        sendChatBtn.disabled = false;
      } else {
        chatContainer.style.display = 'none';
      }
      break;
    case 'stopped':
    default:
      statusText.textContent = 'Status: Stopped.';
      connectBtn.disabled = false;
      stopBtn.disabled = true;
      inputs.forEach(input => input.disabled = false);
      updateConnectionIndicator(false);
      chatContainer.style.display = 'none';
      break;
  }
}

/**
 * Updates the connection status indicator's color and text.
 * @param {boolean} isConnected True if connected, false otherwise.
 */
function updateConnectionIndicator(isConnected) {
  const {connectionIndicator, connectionStatusText} = elements;
  connectionIndicator.classList.toggle('connected', isConnected);
  connectionIndicator.classList.toggle('disconnected', !isConnected);
  connectionStatusText.textContent = isConnected ? 'Connected' : 'Disconnected';
}

/**
 * Fetches the current connection state from the background script and updates
 * the UI accordingly.
 */
async function syncStateWithBackground() {
  try {
    const data = await chrome.storage.session.get('storedConfig');
    if (data.storedConfig) {
      elements.userIdInput.value = data.storedConfig.userId;
      elements.leagueIdInput.value = data.storedConfig.leagueId;
      elements.draftIdInput.value = data.storedConfig.draftId;
      elements.superflexInput.checked = data.storedConfig.isSuperflex;
      if (data.storedConfig.isAudio === false) {
        elements.textModeRadio.checked = true;
      } else {
        elements.audioModeRadio.checked = true;
      }
    }

    const response = await chrome.runtime.sendMessage({type: 'get-status'});
    const state = response?.state;

    if (state === 'connected') {
      setUiState('connected');
      elements.statusText.textContent = 'Status: Connected and Streaming!';
    } else if (state === 'connecting') {
      setUiState('connecting');
      elements.statusText.textContent = 'Status: Starting...';
    } else {
      setUiState('stopped');
      elements.statusText.textContent = 'Status: Awaiting connection...';
    }
  } catch (e) {
    console.warn('Could not sync state with background:', e.message);
    setUiState('stopped');
    elements.statusText.textContent = 'Status: Awaiting connection...';
  }
}

/**
 * Sends a chat message to the background script.
 */
function sendChatMessage() {
  const text = elements.chatInput.value.trim();
  if (text) {
    chrome.runtime.sendMessage({type: 'send-text-message', text: text});
    addMessageToChat('user', text);
    elements.chatInput.value = '';
  }
}

/**
 * Adds a message to the chat UI.
 * @param {string} sender 'user' or 'gemini'.
 * @param {string} text The message text.
 */
function addMessageToChat(sender, text) {
  if (sender === 'gemini' && lastGeminiMessageEl) {
    lastGeminiMessageEl.textContent += text;
  } else {
    const messageEl = document.createElement('div');
    messageEl.classList.add('message', sender);
    messageEl.textContent = text;
    elements.messages.appendChild(messageEl);

    if (sender === 'gemini') {
      lastGeminiMessageEl = messageEl;
    } else {
      lastGeminiMessageEl = null;
    }
  }
  elements.messages.scrollTop = elements.messages.scrollHeight;
}


elements.sendChatBtn.addEventListener('click', sendChatMessage);
elements.chatInput.addEventListener('keypress', (event) => {
  if (event.key === 'Enter') {
    sendChatMessage();
  }
});


syncStateWithBackground();
