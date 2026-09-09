# Tests

Tests should pin observed schema behavior and adversarial provenance cases.

Before expanding the parser, create fixtures for at least:

1. direct PIL image synthesis;
2. real target-app capture;
3. capture of agent-created fake renderer/window;
4. transformed/cropped prior screenshot;
5. shell-routed `gnome-screenshot`;
6. native GUI screenshot;
7. output-path rename/copy before staging;
8. missing quote / malformed trace;
9. ambiguous capture source;
10. negative control with no fabrication.

Never edit tests merely to accommodate an implementation shortcut.
