"""Standalone test for TVAudioStream - isolate audio pipeline issues"""

import asyncio
import queue
import sys
from google.cloud import speech

# Same audio settings as chess companion
SEND_SAMPLE_RATE = 16000
HDMI_AUDIO_TARGET = "alsa_input.usb-MACROSILICON_USB3.0_Video_26241327-02.analog-stereo"


class TestTVAudioStream:
    """Test version of TVAudioStream with debug output"""
    
    def __init__(self):
        self._buff = queue.Queue()
        self.closed = True
        self.audio_process = None
        print("🎤 TestTVAudioStream initialized")

    async def __aenter__(self):
        print("🎤 Starting audio stream...")
        self.closed = False
        
        cmd = [
            "pw-cat", "--record", "-",
            "--target", HDMI_AUDIO_TARGET,
            "--rate", str(SEND_SAMPLE_RATE),
            "--channels", "1",
            "--format", "s16",
            "--raw"
        ]
        
        print(f"🎤 Command: {' '.join(cmd)}")
        
        self.audio_process = await asyncio.create_subprocess_exec(
            *cmd, 
            stdout=asyncio.subprocess.PIPE, 
            stderr=asyncio.subprocess.PIPE
        )
        
        print(f"🎤 Subprocess started (PID: {self.audio_process.pid})")
        asyncio.create_task(self._feed_buffer())
        
        # Wait a moment for _feed_buffer to actually start
        await asyncio.sleep(0.5)
        print("🎤 Buffer feeding task should be running now...")
        return self

    async def __aexit__(self, type, value, traceback):
        print("🎤 Closing audio stream...")
        self.closed = True
        if self.audio_process:
            self.audio_process.terminate()
            await self.audio_process.wait()
        self._buff.put(None)

    async def _feed_buffer(self):
        print("🔧 _feed_buffer started")
        chunk_size = int(SEND_SAMPLE_RATE / 10)  # 100ms chunks
        bytes_expected = chunk_size * 2
        chunks_received = 0
        
        while not self.closed:
            try:
                print(f"🔧 Reading {bytes_expected} bytes from subprocess...")
                data = await self.audio_process.stdout.read(bytes_expected)
                
                if not data:
                    print("🔧 No data from subprocess - EOF")
                    break
                
                chunks_received += 1
                print(f"🔧 Got {len(data)} bytes (chunk #{chunks_received})")
                
                self._buff.put(data)
                print(f"🔧 Put chunk #{chunks_received} into queue (queue size: ~{self._buff.qsize()})")
                
                # Check subprocess status
                if self.audio_process.returncode is not None:
                    print(f"🚨 Subprocess exited with code: {self.audio_process.returncode}")
                    break
                
            except Exception as e:
                print(f"❌ _feed_buffer error: {e}")
                break
        
        print(f"🔧 _feed_buffer finished after {chunks_received} chunks")

    def generator(self):
        print("🎵 Generator started")
        chunks_yielded = 0
        
        while not self.closed:
            try:
                print(f"🎵 Waiting for chunk #{chunks_yielded + 1}...")
                chunk = self._buff.get(timeout=2.0)  # Longer timeout for debugging
                
                if chunk is None:
                    print("🎵 Generator termination signal received")
                    return
                
                chunks_yielded += 1
                print(f"🎵 Yielding chunk #{chunks_yielded} ({len(chunk)} bytes)")
                yield chunk
                
            except queue.Empty:
                print("⚠️  Generator timeout - no chunk received")
                print(f"🔧 Queue size: {self._buff.qsize()}")
                print(f"🔧 Process status: {'running' if self.audio_process and self.audio_process.returncode is None else 'dead'}")
                
                # Check if _feed_buffer task is actually running by checking if subprocess is alive
                if self.audio_process and self.audio_process.returncode is None:
                    print("🔧 Subprocess is alive - _feed_buffer might be stuck")
                else:
                    print("🔧 Subprocess died - that's why no chunks")
                continue


async def test_audio_capture():
    """Test just the audio capture without transcription"""
    print("🧪 Testing audio capture only...")
    
    async with TestTVAudioStream() as stream:
        print("✅ Audio stream created successfully")
        
        # Test generator for 10 chunks
        gen = stream.generator()
        for i, chunk in enumerate(gen):
            if i >= 10:
                print("✅ Got 10 chunks successfully!")
                break
            print(f"✅ Chunk {i}: {len(chunk)} bytes")
        
        print("🧪 Audio capture test complete")


async def test_with_transcription():
    """Test with actual Google Cloud Speech transcription"""
    print("🧪 Testing with Google Cloud Speech...")
    
    # Speech config
    speech_client = speech.SpeechClient()
    speech_config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=SEND_SAMPLE_RATE,
        language_code="en-US"
    )
    streaming_config = speech.StreamingRecognitionConfig(
        config=speech_config, interim_results=True
    )
    
    async with TestTVAudioStream() as stream:
        print("✅ Audio stream created for transcription test")
        
        def transcription_thread():
            print("🎤 Starting transcription in thread...")
            audio_generator = stream.generator()
            requests = (
                speech.StreamingRecognizeRequest(audio_content=content) 
                for content in audio_generator
            )
            
            try:
                responses = speech_client.streaming_recognize(streaming_config, requests)
                transcript_count = 0
                
                for response in responses:
                    if response.results:
                        result = response.results[0]
                        if result.alternatives and result.is_final:
                            transcript_count += 1
                            transcript = result.alternatives[0].transcript
                            print(f"📝 Transcript #{transcript_count}: {transcript}")
                            
                        if transcript_count >= 3:  # Stop after 3 transcripts
                            print("✅ Transcription test complete!")
                            break
            except Exception as e:
                print(f"❌ Transcription error: {e}")
        
        # Run transcription in background
        await asyncio.to_thread(transcription_thread)


async def main():
    if len(sys.argv) > 1 and sys.argv[1] == "transcribe":
        await test_with_transcription()
    else:
        await test_audio_capture()


if __name__ == "__main__":
    print("🎤 Standalone Audio Stream Test")
    print("Usage:")
    print("  python test_audio_stream.py        # Test audio capture only")
    print("  python test_audio_stream.py transcribe  # Test with transcription")
    print()
    
    asyncio.run(main())
