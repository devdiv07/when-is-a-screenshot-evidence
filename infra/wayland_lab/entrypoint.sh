#!/bin/bash
# Boot BOTH display stacks, then run whatever was asked.
#
# Nothing here fabricates platform state. If a component fails to start, that is
# recorded and the affected arm is reported BLOCKED rather than substituted.
set -u

LOG=/lab/out/boot.log
: > "$LOG"
say() { echo "[boot] $*" | tee -a "$LOG"; }

# ----------------------------------------------------------------- X11 arm
: "${DISPLAY:=:99}"
Xvfb "$DISPLAY" -screen 0 "${LAB_SCREEN}x24" -ac +extension RANDR >>"$LOG" 2>&1 &
for _ in $(seq 1 50); do xdpyinfo -display "$DISPLAY" >/dev/null 2>&1 && break; sleep 0.2; done
if xdpyinfo -display "$DISPLAY" >/dev/null 2>&1; then
  DISPLAY="$DISPLAY" openbox >>"$LOG" 2>&1 &
  sleep 1.0
  say "X11 up: $(xdpyinfo -display "$DISPLAY" | grep -m1 'dimensions:')"
  echo "x11=up" >> /lab/out/stack_status
else
  say "X11 FAILED"
  echo "x11=failed" >> /lab/out/stack_status
fi

# ----------------------------------------------------------------- Wayland arm
# The compositor is its own trust domain (uid 1001), separate from the attacker (1000)
# and from the recorder (root).
export XDG_RUNTIME_DIR=/run/user/1001
mkdir -p "$XDG_RUNTIME_DIR"
chown session:session "$XDG_RUNTIME_DIR"
chmod 0755 "$XDG_RUNTIME_DIR"          # traversable so the attacker can reach the socket

runas_session() { setpriv --reuid=1001 --regid=1001 --init-groups env \
    HOME=/home/session USER=session LOGNAME=session \
    XDG_RUNTIME_DIR=/run/user/1001 \
    WLR_BACKENDS=headless WLR_RENDERER=pixman WLR_LIBINPUT_NO_DEVICES=1 \
    XDG_CURRENT_DESKTOP=sway XDG_SESSION_TYPE=wayland \
    WAYLAND_DISPLAY=wayland-1 \
    DBUS_SESSION_BUS_ADDRESS="unix:path=$XDG_RUNTIME_DIR/bus" \
    "$@"; }

# session bus first: the portal is a D-Bus service and cannot exist without one
runas_session dbus-daemon --session --address="unix:path=$XDG_RUNTIME_DIR/bus" --fork \
  >>"$LOG" 2>&1
sleep 0.5
if [ -S "$XDG_RUNTIME_DIR/bus" ]; then
  chmod 0777 "$XDG_RUNTIME_DIR/bus"
  say "session bus up"
  echo "dbus=up" >> /lab/out/stack_status
else
  say "session bus FAILED"; echo "dbus=failed" >> /lab/out/stack_status
fi

runas_session sway -c /lab/sway.conf >>"$LOG" 2>&1 &
SWAY_WAIT=0
for _ in $(seq 1 60); do
  SOCK=$(ls "$XDG_RUNTIME_DIR"/sway-ipc.*.sock 2>/dev/null | head -1)
  if [ -n "${SOCK:-}" ] && [ -S "$XDG_RUNTIME_DIR/wayland-1" ]; then SWAY_WAIT=1; break; fi
  sleep 0.3
done
if [ "$SWAY_WAIT" = "1" ]; then
  # the attacker is a *client* of the trusted compositor, so it needs the sockets
  chmod 0777 "$XDG_RUNTIME_DIR"/wayland-1 "$XDG_RUNTIME_DIR"/wayland-1.lock 2>/dev/null
  chmod 0777 "$XDG_RUNTIME_DIR"/sway-ipc.*.sock 2>/dev/null
  export SWAYSOCK=$(ls "$XDG_RUNTIME_DIR"/sway-ipc.*.sock | head -1)
  echo "SWAYSOCK=$SWAYSOCK" > /lab/out/wayland_env
  echo "XDG_RUNTIME_DIR=$XDG_RUNTIME_DIR" >> /lab/out/wayland_env
  echo "WAYLAND_DISPLAY=wayland-1" >> /lab/out/wayland_env
  echo "DBUS_SESSION_BUS_ADDRESS=unix:path=$XDG_RUNTIME_DIR/bus" >> /lab/out/wayland_env
  say "sway up: $(runas_session swaymsg -t get_version 2>/dev/null | head -c 200)"
  echo "wayland=up" >> /lab/out/stack_status
else
  say "sway FAILED to start (see $LOG)"
  echo "wayland=failed" >> /lab/out/stack_status
fi

# PipeWire + portal. These are what make the STANDARD capture path exist; if they do not
# come up, the portal arm is BLOCKED and says so.
runas_session pipewire >>"$LOG" 2>&1 &
runas_session wireplumber >>"$LOG" 2>&1 &
sleep 1.0
runas_session /usr/libexec/xdg-desktop-portal-wlr >>"$LOG" 2>&1 &
runas_session /usr/libexec/xdg-desktop-portal >>"$LOG" 2>&1 &
sleep 2.0
if runas_session dbus-send --session --print-reply --dest=org.freedesktop.DBus \
      /org/freedesktop/DBus org.freedesktop.DBus.ListNames 2>/dev/null \
      | grep -q "org.freedesktop.portal.Desktop"; then
  say "xdg-desktop-portal present on the session bus"
  echo "portal=up" >> /lab/out/stack_status
else
  say "xdg-desktop-portal NOT on the session bus"
  echo "portal=down" >> /lab/out/stack_status
fi

chmod -R a+rwX /lab/out 2>/dev/null
say "stack status: $(tr '\n' ' ' < /lab/out/stack_status)"
exec "$@"
