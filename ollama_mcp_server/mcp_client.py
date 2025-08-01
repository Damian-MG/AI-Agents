import asyncio
import nest_asyncio
from llama_index.llms.ollama import Ollama
from llama_index.core import Settings
from llama_index.core.workflow import Context
from llama_index.core.agent.workflow import FunctionAgent, ToolCallResult, ToolCall
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec

nest_asyncio.apply()

llm_ = Ollama(model="mario:latest", request_timeout=120.0)
Settings.llm = llm_

mcp_client = BasicMCPClient("http://127.0.0.1:8000/sse")
mcp_tools = McpToolSpec(client=mcp_client)

# Comprobar que el servidor MCP está cogiendo las tools que tocan
# async def main():
#     tools = await mcp_tools.to_tool_list_async()
#     for tool in tools:
#         print(tool.metadata.name, tool.metadata.description)

# asyncio.run(main())

SYSTEM_PROMPT = """
You are Mario from Super Mario Bros an AI assistant for Tool Calling.. Answer as Mario, the assistant, only.
Before you help a user, you need to work with tools to interact with Our Database or with the Weather API
"""

async def get_agent(tools: McpToolSpec):
    tools = await tools.to_tool_list_async()
    agent = FunctionAgent(
        name="Mario",
        description="An agent that can work with Our Database software and interact with the weather API",
        tools=tools,
        llm=llm_,
        system_prompt=SYSTEM_PROMPT,
    )
    return agent

async def handle_user_message(
    message_content: str,
    agent: FunctionAgent,
    agent_context: Context,
    verbose: bool = False,
):
    handler = agent.run(message_content, ctx=agent_context)
    async for event in handler.stream_events():
        if verbose and type(event) == ToolCall:
            print(f"Calling tool {event.tool_name} with kwargs {event.tool_kwargs}")
        elif verbose and type(event) == ToolCallResult:
            print(f"Tool {event.tool_name} returned {event.tool_output}")

    response = await handler
    return str(response)

async def main():
    # get the agent
    agent = await get_agent(mcp_tools)
    # create the agent context
    agent_context = Context(agent)
    
    # Run the agent!
    while True:
        user_input = input("Enter your message: ")
        if user_input == "exit":
            break
        print("User: ", user_input)
        response = await handle_user_message(user_input, agent, agent_context, verbose=True)
        print("Agent: ", response)

# Run the async main function
asyncio.run(main())






