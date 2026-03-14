# 🎤 Wazobia Multilingual Voice Agent

> AI-powered voice assistant supporting English, Yoruba, Hausa, Nigerian Pidgin, and Igbo - deployed on SingularityNET decentralized AI marketplace.

## This repo is ONLY meant for SNET testnet deployment. And used by dedicated users.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![gRPC](https://img.shields.io/badge/gRPC-1.x-green.svg)](https://grpc.io/)
[![LiveKit](https://img.shields.io/badge/LiveKit-Enabled-orange.svg)](https://livekit.io/)
[![SingularityNET](https://img.shields.io/badge/SingularityNET-Ready-purple.svg)](https://singularitynet.io/)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Services](#running-the-services)
- [API Interfaces](#api-interfaces)
- [SingularityNET Integration](#singularitynet-integration)
- [Development](#development)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## 🌟 Overview

**Wazobia Voice Agent** is a multilingual AI voice assistant that:
- Accepts audio input in multiple African languages
- Processes queries using OpenAI's Realtime API
- Returns audio responses in the same language
- Supports real-time voice conversations via LiveKit
- Provides multiple API interfaces (gRPC, REST, File-based)
- Deployed on SingularityNET decentralized marketplace

**Supported Languages:**
- 🇬🇧 English
- 🇳🇬 Yoruba
- 🇳🇬 Hausa
- 🇳🇬 Nigerian Pidgin
- 🇳🇬 Igbo

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Applications                       │
│  (Browser UI, Mobile Apps, Command Line, SNET Marketplace)  │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
       ┌───────▼────────┐            ┌───────▼────────┐
       │  gRPC Server   │            │  REST Server   │
       │  (Port 50051)  │            │  (Port 8000)   │
       └───────┬────────┘            └───────┬────────┘
               │                              │
               └──────────────┬───────────────┘
                              │
                     ┌────────▼─────────┐
                     │  SNET Daemon     │
                     │  (Port 10000)    │
                     └────────┬─────────┘
                              │
                     ┌────────▼─────────┐
                     │  Audio Processor │
                     │  (LiveKit)       │
                     └────────┬─────────┘
                              │
               ┌──────────────┼──────────────┐
               │              │              │
       ┌───────▼──────┐  ┌───▼────┐  ┌─────▼──────┐
       │   LiveKit    │  │ OpenAI │  │  Storage   │
       │  Cloud/Self  │  │   API  │  │ (Transcr.) │
       └──────────────┘  └────────┘  └────────────┘
```

### Components:

1. **Wazobia Agent** (`deepfunding_agent.py`)
   - Core voice processing engine
   - LiveKit + OpenAI Realtime API integration
   - Automatic language detection
   - Runs as systemd service

2. **gRPC Server** (`audio_server_grpc.py`)
   - File-based audio processing
   - Protobuf message format
   - High-performance binary protocol
   - SingularityNET compatible

3. **REST API Server** (`server.py`)
   - HTTP-based interface
   - FastAPI framework
   - File upload/download
   - Web-friendly

4. **SNET Daemon** (`snetd`)
   - Blockchain integration
   - Payment channel management
   - Service discovery
   - Authentication

5. **Web UI** (`ui/`)
   - React-based interface
   - Audio upload/playback
   - SingularityNET marketplace integration
   - Mobile responsive

---

## ✨ Features

### Core Capabilities
- ✅ **Multilingual Voice Processing** - 5 African languages
- ✅ **Real-time Conversations** - Live voice chat via LiveKit
- ✅ **File-based Processing** - Upload audio, get response
- ✅ **Automatic Language Detection** - No manual selection needed
- ✅ **Voice Activity Detection** - Smart silence detection
- ✅ **Audio Normalization** - Optimized for speech recognition
- ✅ **Transcript Logging** - All conversations saved

### API Interfaces
- ✅ **gRPC API** - High-performance binary protocol
- ✅ **REST API** - HTTP-based, web-friendly
- ✅ **WebSocket** - Real-time bidirectional (LiveKit)
- ✅ **Command Line** - Terminal-based clients

### Deployment Options
- ✅ **SingularityNET** - Decentralized AI marketplace
- ✅ **VPS Deployment** - Self-hosted on any server
- ✅ **Docker** - Containerized deployment
- ✅ **Systemd Service** - Production-ready daemon

---

## 📦 Prerequisites

### System Requirements
- **OS:** Ubuntu 20.04/22.04/24.04 (or compatible Linux)
- **CPU:** 2+ cores recommended
- **RAM:** 4GB minimum, 8GB recommended
- **Storage:** 10GB free space
- **Network:** Stable internet connection

### Required Software
- **Python:** 3.9 or higher
- **Node.js:** 14+ (for UI development)
- **Git:** For repository management
- **FFmpeg:** Audio processing
- **PortAudio:** Audio I/O library

### API Keys & Services
- **LiveKit Account** - [Sign up](https://livekit.io)
  - LiveKit URL
  - API Key
  - API Secret
- **OpenAI API Key** - [Get key](https://platform.openai.com/api-keys)
  - Realtime API access required
  - Sufficient credits/quota
- **Ethereum Wallet** (for SingularityNET)
  - Private key for transactions
  - ETH for gas fees (Sepolia testnet or Mainnet)

---

## 🚀 Installation

### 1. Clone Repository
oriinal repo from Team Eusate
```bash
git clone https://github.com/EUSATE/Deepfunding-Hackathon.git
```

### 2. Install System Dependencies

```bash
# Update package list
sudo apt update

# Install Python and build tools
sudo apt install -y python3 python3-pip python3-venv

# Install audio libraries
sudo apt install -y portaudio19-dev python3-pyaudio libasound2-dev \
    build-essential python3-dev ffmpeg

# Install other tools
sudo apt install -y git curl tmux
```

### 3. Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### 4. Install Python Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

### 5. Install SNET Tools (for SingularityNET deployment)

```bash
# Install SNET CLI
pip install snet-cli

# Install SNET Daemon
cd ~
wget https://github.com/singnet/snet-daemon/releases/latest/download/snetd-linux-amd64
chmod +x snetd-linux-amd64
sudo mv snetd-linux-amd64 /usr/local/bin/snetd

# Verify installation
snet --version
snetd version
```

---

## ⚙️ Configuration

### 1. Environment Variables

Create `.env` file:

```bash
cp .env.example .env
nano .env
```

Add your credentials:

```env
# LiveKit Configuration
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=APIxxxxxxxxxxxxxxxxx
LIVEKIT_API_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# OpenAI Configuration
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 2. SNET Daemon Configuration (Optional)

Edit `snet.config.json`:


### 3. Generate Protocol Buffers from "audio_service.proto"

```bash
# Python stubs
python -m grpc_tools.protoc \
  -I. \
  --python_out=. \
  --grpc_python_out=. \
  audio_service.proto

# JavaScript stubs (for UI)
npm install -g grpc-tools
npx grpc_tools_node_protoc \
  -I=. \
  --js_out=import_style=commonjs,binary:./ui \
  --grpc_out=grpc_js:./ui \
  audio_service.proto
```

---

## 🎮 Running the Services

### Quick Start (Development)

```bash
# Activate virtual environment
source venv/bin/activate

# Start Wazobia agent
python deepfunding_agent.py start
```

### Production Setup (Systemd + Tmux)

#### 1: Systemd Service (Wazobia Agent)

```bash
# Create systemd service
sudo nano /etc/systemd/system/wazobia-agent.service
```

Add:

```ini
[Unit]
Description=Wazobia Voice Agent
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/wazobia-voice-agent
Environment="PATH=/home/YOUR_USERNAME/wazobia-voice-agent/venv/bin"
ExecStart=/home/YOUR_USERNAME/wazobia-voice-agent/venv/bin/python deepfunding_agent.py start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable wazobia-agent
sudo systemctl start wazobia-agent
sudo systemctl status wazobia-agent
```

#### 2: Tmux Sessions (gRPC + SNET Daemon)

Manual tmux commands:

```bash
# Start gRPC server
tmux new-session -d -s grpc-server
tmux send-keys -t grpc-server "cd ~/wazobia-voice-agent" C-m
tmux send-keys -t grpc-server "source venv/bin/activate" C-m
tmux send-keys -t grpc-server "python audio_server_grpc.py" C-m

# Start SNET daemon
tmux new-session -d -s snetd
tmux send-keys -t snetd "cd ~/wazobia-voice-agent" C-m
tmux send-keys -t snetd "sudo snetd --config snet.config.json" C-m

# Attach to view logs
tmux attach -t grpc-server
# Press Ctrl+b then d to detach
```

---

## 🔌 API Interfaces (If tests need to be run to test grpc server)

can you bank.mp3 for testing

### 1. gRPC API (Port 50051)

**Python Client:**

```python
python audio_client_grpc.py input_audio.mp3 response.wav
```


### 2. REST API (Port 8000) - Initial REST setup

**Python Client:**

```bash
python simple_client.py input_audio.mp3 response.wav
```


### 3. LiveKit WebSocket (Real-time)-  Test realtime convo interractions

Connect via LiveKit SDK or browser at:
```
https://meet.livekit.io
```

Enter your LiveKit credentials and join a room.

---

##   Deploy UI

Copy UI files to SingularityNET DApp:

```bash
# UI files location
ui/
├── index.js
├── style.css
├── audio_service_pb.js
└── audio_service_pb_service.js
```

Zip UI files.


--- 

## 💻 Development

### Project Structure

```
wazobia-voice-agent/
├── deepfunding_agent.py          # Main agent (LiveKit + OpenAI)
├── audio_server_grpc.py           # gRPC server
├── audio_client_grpc.py           # gRPC client
├── server.py                      # REST API server
├── simple_client.py               # REST client
├── audio_client.py                # Standalone client
├── audio_service.proto            # Protocol definition
├── snet.config.json               # SNET daemon config
├── manage-services.sh             # Service management script
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment template
├── .gitignore                     # Git ignore rules
├── README.md                      # This file
├── ui/                            # Web interface
│   ├── index.js
│   ├── style.css
│   ├── audio_service_pb.js
│   └── audio_service_pb_service.js
```

### Note all needed files for service setup on the marketplace are in the repo but might not be displayed in this directory tree.

### Running Tests

```bash
# Test gRPC server
python audio_client_grpc.py test_audio.mp3

# Test REST server
python simple_client.py test_audio.mp3

# Health check
curl http://localhost:8000/health
```

### Adding New Languages

Edit `deepfunding_agent.py`:

```python
instructions="""
You speak fluently in:
- English
- Yoruba
- Hausa
- Nigerian Pidgin
- Igbo
- [ADD NEW LANGUAGE HERE]
"""
```

---

## 🚢 Deployment

### VPS Deployment

1. **Provision VPS** (DigitalOcean, Linode, AWS EC2, etc.)
2. **Install dependencies** (follow Installation section)
3. **Configure environment** (add API keys)
4. **Setup systemd services**
5. **Configure firewall**:
   ```bash
   sudo ufw allow 22/tcp      # SSH
   sudo ufw allow 50051/tcp   # gRPC
   sudo ufw allow 8000/tcp    # REST API
   sudo ufw allow 10000/tcp   # SNET Daemon
   sudo ufw enable
   ```
6. **Setup SSL** (for production):
   ```bash
   sudo apt install certbot
   sudo certbot certonly --standalone -d your-domain.com
   ```

### Docker Deployment (Coming Soon)

```bash
docker-compose up -d
```

---

## 🐛 Troubleshooting

### Common Issues

**1. Port Already in Use**
```bash
# Check what's using the port
sudo lsof -i :50051

# Kill process
sudo kill -9 PID
```

**2. PortAudio Not Found**
```bash
sudo apt install portaudio19-dev python3-pyaudio
pip install --force-reinstall livekit-agents
```

**3. Agent Not Responding**
```bash
# Check agent logs
sudo journalctl -u wazobia-agent -f

# Verify LiveKit credentials
grep LIVEKIT .env
```

**4. Audio File Not Processed**
- Ensure file is valid audio format (mp3, wav, m4a)
- Check file size < 10MB
- Verify agent is running
- Check gRPC server logs

**5. SNET Daemon Connection Failed**
```bash
# Check daemon status
sudo snetd --config snet.config.json

### Debug Mode

Enable debug logging:

```bash
# In deepfunding_agent.py, set log level:
log_level = "debug"

# Restart service
sudo systemctl restart wazobia-agent
```

### Support Resources

- [LiveKit Documentation](https://docs.livekit.io)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [SingularityNET Dev Portal](https://dev.singularitynet.io)
- [gRPC Documentation](https://grpc.io/docs)

---

## 📊 Performance

- **Latency:** ~2-5 seconds (depends on audio length)
- **Concurrent Users:** 5-10 (single server)
- **Audio Formats:** mp3, wav, m4a, ogg
- **Max Audio Size:** 10MB
- **Languages:** 5 (expandable)

---

## 🔐 Security

- API keys stored in `.env` (never committed)
- SSL/TLS for production endpoints
- SNET daemon handles authentication
- No audio stored permanently (optional transcript logging)
- Rate limiting recommended for production

---


## 📜 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🙏 Acknowledgments

- **LiveKit** - Real-time communication infrastructure
- **OpenAI** - Realtime API and speech processing
- **SingularityNET** - Decentralized AI marketplace
- **Eusate Team** - Original project creators
- **Community** - Contributors and testers

---
