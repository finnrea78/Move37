"""
MCP router package.

Provides versioned REST and MCP transport router assemblies.

Public API
----------
- :mod:`penroselamarck.api.routers.rest`: REST router assembly.
- :mod:`penroselamarck.api.routers.mcp`: MCP transport router.
- :mod:`penroselamarck.api.routers.oauth`: OAuth protected resource metadata router.
- :mod:`penroselamarck.api.routers.v1`: v1 router assembly.

Attributes
----------
None

Examples
--------
>>> from penroselamarck.api.routers.v1 import build_v1_router
>>> build_v1_router().prefix
'/v1'

See Also
--------
:mod:`penroselamarck.api.server`
"""
