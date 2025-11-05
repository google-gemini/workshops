const requestBtn = document.getElementById('requestPermissionBtn');
const statusEl = document.getElementById('status');

requestBtn.addEventListener('click', async () => {
  statusEl.textContent = 'Requesting permission...';
  try {
    const stream = await navigator.mediaDevices.getUserMedia({audio: true});
    stream.getTracks().forEach(track => track.stop());

    statusEl.textContent =
        'Permission granted! You can now close this tab and try again.';
    statusEl.style.color = 'green';
    requestBtn.disabled = true;

  } catch (error) {
    console.error('Error requesting microphone permission:', error);
    statusEl.textContent =
        'Permission was denied. Please enable it in the extension site settings.';
    statusEl.style.color = 'red';
  }
});
