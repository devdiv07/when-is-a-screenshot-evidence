# Reproducible headless lab carrying BOTH display stacks in one image, so that the
# X11 vs Wayland comparison differs in the display architecture and nothing else.
#
#   X11 arm      : Xvfb + Openbox                (matches the frozen Phase I lab)
#   Wayland arm  : sway (wlroots) headless + XWayland + xdg-desktop-portal-wlr + PipeWire
#
# THREE trust domains, one more than the Phase I lab:
#   session   (uid 1001) - runs the COMPOSITOR, the portal and PipeWire. Trusted display.
#   attacker  (uid 1000) - unprivileged; constructs cases. Owns no recorder code.
#   root                 - runs the trusted recorder.
#
# No mocked platform metadata anywhere. Every field is read from the live compositor,
# the live portal, /proc, or a real pixel grab. Unobservable is recorded unobservable.
FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
      sway xwayland grim wlr-randr \
      xdg-desktop-portal xdg-desktop-portal-wlr \
      pipewire pipewire-bin wireplumber libspa-0.2-modules \
      dbus dbus-x11 \
      xvfb xauth x11-utils x11-xserver-utils xdotool wmctrl openbox \
      imagemagick \
      eog imv \
      python3 python3-gi python3-gi-cairo gir1.2-gtk-3.0 \
      python3-pil python3-tk python3-pil.imagetk python3-xlib python3-dbus \
      jq procps psmisc coreutils file \
      fonts-dejavu-core ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Same declared-equivalent capture shim as the frozen X11 lab, recorded explicitly.
RUN printf '%s\n' '#!/bin/sh' 'exec /usr/bin/import "$@"' > /usr/local/bin/labshot \
    && chmod +x /usr/local/bin/labshot

RUN useradd -m -u 1000 -s /bin/bash attacker \
    && useradd -m -u 1001 -s /bin/bash session \
    && mkdir -p /lab /lab/out /lab/out/raw /lab/out/shots /lab/out/ground_truth /lab/work \
    && chown -R attacker:attacker /lab/work \
    && chmod 1777 /lab/out /lab/out/raw /lab/out/shots /lab/out/ground_truth

# xdg-desktop-portal-wlr normally asks a GUI chooser which output to cast. Headless has
# no chooser, so the output is pinned in config. This removes an INTERACTION barrier only;
# it does not add, alter or fabricate any metadata the portal returns.
RUN mkdir -p /home/session/.config/xdg-desktop-portal-wlr \
    && printf '%s\n' '[screencast]' 'output_name=HEADLESS-1' 'chooser_type=none' \
       > /home/session/.config/xdg-desktop-portal-wlr/config \
    && chown -R session:session /home/session/.config

WORKDIR /lab
COPY --chown=root:root sway.conf /lab/sway.conf
COPY --chown=root:root platform_recorder.py /lab/platform_recorder.py
COPY --chown=root:root portal_probe.py /lab/portal_probe.py
COPY --chown=root:root run_platform.py /lab/run_platform.py
COPY --chown=attacker:attacker cases.py /lab/cases.py

ENV LAB_SCREEN=1280x1024
ENV DISPLAY=:99

COPY --chown=root:root entrypoint.sh /lab/entrypoint.sh
RUN chmod +x /lab/entrypoint.sh
ENTRYPOINT ["/lab/entrypoint.sh"]
CMD ["/bin/bash"]
