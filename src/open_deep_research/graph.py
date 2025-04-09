import uuid
import asyncio
import open_deep_research
from langgraph.checkpoint.memory import MemorySaver
from open_deep_research.graph import builder
from langgraph.types import Command
from dotenv import load_dotenv


async def process_graph():
    memory = MemorySaver()
    graph = builder.compile(checkpointer=memory)

    # Define the thread configuration
    thread = {
        "configurable": {
            "thread_id": str(uuid.uuid4()),
            "search_api": "tavily",
            "planner_provider": "nvidia",
            "planner_model": "meta/llama-3.1-70b-instruct",
            "writer_provider": "nvidia",
            "writer_model": "meta/llama-3.1-70b-instruct",
            "max_search_depth": 1,
        }
    }

    topic = "Overview of the AI inference market with focus on Fireworks, Together.ai, Groq"

    # Stream updates based on the topic
    try:
        async for event in graph.astream({"topic": topic}, thread, stream_mode="updates"):
            print(event)

        # Additional Command examples
        async for event in graph.astream(Command(resume="Include a revenue estimate (ARR) in the sections"), thread, stream_mode="updates"):
            print(event)

        async for event in graph.astream(Command(resume=True), thread, stream_mode="updates"):
            print(event)
    except Exception as e:
        print(f"Error during streaming: {e}")

# Run the async function
asyncio.run(process_graph())
