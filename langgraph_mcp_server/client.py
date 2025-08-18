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
from langgraph_mcp_server.graph import build_agent_graph, AgentState

