# CLAUDE.md

Pipeline (`vnpipe`) that turns a public-domain play into a Ren'Py visual novel; first work: Faust I (Spanish, Llorente).

## Rules
- Repo content in English; the game text is Spanish (from the source, never rewritten).
- `src/vnpipe` is work-agnostic. Anything specific to a text goes in `works/<id>/work.toml`.
- Every stage must be deterministic and idempotent; LLM/image outputs are cached by input hash.
- Data contracts live in `src/vnpipe/schemas/*.schema.json`; change schema + tests together.
- ChatGPT image MCP: max 20 generations per hour.

## Commands
- `export UV_CACHE_DIR=$TMPDIR/uv-cache` first when running inside the sandbox.
- `uv sync` — install. `uv run pytest` — tests. `uv run ruff check . && uv run ruff format --check .` — lint.
- `uv run vnpipe --help` — pipeline CLI. Stages: `fetch`, `parse`, `annotate {chunk,status,prompt,merge}`,
  `assets {prompt,import,process,status,placeholders,sheet}`, `renpy [--with-test]`.
- Ren'Py SDK lives in `tools/renpy-sdk` (gitignored; may be a symlink shared between worktrees).
  Inside the sandbox prefix SDK commands with `HOME=$TMPDIR/renpy-home`.
  Lint: `tools/renpy-sdk/renpy.sh vn/faust lint`. Playthrough test and builds: `docs/running.md`.

## Branches and versions
- `development` is the integration branch; `main` receives reviewed merges from it.
  Feature work branches off `development` (`feat/...`, `fix/...`).
- `VERSION` is bumped by `.github/workflows/version.yml` on push (patch on `development`,
  minor on a `development` → `main` merge). Do not edit it by hand.
- CI (`.github/workflows/ci.yml`) runs ruff and pytest.

## Layout
See `docs/plan.md`.
