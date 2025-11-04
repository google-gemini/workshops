/**
 * @fileoverview Offscreen document for the Fantasy Football Draft Companion.
 * Listens for audio capture and playback commands from the background script.
 */

const SEND_AUDIO_SAMPLE_RATE = 16000;
const RECEIVE_AUDIO_SAMPLE_RATE = 24000;
const FRAME_RATE = 1;
const SOUND_EFFECT_VOLUME = 0.3;
const JPEG_QUALITY = 1.0;
const BUFFER_INTERVAL_MS = 100;

// Sound effect assets
const SOUND_EFFECT_ASSETS = {
  'intro': 'sounds/intro.wav',
  'applause': 'sounds/applause.wav',
  'boo': 'sounds/boo.wav',
  'gasp': 'sounds/gasp.wav',
  'chime': 'sounds/chime.wav',
};
const CACHE_SOUND_BUFFERS = {};

// Capture-related state
let audioRecorderContext = null;
let micStream = null;
let videoStream = null;
let frameSenderInterval = null;
let audioBuffer = [];
let bufferSendInterval = null;

// Playback-related state
let playerContext = null;
let audioPlayerNode = null;
let playerInitializationPromise = null;
const soundEffectSources = new Set();

const canvas = document.createElement('canvas');
const ctx = canvas.getContext('2d');

chrome.runtime.onMessage.addListener(
    /**
     * Handles messages sent to the offscreen document.
     * This listener is async to correctly handle asynchronous operations.
     * @param {!object} message The message received.
     * @param {?chrome.runtime.MessageSender} sender The sender of the message.
     * @param {function(?any): void} sendResponse A function to send a response.
     */
    async (message, sender, sendResponse) => {
      if (message.target !== 'offscreen') {
        return;
      }

      switch (message.type) {
        case 'start-capture':
          await startCapture(message.data);
          break;
        case 'play-audio-chunk':
          await playAudioChunk(message.data);
          break;
        case 'play-audio-command':
          await playAudioCommand(message.data);
          break;
        case 'stop-audio-playback':
          if (audioPlayerNode) {
            audioPlayerNode.port.postMessage({command: 'endOfAudio'});
          }
          soundEffectSources.forEach(source => source.stop());
          soundEffectSources.clear();
          break;
        case 'stop-capture':
          await stopCapture();
          break;
      }
    });

/**
 * Starts capturing screen video and optionally microphone audio.
 * @param {{streamId: string, captureAudio: boolean}} data Object containing
 *     streamId for tab capture and captureAudio boolean.
 */
async function startCapture(data) {
  if (audioRecorderContext || frameSenderInterval) {
    console.warn('Capture is already in progress.');
    return;
  }

  const {streamId, captureAudio} = data;

  try {
    // Get video stream from tab
    videoStream = await navigator.mediaDevices.getUserMedia({
      video: {
        mandatory: {
          chromeMediaSource: 'tab',
          chromeMediaSourceId: streamId,
        },
      },
    });

    if (captureAudio) {
      // Get audio stream from microphone
      micStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          autoGainControl: true,
          noiseSuppression: 1,
          echoCancellation: 1
        },
      });
    }

    // --- Setup video capture pipeline ---
    const videoTrack = videoStream.getVideoTracks()[0];
    const imageCapture = new ImageCapture(videoTrack);

    frameSenderInterval = setInterval(async () => {
      try {
        const imageBitmap = await imageCapture.grabFrame();
        const cropHeight = imageBitmap.height / 2;
        canvas.width = imageBitmap.width;
        canvas.height = cropHeight;

        ctx.drawImage(
            imageBitmap, 0, 0, imageBitmap.width, cropHeight, 0, 0,
            imageBitmap.width, cropHeight);
        canvas.toBlob((blob) => {
          if (!blob) return;
          const reader = new FileReader();
          reader.onload = () => {
            chrome.runtime.sendMessage({
              type: 'media-data',
              target: 'background',
              mime_type: 'image/jpeg',
              data: reader.result,
            });
          };
          reader.readAsDataURL(blob);
        }, 'image/jpeg', JPEG_QUALITY);
      } catch (error) {
        console.warn('Could not grab video frame:', error);
      }
    }, 1000 / FRAME_RATE);

    if (captureAudio) {
      audioRecorderContext =
          new AudioContext({sampleRate: SEND_AUDIO_SAMPLE_RATE});
      await audioRecorderContext.audioWorklet.addModule(
          chrome.runtime.getURL('pcm-recorder-processor.js'));

      const source = audioRecorderContext.createMediaStreamSource(micStream);
      const audioRecorderNode =
          new AudioWorkletNode(audioRecorderContext, 'pcm-recorder-processor');

      audioRecorderNode.port.onmessage = (event) => {
        const pcm16Data = convertFloat32ToPCM(event.data);
        handleAudioRecording(pcm16Data);
      };

      source.connect(audioRecorderNode);
      audioRecorderNode.connect(audioRecorderContext.destination);
    }

    console.log('Successfully started video and audio capture pipelines.');
    chrome.runtime.sendMessage({type: 'capture-started-successfully'});

  } catch (error) {
    console.error(
        'Error starting full media capture:', error.name, error.message);
    await stopCapture();
    chrome.runtime.sendMessage({
      type: 'capture-failed',
      error: {name: error.name, message: error.message},
    });
  }
}

/**
 * Handles incoming PCM data from the recorder worklet by buffering it.
 * @param {!ArrayBuffer} pcmData - The 16-bit PCM audio data.
 */
function handleAudioRecording(pcmData) {
  audioBuffer.push(new Uint8Array(pcmData));

  if (!bufferSendInterval) {
    bufferSendInterval = setInterval(sendBufferedAudio, BUFFER_INTERVAL_MS);
  }
}

/**
 * Combines buffered audio chunks and sends them to the background script.
 * This is an async function because Blob.arrayBuffer() is async.
 */
async function sendBufferedAudio() {
  if (audioBuffer.length === 0) {
    return;
  }

  const audioBlob = new Blob(audioBuffer);
  const combinedBuffer = await audioBlob.arrayBuffer();

  audioBuffer = [];

  if (combinedBuffer.byteLength === 0) {
    return;
  }

  const base64Audio = arrayBufferToBase64(combinedBuffer);

  chrome.runtime.sendMessage({
    type: 'media-data',
    target: 'background',
    mime_type: 'audio/pcm',
    data: base64Audio,
  });
}


/**
 * Initializes the AudioContext and player node for playback.
 */
async function initializePlayer() {
  if (playerContext) return;

  try {
    playerContext = new AudioContext({sampleRate: RECEIVE_AUDIO_SAMPLE_RATE});
    await playerContext.resume();

    // Cache all sound effects.
    const loadingPromises = Object.entries(SOUND_EFFECT_ASSETS)
                                .map(([id, url]) => loadAndCacheSound(id, url));
    await Promise.all(loadingPromises);
    console.log(`Successfully cached ${loadingPromises.length} sound effects.`);

    // Setup streamed audio worklet.
    const workletURL = chrome.runtime.getURL('pcm-player-processor.js');
    await playerContext.audioWorklet.addModule(workletURL);
    audioPlayerNode =
        new AudioWorkletNode(playerContext, 'pcm-player-processor');
    audioPlayerNode.connect(playerContext.destination);
    audioPlayerNode.port.onmessage = (event) => {
      console.log('Received audio data from server:', event.data);
    };
    console.log('Audio player initialized.');
  } catch (error) {
    console.error('Failed to initialize audio player:', error);
    playerContext = null;
    audioPlayerNode = null;
    playerInitializationPromise = null;
    throw error;
  }
}

/**
 * Helper function to fetch, decode, and cache an audio file.
 * @param {string} id The standardized sound ID.
 * @param {string} url The path to the sound file.
 */
async function loadAndCacheSound(id, url) {
  const fullUrl = chrome.runtime.getURL(url);
  const response = await fetch(fullUrl);
  const arrayBuffer = await response.arrayBuffer();

  CACHE_SOUND_BUFFERS[id] = await playerContext.decodeAudioData(arrayBuffer);
}


/**
 * Plays a specific sound effect using the cached AudioBuffer.
 * This is called when the server sends a 'play_audio' command.
 * @param {string} soundId The standardized soundId.
 */
async function playAudioCommand(soundId) {
  if (!playerInitializationPromise) {
    playerInitializationPromise = initializePlayer();
  }

  try {
    await playerInitializationPromise;

    const audioBuffer = CACHE_SOUND_BUFFERS[soundId];

    if (audioBuffer) {
      const gainNode = playerContext.createGain();
      gainNode.gain.value = SOUND_EFFECT_VOLUME;

      const source = playerContext.createBufferSource();
      source.buffer = audioBuffer;
      source.connect(gainNode);
      gainNode.connect(playerContext.destination);
      source.start(0);
      soundEffectSources.add(source);
      source.onended = () => {
        soundEffectSources.delete(source);
      };

      console.log(`Playing cached sound: ${soundId} at ${
          SOUND_EFFECT_VOLUME * 100}% volume`);
    } else {
      console.warn(
          `Attempted to play unknown or un-cached sound ID: ${soundId}`);
    }

    if (playerContext.state === 'suspended') {
      await playerContext.resume();
    }
  } catch (error) {
    console.error('Error during cached audio playback:', error);
  }
}

/**
 * Plays a chunk of audio data, initializing the player if needed.
 * @param {string} base64Data The audio data encoded in base64.
 */
async function playAudioChunk(base64Data) {
  if (!playerInitializationPromise) {
    playerInitializationPromise = initializePlayer();
  }

  try {
    await playerInitializationPromise;
    if (audioPlayerNode) {
      audioPlayerNode.port.postMessage(base64ToArrayBuffer(base64Data));
    }
  } catch (error) {
    console.error(
        'Cannot play audio chunk due to player initialization failure.');
  }
}


/**
 * Stops all ongoing media capture, including audio and video streams,
 * and clears any frame sending intervals.
 */
async function stopCapture() {
  if (frameSenderInterval) {
    clearInterval(frameSenderInterval);
    frameSenderInterval = null;
  }
  if (bufferSendInterval) {
    clearInterval(bufferSendInterval);
    bufferSendInterval = null;
  }

  if (audioBuffer.length > 0) {
    await sendBufferedAudio();
  }

  micStream?.getTracks().forEach(track => track.stop());
  videoStream?.getTracks().forEach(track => track.stop());
  micStream = null;
  videoStream = null;

  if (audioRecorderContext) {
    await audioRecorderContext.close();
    audioRecorderContext = null;
  }
  if (playerContext) {
    await playerContext.close();
    playerContext = null;
    audioPlayerNode = null;
    playerInitializationPromise = null;
  }

  console.log('Media capture stopped and all resources released.');
}

/**
 * Converts a Float32Array to a 16-bit PCM ArrayBuffer.
 * @param {!Float32Array} inputData Audio samples ranging from -1.0 to 1.0.
 * @return {!ArrayBuffer} The 16-bit PCM data.
 */
function convertFloat32ToPCM(inputData) {
  const pcm16 = new Int16Array(inputData.length);
  for (let i = 0; i < inputData.length; i++) {
    // Clamp the value between -1 and 1 before converting
    const s = Math.max(-1, Math.min(1, inputData[i]));
    // Scale to 16-bit integer range
    pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
  }
  return pcm16.buffer;
}

/**
 * Converts a base64 encoded string to an ArrayBuffer.
 * @param {string} base64 The base64 encoded string.
 * @return {!ArrayBuffer} An ArrayBuffer containing the binary data.
 */
function base64ToArrayBuffer(base64) {
  const binaryString = window.atob(base64);
  const len = binaryString.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes.buffer;
}

/**
 * Converts an ArrayBuffer to a Base64 encoded string.
 * @param {!ArrayBuffer} buffer The ArrayBuffer to convert.
 * @return {string} The Base64 encoded string.
 */
function arrayBufferToBase64(buffer) {
  let binary = '';
  const bytes = new Uint8Array(buffer);
  const len = bytes.byteLength;
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}
