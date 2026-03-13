#!/usr/bin/env python3
"""
Simple HTTP Client for Wazobia Audio Server
Uploads audio file and downloads response
"""

import requests
import sys
import os
from pathlib import Path

# Server URL
SERVER_URL = "http://localhost:8000"

def chat(input_file, output_file=None):
    """
    Send audio file to server and get response
    
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
    
    print(f"\n{'='*60}")
    print(f"🎤 Wazobia Audio Client")
    print(f"{'='*60}")
    print(f"Server:  {SERVER_URL}")
    print(f"Input:   {input_file}")
    print(f"Output:  {output_file}")
    print(f"{'='*60}\n")
    
    try:
        # Upload audio file
        print("📤 Uploading audio to server...")
        
        with open(input_file, 'rb') as f:
            files = {'audio': (Path(input_file).name, f, 'audio/mpeg')}
            
            response = requests.post(
                f"{SERVER_URL}/chat",
                files=files,
                timeout=120  # 2 minutes timeout
            )
        
        if response.status_code == 200:
            # Save response audio
            print("✓ Received response from server")
            print(f"💾 Saving response to: {output_file}")
            
            with open(output_file, 'wb') as f:
                f.write(response.content)
            
            print(f"✓ Response saved successfully!")
            print(f"\n{'='*60}\n")
            return True
            
        else:
            print(f"❌ Server error: {response.status_code}")
            print(f"   {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Cannot connect to server at {SERVER_URL}")
        print(f"   Is the server running? Start with: python server.py")
        return False
        
    except requests.exceptions.Timeout:
        print(f"❌ Error: Request timed out")
        print(f"   The server took too long to respond")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def check_health():
    """Check if server is running"""
    try:
        response = requests.get(f"{SERVER_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"✓ Server is running at {SERVER_URL}")
            return True
        else:
            print(f"⚠ Server returned status: {response.status_code}")
            return False
    except:
        print(f"❌ Server is not running at {SERVER_URL}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python simple_client.py <input_audio_file> [output_audio_file]")
        print("\nExamples:")
        print("  python simple_client.py question.mp3")
        print("  python simple_client.py question.wav response.wav")
        print("\nCommands:")
        print("  python simple_client.py --health    Check server status")
        sys.exit(1)
    
    # Check health command
    if sys.argv[1] == "--health":
        check_health()
        sys.exit(0)
    
    # Process audio
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = chat(input_file, output_file)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
