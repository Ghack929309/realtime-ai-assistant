from __future__ import annotations

import dotenv
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.agents.multimodal import MultimodalAgent
from livekit.plugins import openai

from src.api import AssistantFunction
from src.prompts import WELCOME_MESSAGE

# Load environment variables (if any)
dotenv.load_dotenv()


async def entrypoint(ctx: JobContext) -> None:
    # Connect to the LiveKit room and wait for participants
    await ctx.connect(auto_subscribe=AutoSubscribe.SUBSCRIBE_ALL)
    await ctx.wait_for_participant()

    # Instantiate your local LLM using Ollama.
    # Adjust the model name ("llama3.1") and base_url (port/path) as needed.
    model = openai.LLM.with_ollama(
        model="llama3.1", base_url="http://localhost:11023/v1"
    )

    # Create an instance of your assistant functions
    assistant_fnc = AssistantFunction()

    # Instantiate the multimodal agent with your local LLM
    assistant = MultimodalAgent(
        model=model,
        fnc_ctx=assistant_fnc,
    )
    assistant.start(ctx.room)

    # Create a new conversation session with a welcome message.
    # (Assumes your LLM instance supports a sessions list.)
    session = model.sessions[0]
    session.conversation.item.create(
        llm.ChatMessage(
            role="assistant",
            content=WELCOME_MESSAGE,
        )
    )
    session.response.create()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
