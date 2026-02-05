"""
MCP router package.

Provides versioned REST and MCP transport router assemblies.

Public API
----------
- :mod:`penroselamarck.mcp.routers.rest`: REST router assembly.
- :mod:`penroselamarck.mcp.routers.mcp`: MCP transport router.
- :mod:`penroselamarck.mcp.routers.oauth`: OAuth protected resource metadata router.
- :mod:`penroselamarck.mcp.routers.v1`: v1 router assembly.

Attributes
----------
None

Examples
--------
>>> from penroselamarck.mcp.routers.v1 import build_v1_router
>>> build_v1_router().prefix
'/v1'

See Also
--------
:mod:`penroselamarck.mcp.server`
"""
