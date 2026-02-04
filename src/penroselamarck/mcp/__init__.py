"""
Penrose-Lamarck MCP (HTTP bridge) package.

Public API
----------
- :mod:`penroselamarck.mcp.server`: FastAPI application with tool endpoints.
- :mod:`penroselamarck.mcp.schemas`: Pydantic models for API payloads.
- :mod:`penroselamarck.mcp.transport`: MCP HTTP/SSE transport utilities.

Attributes
----------
__version__ : str
    Package version.

Examples
--------
>>> __version__.count(\".\") == 2
True

See Also
--------
:mod:`penroselamarck.mcp.tool_registry`
"""

__version__ = "0.2.0"
