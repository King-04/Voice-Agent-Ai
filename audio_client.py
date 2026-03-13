#!/usr/bin/env python3
"""
Audio File Client for Wazobia Agent
Uploads audio file, gets voice response
"""

import asyncio
import sys
import os
from pathlib import Path
from livekit import rtc, api
from pydub import AudioSegment
import wave
import io
import time

# Your LiveKit credentials
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "wss://experimentaltest-ryl69z6o.livekit.cloud")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "APIRLFssgzfhU8w")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "OfikDseY0XrGc61ZseTSflnZAWQ2Ozf2JhNQWgndkpyB")

class AudioFileClient:
    def __init__(self, room_name="audio-session"):
        self.room_name = room_name
        self.room = None
        self.received_audio = []
        self.agent_joined = False
        self.greeting_finished = False
        self.response_started = False
        self.last_audio_time = 0
        self.silence_threshold = 5.0  # seconds of silence to detect end
        
    async def generate_token(self, identity):
        """Generate access token for this client"""
        token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET) \
            .with_identity(identity) \
            .with_name(identity) \
            .with_grants(api.VideoGrants(
                room_join=True,
                room=self.room_name,
                can_publish=True,
                can_subscribe=True,
            )).to_jwt()
        return token
    
    def convert_to_pcm(self, audio_file):
        """Convert audio file to PCM format for LiveKit with silence padding"""
        print(f"Converting {audio_file} to PCM...")
    
        # Load audio file
        audio = AudioSegment.from_file(audio_file)
    
        # BOOST VOLUME (VAD needs strong signal)
        audio = audio + 10  # Increase by 10dB
        print(f"  Boosted volume by 10dB")
       
        # Convert to 48kHz, mono, 16-bit PCM
        audio = audio.set_frame_rate(48000).set_channels(1).set_sample_width(2)
    
        # Normalize volume (make it as loud as possible without clipping)
        audio = audio.normalize()
        print(f"  Normalized audio volume")

        # ADD SILENCE PADDING (2 second before, 2 seconds after)
        silence_before = AudioSegment.silent(duration=2000, frame_rate=48000)  # 1 sec
        silence_after = AudioSegment.silent(duration=2000, frame_rate=48000)   # 2 sec
    
        # Combine: silence + your audio + silence
        audio = silence_before + audio + silence_after
    
        print(f"  Added silence padding for VAD detection")
    
        # Export as raw PCM
        pcm_data = audio.raw_data
    
        return pcm_data, 48000

    
    async def publish_audio_file(self, audio_file):
        """Publish audio file to the room with proper streaming"""
        print(f"\n📤 Publishing your audio: {audio_file}")
    
        pcm_data, sample_rate = self.convert_to_pcm(audio_file)
    
        # Create audio source with proper settings
        source = rtc.AudioSource(sample_rate, 1)
    
        # Create track with microphone-like properties
        track = rtc.LocalAudioTrack.create_audio_track("microphone", source)
    
        # Publish with proper options (match real microphone)
        options = rtc.TrackPublishOptions(
            source=rtc.TrackSource.SOURCE_MICROPHONE,  # Tell LiveKit this is mic
            dtx=False,  # Don't use discontinuous transmission
        )
    
        publication = await self.room.local_participant.publish_track(track, options)
        print("✓ Track published as microphone")
    
        # Wait a moment for track to be fully ready
        await asyncio.sleep(0.5)
    
        # Stream audio with consistent timing
        samples_per_frame = sample_rate // 50  # 20ms frames (50 fps)
        bytes_per_frame = samples_per_frame * 2  # 16-bit = 2 bytes per sample
    
        total_frames = len(pcm_data) // bytes_per_frame
        print(f"  Streaming {total_frames} frames...")
    
        for i in range(0, len(pcm_data), bytes_per_frame):
            chunk = pcm_data[i:i+bytes_per_frame]
        
            # Pad last chunk if needed
            if len(chunk) < bytes_per_frame:
                chunk += b'\x00' * (bytes_per_frame - len(chunk))
        
            # Create properly formatted frame
            frame = rtc.AudioFrame(
                data=chunk,
                sample_rate=sample_rate,
                num_channels=1,
                samples_per_channel=samples_per_frame
            )
        
            # Capture frame
            await source.capture_frame(frame)
        
            # Progress indicator
            if i % (bytes_per_frame * 50) == 0:  # Every second
                progress = (i / len(pcm_data)) * 100
                print(f"  Progress: {progress:.0f}%")
        
            # CRITICAL: Maintain precise 20ms timing
            await asyncio.sleep(0.02)
    
        print("✓ Finished streaming audio")
    
        # Keep publishing for agent to process
        await asyncio.sleep(3)
    
    async def save_response(self, output_file):
        """Save received audio to file"""
        if not self.received_audio:
            print("❌ No audio received from agent")
            return
        
        print(f"\n💾 Saving response to: {output_file}")
        
        combined_audio = b''.join(self.received_audio)

        # STRIP FIRST 10 SECONDS OF SILENCE
        # 48000 Hz * 2 bytes (16-bit) * 1 channel * 10 seconds = 960000 bytes
        bytes_to_skip = 48000 * 2 * 10  # 960000 bytes
    
        if len(combined_audio) > bytes_to_skip:
            combined_audio = combined_audio[bytes_to_skip:]
            print(f"  Stripped first 10 seconds of silence")
        else:
            print(f"  ⚠ Audio too short to strip, keeping as is")
        
        with wave.open(output_file, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(48000)
            wav_file.writeframes(combined_audio)
        
        print(f"✓ Response saved: {output_file}")
        
        # Show duration
        duration = len(combined_audio) / (48000 * 2)
        print(f"  Duration: {duration:.1f} seconds")
    
    async def monitor_silence(self):
        """Monitor for silence to detect when agent finishes talking"""
        while not self.greeting_finished:
            await asyncio.sleep(0.1)
            
            if self.last_audio_time > 0:
                silence_duration = time.time() - self.last_audio_time
                
                if silence_duration >= self.silence_threshold:
                    print(f"✓ Agent finished talking (silence detected)")
                    self.greeting_finished = True
                    break
    
    async def connect_and_chat(self, input_file, output_file):
        """Main function: upload audio, get response"""
        print(f"\n{'='*60}")
        print(f"🎤 Wazobia Audio Client")
        print(f"{'='*60}")
        print(f"Input:  {input_file}")
        print(f"Output: {output_file}")
        print(f"Room:   {self.room_name}")
        print(f"{'='*60}\n")
        
        token = await self.generate_token("audio-client")
        self.room = rtc.Room()
        
        # Set up event handlers
        @self.room.on("participant_connected")
        def on_participant_connected(participant):
            print(f"✓ Participant connected: {participant.identity}")
            if "agent" in participant.identity.lower():
                self.agent_joined = True
                print("🤖 Agent joined - waiting for greeting...")
        
        @self.room.on("track_subscribed")
        def on_track_subscribed(track, publication, participant):
            if track.kind == rtc.TrackKind.KIND_AUDIO:
                print(f"✓ Receiving audio from: {participant.identity}")
                audio_stream = rtc.AudioStream(track)
                asyncio.create_task(self.receive_audio(audio_stream))
        
        # Connect to room
        print("🔌 Connecting to LiveKit room...")
        await self.room.connect(LIVEKIT_URL, token)
        print("✓ Connected!\n")
        
        # Wait for agent to join
        print("⏳ Waiting for agent to join...")
        for i in range(15):
            if self.agent_joined:
                break
            await asyncio.sleep(1)
        
        if not self.agent_joined:
            print("❌ Agent didn't join. Exiting.")
            await self.room.disconnect()
            return
        
        # Wait for agent to finish greeting (silence detection)
        print("⏳ Waiting for agent to finish greeting...")
        silence_task = asyncio.create_task(self.monitor_silence())
        
        try:
            await asyncio.wait_for(silence_task, timeout=20)
        except asyncio.TimeoutError:
            print("⚠ Timeout waiting for silence, continuing anyway...")
            self.greeting_finished = True
        
        # Small pause
        await asyncio.sleep(1)
        
        # NOW publish user's audio
        self.response_started = True  # Start recording responses now
        await self.publish_audio_file(input_file)
        
        # Wait for agent's response
        print("\n⏳ Waiting for agent response...")
        response_timeout = 30
        start_wait = time.time()
        
        while time.time() - start_wait < response_timeout:
            if self.received_audio:
                print("✓ Receiving response...")
                break
            await asyncio.sleep(0.5)
        
        if self.received_audio:
            # Wait for agent to finish response (longer timeout)
            print("⏳ Waiting for complete response...")
            self.last_audio_time = time.time()
    
            # Wait longer - up to 20 seconds, looking for 5 seconds of silence
            for i in range(40):  # 20 seconds total (40 * 0.5)
                silence_duration = time.time() - self.last_audio_time
                if silence_duration >= 3.0:  # 3 seconds of silence = done
                    print("✓ Response complete (3s silence detected)")
                    break
                await asyncio.sleep(0.5)
        
                # Show progress every 5 seconds
                if i % 10 == 0 and i > 0:
                    print(f"  Still recording... ({i//2}s)")
        
        # Save response
        await self.save_response(output_file)
        
        # Disconnect
        await self.room.disconnect()
        print("\n✓ Disconnected\n")
        print(f"{'='*60}\n")
    
    async def receive_audio(self, audio_stream):
        """Receive audio frames from agent"""
        async for event in audio_stream:
            frame = event.frame
            
            # Update last audio time (for silence detection)
            self.last_audio_time = time.time()
            
            # Only record after we've sent our audio (skip greeting)
            if self.response_started:
                self.received_audio.append(frame.data.tobytes())


async def main():
    if len(sys.argv) < 2:
        print("Usage: python audio_client.py <input_audio_file> [output_audio_file]")
        print("\nExample:")
        print("  python audio_client.py question.mp3")
        print("  python audio_client.py question.wav response.wav")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "response.wav"
    
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)
    
    client = AudioFileClient(room_name=f"file-upload-{os.getpid()}")
    await client.connect_and_chat(input_file, output_file)


if __name__ == "__main__":
    asyncio.run(main())

