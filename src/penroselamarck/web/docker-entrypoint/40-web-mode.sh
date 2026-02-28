#!/bin/sh
set -eu

# Nginx entrypoint hook:
# - This script is copied into /docker-entrypoint.d/ in the web image.
# - The official nginx entrypoint executes scripts in lexical order.
# - Prefix "40-" gives deterministic ordering among entrypoint hooks.
#
# Purpose:
# - Select runtime nginx mode from WEB_STANDALONE_DEBUG.
# - true  => standalone config (no /v1 proxy dependency on api service).
# - false => proxy config (normal /v1 -> penroselamarck-api flow).

MODE="${WEB_STANDALONE_DEBUG:-false}"
TARGET="/etc/nginx/conf.d/default.conf"

case "$MODE" in
true | TRUE | 1 | yes | YES)
    cp /etc/nginx/penroselamarck/nginx.standalone.conf "$TARGET"
    echo "[penroselamarck-web] WEB_STANDALONE_DEBUG=true -> standalone nginx config enabled"
    ;;
*)
    cp /etc/nginx/penroselamarck/nginx.proxy.conf "$TARGET"
    echo "[penroselamarck-web] WEB_STANDALONE_DEBUG=false -> proxy nginx config enabled"
    ;;
esac
