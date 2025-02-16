from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
import os
import re
from typing import AsyncIterable

import dotenv

from livekit.agents import (
    AutoSubscribe,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    llm,
)
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import deepgram, google, openai, silero, turn_detector

from db import DB_queries
from src.functions import AssistantFunction
from src.prompts import INSTRUCTIONS, WELCOME_MESSAGE

dotenv.load_dotenv()
db = DB_queries()

google_credentials_path = os.path.abspath("./google_credentials.json")


stt = deepgram.STT(
    model="nova-2-general",
    interim_results=True,
    smart_format=True,
    punctuate=False,
    filler_words=True,
    profanity_filter=False,
    language="fr",
    api_key=os.getenv("DEEPGRAM_API_KEY"),
)
tts = google.TTS(
    gender="female",
    language="fr-CA",
    # punctuation=True,
    # voice_name="fr-CA-Chirp-HD-F",
    voice_name="fr-CA-Chirp-HD-O",
    # credentials_info=google_credentials_values,
    credentials_file=google_credentials_path,
)

# tts = deepgram.TTS(
#     model="aura-stella-en",  # Changed to English voice
#     api_key=os.getenv("DEEPGRAM_API_KEY"),  # Add this
# )


def clean_text_for_tts(
    assistant: VoicePipelineAgent, text: str | AsyncIterable[str]
) -> str | AsyncIterable[str]:
    """Sanitizes text for TTS by removing Markdown formatting and special characters."""
    EMOJI_PATTERN = r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\u2600-\u26FF\u2700-\u27BF]+"

    async def _process_chunks():
        async for chunk in text:
            chunk = re.sub(r"\!?\[([^\]]*)\]\([^)]*\)", r"\1", chunk)
            chunk = re.sub(r"`{1,3}(.*?)`{1,3}", r"\1", chunk)
            chunk = re.sub(r"\s*[*_]+\s*(.*?)\s*[*_]+\s*", r"\1", chunk)
            chunk = re.sub(r"^#{1,6}\s*", "", chunk, flags=re.MULTILINE)
            chunk = re.sub(r"<[^>]+>", "", chunk)
            chunk = re.sub(EMOJI_PATTERN, "", chunk)
            yield chunk

    if isinstance(text, str):
        text = re.sub(r"\!?\[([^\]]*)\]\([^)]*\)", r"\1", text)
        text = re.sub(r"`{1,3}(.*?)`{1,3}", r"\1", text)
        text = re.sub(r"\s*[*_]+\s*(.*?)\s*[*_]+\s*", r"\1", text)
        text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
        text = re.sub(r"<[^>]+>", "", text)
        text = re.sub(EMOJI_PATTERN, "", text)
        return text

    return _process_chunks()




def prewarm(proc: JobProcess) -> None:
    proc.userdata["vad"] = silero.VAD.load()
    proc.userdata["stt"] = stt
    proc.userdata["tts"] = tts


async def entrypoint(ctx: JobContext) -> None:
    # Connect to LiveKit and set up the participant
    async with lifespan():
        print("Initializing lifespan")
    await ctx.connect(auto_subscribe=AutoSubscribe.SUBSCRIBE_ALL)
    participant = await ctx.wait_for_participant()
    
    init_chat_ctx = llm.ChatContext().append(
        text=INSTRUCTIONS,
        role="system",
    )
    assistant_fnc = AssistantFunction()

    agent = VoicePipelineAgent(
        llm=openai.LLM.with_ollama(
            model="llama3.1:latest",
            base_url="http://localhost:11434/v1",
            # model="dolphin-2.2.1-mistral-7b",
            # base_url="http://localhost:1234/v1",
            temperature=8,
            parallel_tool_calls=False,
            tool_choice="auto",
        ),
        vad=silero.VAD.load(),
        turn_detector=turn_detector.EOUModel(),
        stt=stt,
        tts=tts,
        fnc_ctx=assistant_fnc,
        chat_ctx=init_chat_ctx,
        interrupt_speech_duration=0.5,
        interrupt_min_words=3,
        # minimal silence duration to consider end of turn
        min_endpointing_delay=0.5,
    )

    # @ctx.room.on("transcription_received")
    # def on_participant_connected(participant: rtc.RemoteParticipant):
    #     data = participant.track_publications()
    #     print("words", data)
    #     # agent.interrupt(interrupt_all=True)
    await asyncio.sleep(1)
    agent.start(ctx.room, participant)

    await agent.say(WELCOME_MESSAGE)


@asynccontextmanager
async def lifespan():
    """Initialize the database connection and index."""
    await db.initialize()

    try:
        yield
    except Exception as e:
        print(f"❌ Lifespan failed: {str(e)}")
    

if __name__ == "__main__":

    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
