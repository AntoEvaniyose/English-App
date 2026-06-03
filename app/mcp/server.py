from fastmcp import FastMCP

mcp = FastMCP(
    name="English Learning MCP",
    version="1.0.0"
)

# register tools
import app.mcp.user_tools
import app.mcp.content_tools