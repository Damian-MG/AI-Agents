import os

from typing import List, Annotated
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage
from langchain.tools import tool, BaseTool
from langgraph.graph import StateGraph, add_messages, START
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver


class AgentState(BaseModel):
    messages: Annotated[List, add_messages]


@tool
def multiply(a: int, b: int) -> int:
    """Multiply a and b.

    Args:
        a: first int
        b: second int
    """
    return a * b


def build_agent_graph(tools: List[BaseTool] = None):

    if tools is None:
        tools = []

    system_prompt = """
Your name is Pepe and you are an expert data scientist. You help customers
manage their data science projects by leveraging the tools available to you.

<filesystem>
You have access to a set of tools that allow you to interact with the user's
local filesystem.
You are only able to access files within the working directory `projects`.
The absolute path to this directory is: {working_dir}
If you try to access a file outside of this directory, you will receive an
error. Always use absolute paths when specifying files.
</filesystem>

<projects>
A project is a directory within the `projects` directory.
When using the create_new_directory tool to create a new project, the following
commands will be run for you:
    a. `mkdir <directory_name>` - creates a new directory for the project
    b. `chdir <directory_name>` - changes to the new directory
    c. `echo "Hello World! > README.md"` - creates a new file within the
        project
Every project has the exact same structure.

<data>
When the user refers to data for a project, they are referring to the data
within the `data` directory of the project. All projects must use the `data`
directory to store all data related to the project. The user can also load data
into this directory. You have a set of tools called dataflow that allow you to
interact with the customer's data. The dataflow tools are used to load data
into the session to query and work with it. You must always first load data
into the session before you can do anything with it.
</data>

<code>
The main.py file is the entry point for the project and will contain all the
code to load, transform, and model the data. You will primarily work on this
file to complete the user's requests. main.py should only be used to implement
permanent changes to the data.
</code>

<tools>
{tools}
</tools>

Assist the customer in all aspects of their data science workflow.
"""

    llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            temperature=0.9,
            max_tokens=4096,
            timeout=None,
            max_retries=2
        )

    if tools:
        llm = llm.bind_tools(tools)
        # Inject tools into promtp
        tools_json = [tool.model_dump_json(include=["name", "description"])
                      for tool in tools]
        system_prompt = system_prompt.format(
            tools="\n".join(tools_json),
            working_dir=os.environ.get('MCP_FILESYSTEM_DIR')
        )

    def assistant(state: AgentState) -> AgentState:
        response = llm.invoke([SystemMessage(content=system_prompt) +
                               state.messages])
        state.messages.append(response)
        return state

    builder = StateGraph(AgentState)

    builder.add_node("Pepe", assistant)
    builder.add_node(ToolNode(tools))

    builder.add_edge(START, "Pepe")
    builder.add_conditional_edges(
        "Pepe",
        tools_condition
    )
    builder.add_edge("tools", "Pepe")

    return builder.compile(checkpointer=MemorySaver())


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    graph = build_agent_graph(tools=[multiply])
    with open("graph_visualization.png", "wb") as f:
        f.write(graph.get_graph().draw_mermaid_png())
