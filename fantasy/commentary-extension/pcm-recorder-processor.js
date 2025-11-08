class PCMProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
  }

  /**
   * Processes the audio input.
   * @param {!Array<!Array<!Float32Array>>} inputs
   * @param {!Array<!Array<!Float32Array>>} outputs
   * @param {!Object<string, !Float32Array>} parameters
   * @return {boolean}
   */
  process(inputs, outputs, parameters) {
    if (inputs.length > 0 && inputs[0].length > 0) {
      // Use the first channel
      const inputChannel = inputs[0][0];
      // Copy the buffer to avoid issues with recycled memory
      const inputCopy = new Float32Array(inputChannel);
      this.port.postMessage(inputCopy);
    }
    return true;
  }
}

registerProcessor('pcm-recorder-processor', PCMProcessor);
