#!/bin/bash
# Boot a real headless X11 desktop, then run whatever was asked.
set -e
: "${DISPLAY:=:99}"
: "${LAB_SCREEN:=1280x1024x24}"
Xvfb "$DISPLAY" -screen 0 "$LAB_SCREEN" -ac +extension RANDR >/tmp/xvfb.log 2>&1 &
for i in $(seq 1 50); do xdpyinfo -display "$DISPLAY" >/dev/null 2>&1 && break; sleep 0.2; done
xdpyinfo -display "$DISPLAY" >/dev/null 2>&1 || { echo "X server failed"; cat /tmp/xvfb.log; exit 1; }
DISPLAY="$DISPLAY" openbox >/tmp/openbox.log 2>&1 &
sleep 1.5
echo "X11 lab up: $(xdpyinfo -display $DISPLAY | grep -m1 'dimensions:')"
exec "$@"
