from dotenv import load_dotenv
from livekit import agents, rtc
from livekit.agents import Agent, AgentSession, RunContext, RoomInputOptions
from livekit.agents.llm import function_tool
from livekit.plugins import openai
from datetime import datetime
import json
import os
import asyncio
from pathlib import Path

# Load environment variables
load_dotenv(".env")

class SateAssistant(Agent):
    """Healthcare assistant that speaks Nigerian Pidgin and helps with symptom recognition."""

    def __init__(self, transcript_file: str = None):
        super().__init__(
            instructions="""You are Wazobia, a friendly and helpful multilingual voice customer support agent. You communicate naturally through spoken conversation.

            Language Capabilities
            You speak fluently in:
            - English
            - Yoruba
            - Hausa
            - Nigerian Pidgin
            - Igbo

            Language Switching - CRITICAL RULE
            ALWAYS respond immediately in the exact language the customer is speaking. When the customer switches languages during the call, immediately switch to that language. Listen carefully to detect which language they're using and match it instantly.

            Voice Conversation Guidelines
            - Keep responses SHORT and conversational (2-3 sentences at a time)
            - Speak naturally as if having a real phone conversation
            - Use verbal acknowledgments like "okay", "I see", "mm-hmm", "Naso", "chai" to show you're listening
            - Pause appropriately to let customers speak
            - Don't read out lists or long explanations - break information into digestible chunks
            - Ask one question at a time
            - Avoid saying things like "let me explain:" or "here are the steps:" - just speak naturally

            Your Personality
            - Warm and patient, like talking to a helpful friend
            - Professional but approachable
            - Empathetic and understanding
            - Use natural greetings appropriate to each language and Nigerian culture
            - Match the customer's energy and pace

            Handling Issues
            - Listen actively and confirm understanding
            - Ask clarifying questions naturally
            - Provide clear, simple solutions
            - Check if the customer needs anything else before ending

            Remember: You're having a real-time voice conversation. Be natural, be brief, and be helpful.
            it's very important to always respond in or switch to the language the customer is using immediately.
            """
        )

        # Symptom log storage
        self.symptom_logs = []

        # Transcript file path
        self.transcript_file = transcript_file
        self.transcript_lock = asyncio.Lock()

    async def log_transcript(self, speaker: str, message: str):
        """Log conversation to transcript file in English.

        Args:
            speaker: Who is speaking (user, agent, system)
            message: The message content (should be in English for logging)
        """
        if not self.transcript_file:
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "speaker": speaker,
            "message": message
        }

        async with self.transcript_lock:
            try:
                # Append to transcript file
                with open(self.transcript_file, "a", encoding="utf-8") as f:
                    f.write(f"[{timestamp}] {speaker}: {message}\n")
                    f.write("\n")
            except Exception as e:
                print(f"Error logging transcript: {e}")

    @function_tool
    async def get_current_date_and_time(self, context: RunContext) -> str:
        """Get the current date and time for logging purposes."""
        current_datetime = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        return f"Today na {current_datetime}"

async def entrypoint(ctx: agents.JobContext):
    """Entry point for the sate assistant."""

    # Create transcripts directory if it doesn't exist
    transcripts_dir = Path("transcripts")
    transcripts_dir.mkdir(exist_ok=True)

    # Create unique transcript file for this session
    session_id = ctx.room.name or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    transcript_file = transcripts_dir / f"{session_id}_transcript.txt"

    # Initialize transcript file with session header
    with open(transcript_file, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("SATE ASSISTANT - SESSION TRANSCRIPT\n")
        f.write("=" * 80 + "\n")
        f.write(f"Session ID: {session_id}\n")
        f.write(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")

    print(f"Transcript will be saved to: {transcript_file}")

    # Create agent instance with transcript file
    agent = SateAssistant(transcript_file=str(transcript_file))

    # Option 2: Using OpenAI Realtime Model
    session = AgentSession(
        llm=openai.realtime.RealtimeModel(voice="sage"),
    )

    # Set up event handlers for transcript logging
    @session.on("user_speech_committed")
    def on_user_speech(ev):
        """Log user speech to transcript"""
        if hasattr(ev, 'alternatives') and ev.alternatives:
            # Get the transcribed text
            user_text = ev.alternatives[0].text
            asyncio.create_task(
                agent.log_transcript("USER", user_text)
            )

    @session.on("agent_speech_committed")
    def on_agent_speech(ev):
        """Log agent speech to transcript"""
        if hasattr(ev, 'message'):
            # Log agent response (in Pidgin)
            agent_text = ev.message
            asyncio.create_task(
                agent.log_transcript("AGENT", agent_text)
            )

    @session.on("function_calls_finished")
    def on_function_calls(ev):
        """Log function calls to transcript"""
        if hasattr(ev, 'called_functions'):
            for func_call in ev.called_functions:
                func_name = func_call.name if hasattr(func_call, 'name') else 'unknown'
                asyncio.create_task(
                    agent.log_transcript(
                        "SYSTEM",
                        f"Function called: {func_name}"
                    )
                )

    # Start the session
    await session.start(
        room=ctx.room,
        agent=agent,
        room_input_options=RoomInputOptions(
            # noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Log session start
    await agent.log_transcript("SYSTEM", "Session started")

    # Generate initial greeting in Pidgin
    await session.generate_reply(
        instructions="""Greet the user warmly in Nigerian wazobia (a combination of Hausa, Yoruba, and Igbo).
        Introduce yourself as wazobia and explain that you can help them briefly with their issues.
        Keep it natural, warm, and compassionate."""
    )

    # Log initial greeting
    await agent.log_transcript("SYSTEM", "Initial greeting sent to user")


if __name__ == "__main__":
    # Run the agent
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
