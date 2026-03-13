#!/usr/bin/env python3
"""
Wazobia Audio gRPC Server
Handles audio file processing via gRPC
"""

import grpc
from concurrent import futures
import asyncio
import os
import uuid
from pathlib import Path
from livekit import rtc, api
from pydub import AudioSegment
import wave
import time
import io

# Import generated gRPC code
import audio_service_pb2
import audio_service_pb2_grpc

# LiveKit credentials
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "wss://experimentaltest-ryl69z6o.livekit.cloud")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "APIRLFssgzfhU8w")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "OfikDseY0XrGc61ZseTSflnZAWQ2Ozf2JhNQWgndkpyB")

# Create directories
TEMP_DIR = Path("temp_grpc")
TEMP_DIR.mkdir(exist_ok=True)


class AudioFileClient:
    """Audio processing client - same logic as before"""
    
    def __init__(self, room_name="audio-session"):
        self.room_name = room_name
        self.room = None
        self.received_audio = []
        self.agent_joined = False
        self.greeting_finished = False
        self.response_started = False
        self.last_audio_time = 0
        self.silence_threshold = 5.0
        
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
        
        audio = AudioSegment.from_file(audio_file)
        audio = audio + 10
        print(f"  Boosted volume by 10dB")
        
        audio = audio.set_frame_rate(48000).set_channels(1).set_sample_width(2)
        audio = audio.normalize()
        print(f"  Normalized audio volume")
        
        silence_before = AudioSegment.silent(duration=2000, frame_rate=48000)
        silence_after = AudioSegment.silent(duration=2000, frame_rate=48000)
        
        audio = silence_before + audio + silence_after
        print(f"  Added silence padding for VAD detection")
        
        pcm_data = audio.raw_data
        return pcm_data, 48000
    
    async def publish_audio_file(self, audio_file):
        """Publish audio file to the room with proper streaming"""
        print(f"\n📤 Publishing audio: {audio_file}")
        
        pcm_data, sample_rate = self.convert_to_pcm(audio_file)
        source = rtc.AudioSource(sample_rate, 1)
        track = rtc.LocalAudioTrack.create_audio_track("microphone", source)
        
        options = rtc.TrackPublishOptions(
            source=rtc.TrackSource.SOURCE_MICROPHONE,
            dtx=False,
        )
        
        publication = await self.room.local_participant.publish_track(track, options)
        print("✓ Track published as microphone")
        
        await asyncio.sleep(0.5)
        
        samples_per_frame = sample_rate // 50
        bytes_per_frame = samples_per_frame * 2
        total_frames = len(pcm_data) // bytes_per_frame
        print(f"  Streaming {total_frames} frames...")
        
        for i in range(0, len(pcm_data), bytes_per_frame):
            chunk = pcm_data[i:i+bytes_per_frame]
            
            if len(chunk) < bytes_per_frame:
                chunk += b'\x00' * (bytes_per_frame - len(chunk))
            
            frame = rtc.AudioFrame(
                data=chunk,
                sample_rate=sample_rate,
                num_channels=1,
                samples_per_channel=samples_per_frame
            )
            
            await source.capture_frame(frame)
            
            if i % (bytes_per_frame * 50) == 0:
                progress = (i / len(pcm_data)) * 100
                print(f"  Progress: {progress:.0f}%")
            
            await asyncio.sleep(0.02)
        
        print("✓ Finished streaming audio")
        await asyncio.sleep(3)
    
    async def save_response(self, output_file):
        """Save received audio to file"""
        if not self.received_audio:
            print("❌ No audio received from agent")
            return False
        
        print(f"\n💾 Saving response to: {output_file}")
        
        combined_audio = b''.join(self.received_audio)
        bytes_to_skip = 48000 * 2 * 10
        
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
        
        duration = len(combined_audio) / (48000 * 2)
        print(f"  Duration: {duration:.1f} seconds")
        return True, duration
    
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
        print(f"🎤 Processing gRPC Audio Request")
        print(f"{'='*60}")
        print(f"Input:  {input_file}")
        print(f"Output: {output_file}")
        print(f"Room:   {self.room_name}")
        print(f"{'='*60}\n")
        
        token = await self.generate_token("grpc-client")
        self.room = rtc.Room()
        
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
        
        print("🔌 Connecting to LiveKit room...")
        await self.room.connect(LIVEKIT_URL, token)
        print("✓ Connected!\n")
        
        print("⏳ Waiting for agent to join...")
        for i in range(15):
            if self.agent_joined:
                break
            await asyncio.sleep(1)
        
        if not self.agent_joined:
            print("❌ Agent didn't join. Exiting.")
            await self.room.disconnect()
            return False, 0
        
        print("⏳ Waiting for agent to finish greeting...")
        silence_task = asyncio.create_task(self.monitor_silence())
        
        try:
            await asyncio.wait_for(silence_task, timeout=20)
        except asyncio.TimeoutError:
            print("⚠ Timeout waiting for silence, continuing anyway...")
            self.greeting_finished = True
        
        await asyncio.sleep(1)
        
        self.response_started = True
        await self.publish_audio_file(input_file)
        
        print("\n⏳ Waiting for agent response...")
        response_timeout = 30
        start_wait = time.time()
        
        while time.time() - start_wait < response_timeout:
            if self.received_audio:
                print("✓ Receiving response...")
                break
            await asyncio.sleep(0.5)
        
        if self.received_audio:
            print("⏳ Waiting for complete response...")
            self.last_audio_time = time.time()
            
            for i in range(40):
                silence_duration = time.time() - self.last_audio_time
                if silence_duration >= 3.0:
                    print("✓ Response complete (3s silence detected)")
                    break
                await asyncio.sleep(0.5)
                
                if i % 10 == 0 and i > 0:
                    print(f"  Still recording... ({i//2}s)")
        
        success, duration = await self.save_response(output_file)
        
        await self.room.disconnect()
        print("\n✓ Disconnected\n")
        print(f"{'='*60}\n")
        
        return success, duration
    
    async def receive_audio(self, audio_stream):
        """Receive audio frames from agent"""
        async for event in audio_stream:
            frame = event.frame
            self.last_audio_time = time.time()
            
            if self.response_started:
                self.received_audio.append(frame.data.tobytes())


class AudioServiceServicer(audio_service_pb2_grpc.AudioServiceServicer):
    """gRPC service implementation"""
    
    def ProcessAudio(self, request, context):
        """Process audio file and return response"""
        print(f"\n{'='*60}")
        print(f"📥 gRPC ProcessAudio request received")
        print(f"{'='*60}")
        
        # Generate unique ID for this request
        request_id = str(uuid.uuid4())[:8]
        
        # Save input audio to temp file
        input_filename = f"{request_id}_input.{request.format}"
        input_path = TEMP_DIR / input_filename
        
        with open(input_path, 'wb') as f:
            f.write(request.audio_data)
        
        print(f"✓ Saved input: {input_path} ({len(request.audio_data)} bytes)")
        
        # Prepare output path
        output_filename = f"{request_id}_response.wav"
        output_path = TEMP_DIR / output_filename
        
        # Process audio (run async code in sync context)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            client = AudioFileClient(room_name=f"grpc-{request_id}")
            success, duration = loop.run_until_complete(
                client.connect_and_chat(str(input_path), str(output_path))
            )
            
            if not success or not output_path.exists():
                return audio_service_pb2.AudioResponse(
                    audio_data=b'',
                    format='wav',
                    duration=0,
                    success=False,
                    error_message="Failed to get response from agent"
                )
            
            # Read response audio
            with open(output_path, 'rb') as f:
                response_audio = f.read()
            
            print(f"✓ Sending response: {len(response_audio)} bytes, {duration:.1f}s")
            
            return audio_service_pb2.AudioResponse(
                audio_data=response_audio,
                format='wav',
                duration=duration,
                success=True,
                error_message=''
            )
            
        except Exception as e:
            print(f"❌ Error processing request: {e}")
            return audio_service_pb2.AudioResponse(
                audio_data=b'',
                format='wav',
                duration=0,
                success=False,
                error_message=str(e)
            )
            
        finally:
            # Cleanup temp files
            if input_path.exists():
                input_path.unlink()
            if output_path.exists():
                output_path.unlink()
            loop.close()
    
    def HealthCheck(self, request, context):
        """Health check endpoint"""
        print(f"📊 Health check requested")
        return audio_service_pb2.HealthResponse(
            healthy=True,
            status="running",
            service="wazobia-audio-grpc-server"
        )


def serve():
    """Start gRPC server"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    audio_service_pb2_grpc.add_AudioServiceServicer_to_server(
        AudioServiceServicer(), server
    )
    
    server.add_insecure_port('[::]:50051')
    
    print("\n" + "="*60)
    print("🚀 Starting Wazobia Audio gRPC Server")
    print("="*60)
    print(f"Server listening on: localhost:50051")
    print(f"Protocol: gRPC")
    print(f"Services:")
    print(f"  - ProcessAudio  (process audio file)")
    print(f"  - HealthCheck   (check server health)")
    print("="*60 + "\n")
    
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
