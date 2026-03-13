#!/usr/bin/env python3
"""
Wazobia Audio gRPC Client
Simple client to send audio and receive response via gRPC
"""

import grpc
import sys
import os
from pathlib import Path

# Import generated gRPC code
import audio_service_pb2
import audio_service_pb2_grpc

# Server address
SERVER_ADDRESS = 'localhost:50051'


def process_audio(input_file, output_file=None):
    """
    Send audio file to gRPC server and get response
    
    Args:
        input_file: Path to input audio file
        output_file: Path to save response (optional)
    """
    if not os.path.exists(input_file):
        print(f"❌ Error: Input file not found: {input_file}")
        return False
    
    # Default output filename
    if not output_file:
        output_file = f"response_{Path(input_file).stem}.wav"
    
    # Get file format
    file_format = Path(input_file).suffix.lstrip('.')
    
    print(f"\n{'='*60}")
    print(f"🎤 Wazobia gRPC Audio Client")
    print(f"{'='*60}")
    print(f"Server:  {SERVER_ADDRESS}")
    print(f"Input:   {input_file}")
    print(f"Output:  {output_file}")
    print(f"{'='*60}\n")
    
    try:
        # Read input audio file
        print("📖 Reading input audio...")
        with open(input_file, 'rb') as f:
            audio_data = f.read()
        
        print(f"✓ Read {len(audio_data)} bytes")
        
        # Create gRPC channel
        print(f"🔌 Connecting to gRPC server at {SERVER_ADDRESS}...")
        
        with grpc.insecure_channel(SERVER_ADDRESS) as channel:
            stub = audio_service_pb2_grpc.AudioServiceStub(channel)
            
            # Create request
            request = audio_service_pb2.AudioRequest(
                audio_data=audio_data,
                filename=Path(input_file).name,
                format=file_format
            )
            
            print("📤 Sending audio to server...")
            print("⏳ Waiting for response (this may take 30-60 seconds)...")
            
            # Call gRPC method with timeout
            response = stub.ProcessAudio(request, timeout=120)
            
            if response.success:
                print(f"✓ Received response from server")
                print(f"  Duration: {response.duration:.1f} seconds")
                print(f"  Size: {len(response.audio_data)} bytes")
                
                # Save response audio
                print(f"💾 Saving response to: {output_file}")
                with open(output_file, 'wb') as f:
                    f.write(response.audio_data)
                
                print(f"✓ Response saved successfully!")
                print(f"\n{'='*60}\n")
                return True
                
            else:
                print(f"❌ Server returned error: {response.error_message}")
                return False
                
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.UNAVAILABLE:
            print(f"❌ Error: Cannot connect to gRPC server at {SERVER_ADDRESS}")
            print(f"   Is the server running? Start with: python audio_server_grpc.py")
        elif e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
            print(f"❌ Error: Request timed out")
            print(f"   The server took too long to respond")
        else:
            print(f"❌ gRPC Error: {e.code()} - {e.details()}")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def check_health():
    """Check if gRPC server is running"""
    try:
        with grpc.insecure_channel(SERVER_ADDRESS) as channel:
            stub = audio_service_pb2_grpc.AudioServiceStub(channel)
            
            request = audio_service_pb2.HealthRequest(service="wazobia")
            response = stub.HealthCheck(request, timeout=5)
            
            if response.healthy:
                print(f"✓ Server is running at {SERVER_ADDRESS}")
                print(f"  Status: {response.status}")
                print(f"  Service: {response.service}")
                return True
            else:
                print(f"⚠ Server unhealthy: {response.status}")
                return False
                
    except grpc.RpcError:
        print(f"❌ gRPC server is not running at {SERVER_ADDRESS}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python audio_client_grpc.py <input_audio_file> [output_audio_file]")
        print("\nExamples:")
        print("  python audio_client_grpc.py question.mp3")
        print("  python audio_client_grpc.py question.wav response.wav")
        print("\nCommands:")
        print("  python audio_client_grpc.py --health    Check server status")
        sys.exit(1)
    
    # Check health command
    if sys.argv[1] == "--health":
        check_health()
        sys.exit(0)
    
    # Process audio
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = process_audio(input_file, output_file)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
