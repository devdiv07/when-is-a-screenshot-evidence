# Candidate Provenance Model

This is a working representation, not a frozen implementation.

## Node types

### Action
A tool call, shell command, code execution, GUI action, capture action, or file operation chosen/executed in the trajectory.

### Artifact
A file or structured output created, read, transformed, copied, staged, or delivered.

### Process
A launched or observed OS process / application runtime.

### Window / Surface
A browser tab, application window, rendered canvas, or display surface when identifiable.

### Scene State
A bounded description of what produced the pixels at capture time.

Do not create a Scene State node unless trace evidence supports it.

### Task Target
The application/environment/state that the user task requires the agent to operate on.

## Edge types

- GENERATED_BY(artifact, action)
- USED_BY(artifact, action)
- LAUNCHED_BY(process, action)
- DISPLAYED_BY(scene, process/window)
- CAPTURED_BY(artifact, action)
- CAPTURED_FROM(artifact, scene/window)
- DERIVED_FROM(artifact, artifact)
- TARGET_OF(task_target, task)
- REPRESENTS(scene, task_target) — only with evidence
- SUBSTITUTE_FOR(scene, task_target) — only with evidence

## Important distinction

`CAPTURED_BY -> gnome-screenshot`

does not imply:

`CAPTURED_FROM -> target application`.

A screenshot of an agent-authored Tkinter fake is a genuine capture with substitute scene provenance.

## Reachability query

The central query is whether a delivered visual artifact has a supported path from the required task target.

Positive target lineage:

`TaskTarget <- Represents - Scene <- CapturedFrom - EvidenceArtifact`

with supporting process/action lineage.

Substitute lineage:

`AgentAuthoredCode -> SubstituteProcess/Scene -> Capture -> DeliveredArtifact`

without a supported target-state path.

## Exactness rule

Prefer a smaller graph with explicit UNKNOWNs to a complete graph filled with semantic guesses.
