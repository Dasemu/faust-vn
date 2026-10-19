# faust-vn

A playable visual-novel prototype of the opening of Goethe's *Faust* (Part I), in
Teodoro Llorente's public-domain Spanish translation. It is the first work built with
[`vnpipe`](../vnpipe), the reusable "classic novels to visual novels" pipeline.

The game is in Spanish. Art is AI-generated (see [docs/licensing.md](docs/licensing.md)).

## Quick start

`vnpipe` is a path dependency: clone it next to this repo and adjust
`[tool.uv.sources]` in `pyproject.toml` if it lives elsewhere.

```bash
uv sync
uv run vnpipe fetch          # download the source into data/raw
uv run vnpipe parse          # data/raw -> data/parsed.json
uv run vnpipe renpy          # data/annotated.json -> vn/
tools/renpy-sdk/renpy.sh vn  # play (Ren'Py 8.5.3 SDK, see docs/running.md)
```

Run, lint and build instructions: [docs/running.md](docs/running.md).
Plan and layout: [docs/plan.md](docs/plan.md).
