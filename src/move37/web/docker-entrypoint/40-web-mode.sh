#!/bin/sh
set -eu

MODE="${WEB_STANDALONE_DEBUG:-false}"
TARGET="/etc/nginx/conf.d/default.conf"

case "$MODE" in
true | TRUE | 1 | yes | YES)
    cp /etc/nginx/move37/nginx.standalone.conf "$TARGET"
    echo "[move37-web] WEB_STANDALONE_DEBUG=true -> standalone nginx config enabled"
    ;;
*)
    cp /etc/nginx/move37/nginx.proxy.conf "$TARGET"
    echo "[move37-web] WEB_STANDALONE_DEBUG=false -> proxy nginx config enabled"
    ;;
esac
