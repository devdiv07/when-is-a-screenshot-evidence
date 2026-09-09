# Reproducible headless X11 lab for the Phase I empirical arm.
#
# Real Xvfb display, real window manager, real windows, real screenshot bytes.
# No mocked window metadata anywhere: the recorder derives every field from the
# live X server, /proc and the filesystem.
#
# Two identities exist inside the container:
#   attacker  (uid 1000, unprivileged) - constructs scenarios, owns no recorder code
#   root                                - runs the trusted recorder
FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
      xvfb xauth x11-utils x11-xserver-utils xdotool wmctrl openbox \
      xserver-xephyr \
      imagemagick scrot \
      python3 python3-tk python3-pil python3-pil.imagetk python3-xlib \
      procps psmisc coreutils file \
      fonts-dejavu-core \
      ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# gnome-screenshot pulls a large GNOME dependency chain and needs a session bus;
# the declared equivalent capture implementation for this lab is ImageMagick
# `import`, which performs a genuine X11 pixel grab. Recorded in the manifest as
# capture_tool so the substitution is explicit rather than silent.
RUN printf '%s\n' '#!/bin/sh' \
    'exec /usr/bin/import "$@"' > /usr/local/bin/labshot && chmod +x /usr/local/bin/labshot

RUN useradd -m -u 1000 -s /bin/bash attacker \
    && mkdir -p /lab /lab/out /lab/out/ground_truth /lab/out/raw /lab/out/shots /lab/work \
    && chown -R attacker:attacker /lab/work /lab/out/ground_truth \
    && chmod 1777 /lab/out

WORKDIR /lab
COPY --chown=root:root recorder.py /lab/recorder.py
COPY --chown=attacker:attacker scenarios.py /lab/scenarios.py
COPY --chown=root:root run_empirical.py /lab/run_empirical.py
COPY --chown=root:root race_s1.py /lab/race_s1.py
COPY --chown=root:root nested_s2.py /lab/nested_s2.py
COPY --chown=root:root adjudicate_empirical.py /lab/adjudicate_empirical.py
COPY --chown=root:root test_isolation.py /lab/test_isolation.py
COPY --chown=root:root adjudicator.py /lab/adjudicator.py
COPY --chown=root:root adversarial_cases.py /lab/adversarial_cases.py
COPY --chown=root:root task_declarations.json /lab/out_task_declarations.json

ENV DISPLAY=:99
ENV LAB_SCREEN=1280x1024x24
CMD ["/bin/bash"]

COPY --chown=root:root entrypoint.sh /lab/entrypoint.sh
RUN chmod +x /lab/entrypoint.sh
ENTRYPOINT ["/lab/entrypoint.sh"]
