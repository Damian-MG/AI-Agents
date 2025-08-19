"""
This file implements de MCP Client for a Langgraph Agent

MCP clients are responsible for connecting and communicating with MCP servers.
This client is analogous to Cursor or Claude Desktop and you would configure
them in the same way by specifying the MCP server configuration in 
mcp_config.json
"""

from typing import AsyncGenerator
from langchain_core.messages import HumanMessage, AIMessageChunk
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph
from my_mcp.config import mcp_config
from graph import build_agent_graph, AgentState


async def stream_graph_response(
        input: AgentState, graph: StateGraph, config: dict = {}
        ) -> AsyncGenerator[str, None]:
    """
    Stream the response from the graph while parsing out tool calls.

    Args:
        input: The input for the graph
        graph: The graph to run
        config: The config to pass to the graph. Required for memory

    Yields:
        A processed string from the graph's chunked response
    """
    async for message_chunk, metadata in graph.astream(
            input=input,
            stream_mode="messages",
            config=config
    ):
        if isinstance(message_chunk, AIMessageChunk):
            if message_chunk.response_metadata:
                finish_reason = message_chunk.response_metadata.get(
                    "finish_reason", "")
                if finish_reason == "tool_calls":
                    yield "\n\n"

            if message_chunk.tool_call_chunks:
                tool_chunk = message_chunk.tool_call_chunks[0]
                tool_name = tool_chunk.get("name", "")
                args = tool_chunk.get("args", "")

                tool_call_str = ""
                if tool_name:
                    tool_call_str += f"\n\n <TOOL CALL: {tool_name} > \n\n"
                if args:
                    tool_call_str += str(args)

                yield tool_call_str

            else:
                yield message_chunk.content

            continue


async def main():
    """
    Initialize the MCP Client and run the agent conversation loop.

    The MultiServerMCPClient allows the connection to multiple MCP servers
    using a single client and config.
    """
    client = MultiServerMCPClient(connections=mcp_config)
    tools = await client.get_tools()
    graph = build_agent_graph(tools=tools)

    graph_config = {
        "configurable": {
            "thread_id": "1"
        }
    }

    while True:
        user_input = input("\n\n USER: ")
        if user_input in ["quit", "exit"]:
            break

        print("\n ------ USER ------ \n\n", user_input)
        print("\n ------ ASSISTANT ------ \n\n")

        async for response in stream_graph_response(
            input=AgentState(messages=[HumanMessage(content=user_input)]),
            graph=graph,
            config=graph_config
        ):
            print(response, end="", flush=True)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
