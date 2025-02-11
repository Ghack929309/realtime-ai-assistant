from __future__ import annotations

import dotenv
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.agents.multimodal import MultimodalAgent
from livekit.plugins import openai

from src.api import AssistantFunction
from src.prompts import INSTRUCTIONS, WELCOME_MESSAGE

dotenv.load_dotenv()


async def entrypoint(ctx: JobContext) -> None:
    await ctx.connect(auto_subscribe=AutoSubscribe.SUBSCRIBE_ALL)
    await ctx.wait_for_participant()

    model = openai.realtime.RealtimeModel(
        instructions=INSTRUCTIONS,
        voice="shimmer",
        temperature=0.8,
        modalities=["audio", "text"],
    )
    assistant_fnc = AssistantFunction()
    assistant = MultimodalAgent(
        model=model,
        fnc_ctx=assistant_fnc,
    )
    assistant.start(ctx.room)

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
