"""
Penrose-Lamarck MCP (HTTP bridge) package.

Public API
----------
- :mod:`penroselamarck.api.server`: FastAPI application with tool endpoints.
- :mod:`penroselamarck.api.schemas`: Pydantic models for API payloads.
- :mod:`penroselamarck.api.transport`: MCP HTTP/SSE transport utilities.

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
:mod:`penroselamarck.api.tool_registry`
"""

__version__ = "0.2.0"
