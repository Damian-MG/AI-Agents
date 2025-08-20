from mcp.server.fastmcp import FastMCP

# MCP server instance
mcp = FastMCP("Math")


# Registers this function as a an available tool on the MCP server
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b


# Start the MCP server
if __name__ == "__main__":
    mcp.run(transport='stdio')
