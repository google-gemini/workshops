/**
 * @fileoverview Service worker for the Fantasy Football Draft Companion.
 * Manages WebSocket connection and offscreen document for audio processing.
 */

const MIDDLEWARE_PORT = 5000;

let controlWs = null;
let creatingOffscreenPromise = null;
let isStopping = false;
let connectionState = 'stopped';

chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  if (request.type === 'connect-and-start') {
    connectAndStart(request.config);
  } else if (request.type === 'stop-everything') {
    stopEverything();
  } else if (request.type === 'get-status') {
    sendResponse({state: connectionState});
    return;
  } else if (request.type === 'send-text-message') {
    sendMessage({mime_type: 'text/plain', data: request.text});
    return;
  }

  if (request.type === 'media-data' && request.target === 'background') {
    let base64Data;

    if (request.mime_type === 'audio/pcm') {
      base64Data = request.data;
    } else if (request.mime_type === 'image/jpeg') {
      base64Data = request.data.split(',')[1];
    }

    if (base64Data) {
      const message = {mime_type: request.mime_type, data: base64Data};
      sendMessage(message);
    }
  }
});

/**
 * Establishes a WebSocket connection and sets up the offscreen document
 * for audio handling.
 * @param {!Object} config The configuration object containing connection
 *     details.
 */
async function connectAndStart(config) {
  chrome.storage.session.set({storedConfig: config});
  connectionState = 'connecting';
  await setupOffscreenDocument('offscreen.html');

  const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
  if (!tab) {
    console.error('Could not find active tab to capture.');
    stopEverything();
    return;
  }

  const streamId =
      await chrome.tabCapture.getMediaStreamId({targetTabId: tab.id});

  const captureStarted = await new Promise((resolve) => {
    const listener = (message) => {
      if (message.type === 'capture-started-successfully') {
        chrome.runtime.onMessage.removeListener(listener);
        resolve({success: true});
      } else if (message.type === 'capture-failed') {
        console.error('Capture permission failed:', message.error);
        chrome.runtime.onMessage.removeListener(listener);
        resolve({success: false, error: message.error});
      }
    };
    chrome.runtime.onMessage.addListener(listener);

    chrome.runtime.sendMessage({
      type: 'start-capture',
      target: 'offscreen',
      data: {streamId: streamId, captureAudio: config.isAudio}
    });
  });

  if (!captureStarted.success) {
    if (captureStarted.error?.name === 'NotAllowedError' && config.isAudio) {
      chrome.runtime.sendMessage({
        type: 'update-status',
        status: 'Mic permission needed...',
        error: true
      });
      await chrome.runtime.openOptionsPage();
    } else {
      chrome.runtime.sendMessage(
          {type: 'update-status', status: 'Capture failed.', error: true});
    }
    stopEverything();
    return;
  }
  chrome.runtime.sendMessage(
      {type: 'update-status', status: 'Capture active. Connecting...'});

  const {userId, leagueId, draftId, isSuperflex, isAudio} = config;
  const WEBSOCKET_URL = `ws://localhost:${MIDDLEWARE_PORT}/ws`;
  const url = `${WEBSOCKET_URL}/${userId}/${leagueId}/${draftId}/${
      isSuperflex}?is_audio=${isAudio}`;

  controlWs = new WebSocket(url);

  controlWs.onopen = async () => {
    connectionState = 'connected';
    console.log('Websocket connected.');
    chrome.runtime.sendMessage(
        {type: 'update-status', status: 'Connected and Streaming!'});
  };

  controlWs.onmessage = (event) => {
    const message_from_server = JSON.parse(event.data);
    if (message_from_server.turn_complete === true) {
      chrome.runtime.sendMessage({type: 'turn-complete'});
      return;
    }

    if (message_from_server.interrupted === true) {
      chrome.runtime.sendMessage(
          {type: 'stop-audio-playback', target: 'offscreen'});
      return;
    }

    if (message_from_server.mime_type === 'audio/pcm') {
      chrome.runtime.sendMessage({
        type: 'play-audio-chunk',
        target: 'offscreen',
        data: message_from_server.data
      });
    } else if (message_from_server.mime_type === 'text/plain') {
      if (message_from_server.command_type === 'play_audio' &&
          message_from_server.sound_id) {
        chrome.runtime.sendMessage({
          type: 'play-audio-command',
          target: 'offscreen',
          data: message_from_server.sound_id
        });
        return;
      }
      chrome.runtime.sendMessage(
          {type: 'text-message-from-server', text: message_from_server.data});
    }
  };

  controlWs.onerror = (error) => {
    console.error('Websocket error:', error);
    chrome.runtime.sendMessage(
        {type: 'update-status', status: 'Connection error.', error: true});
    stopEverything();
  };

  controlWs.onclose = () => {
    console.log('WebSocket disconnected.');
    stopEverything();
  };
}


/**
 * Sets up an offscreen document for audio capture and playback.
 * @param {string} path The path to the offscreen document HTML file.
 * @return {!Promise<void>} A promise that resolves when the offscreen document
 *     is set up.
 */
async function setupOffscreenDocument(path) {
  const existingContexts =
      await chrome.runtime.getContexts({contextTypes: ['OFFSCREEN_DOCUMENT']});
  if (existingContexts.length > 0) {
    console.log('Offscreen document already exists.');
    return;
  }
  if (creatingOffscreenPromise) {
    await creatingOffscreenPromise;
  } else {
    creatingOffscreenPromise = chrome.offscreen.createDocument({
      url: path,
      reasons: ['USER_MEDIA', 'AUDIO_PLAYBACK'],
      justification: 'To capture microphone audio and play back server audio.',
    });
    await creatingOffscreenPromise;
    creatingOffscreenPromise = null;
  }
}

/**
 * Closes the offscreen document if one exists.
 * @return {!Promise<void>} A promise that resolves when the offscreen document
 *     is closed.
 */
async function closeOffscreenDocument() {
  const existingContexts =
      await chrome.runtime.getContexts({contextTypes: ['OFFSCREEN_DOCUMENT']});
  if (existingContexts.length > 0) {
    await chrome.offscreen.closeDocument();
  }
}

/**
 * Closes the WebSocket connection and the offscreen document.
 */
async function stopEverything() {
  if (isStopping) return;
  isStopping = true;
  connectionState = 'stopped';
  console.log('Stopping everything...');

  if (controlWs) {
    controlWs.onmessage = null;
    controlWs.onerror = null;
    controlWs.onclose = null;
    if (controlWs.readyState === WebSocket.OPEN) {
      controlWs.close();
    }
    controlWs = null;
  }

  try {
    const hasOffscreen = await chrome.offscreen.hasDocument();
    if (hasOffscreen) {
      chrome.runtime.sendMessage({type: 'stop-capture', target: 'offscreen'});
    }
  } catch (e) {
    console.warn(
        'Could not send stop message to offscreen doc, it may already be closed.',
        e);
  }

  await closeOffscreenDocument();

  chrome.runtime.sendMessage({type: 'update-status', status: 'Stopped.'});

  setTimeout(() => {
    isStopping = false;
  }, 500);
  console.log('Stopped everything.');
}


/**
 * Sends a message over the WebSocket connection if it is open.
 * @param {!Object} message The message object to send.
 */
function sendMessage(message) {
  if (controlWs && controlWs.readyState == WebSocket.OPEN) {
    const messageJson = JSON.stringify(message);
    controlWs.send(messageJson);
  }
}
