# Plan

Goal: a playable Ren'Py prototype of the opening of Goethe's *Faust I* (Llorente's
Spanish translation) **and** a reusable pipeline that turns any public-domain play
from Project Gutenberg into a visual novel. Faust is the first "work"; Werther and
others should only need a new `works/<name>/work.toml` plus art.

## Pipeline

```
Gutenberg .txt ──fetch──▶ raw (cached, gitignored)
              ──clean──▶ play.txt        (header/footer/intro stripped, scope cut)
              ──parse──▶ parsed.json     (scenes, speakers, verse lines, directions)
              ──chunk──▶ annotations/chunks/*.json   (LLM work units)
   LLM sub-agents ─────▶ annotations/cache/*.json    (one file per chunk, keyed by hash)
              ──merge──▶ annotated.json  (schema-validated, complete)
art (MCP) ──▶ assets/assets.json + images (manifest, sha256, status)
              ──renpy──▶ game/           (generated Ren'Py project)
```

Every stage is a `vnpipe` CLI subcommand, deterministic given its inputs, and
idempotent (re-running produces byte-identical output). The only non-deterministic
steps — LLM annotation and image generation — write to caches keyed by content
hash, so they are resumable and never redone unless their input changes.

## Layout

| Path | Purpose |
|---|---|
| `src/vnpipe/` | Generic pipeline code (no Faust-specific logic) |
| `src/vnpipe/schemas/` | JSON Schemas: parsed text, annotation, asset manifest |
| `works/faust/work.toml` | Everything work-specific: source URL, scope markers, cast, colors, locations, expression maps |
| `works/faust/data/` | `play.txt`, `parsed.json`, `annotated.json` |
| `works/faust/annotations/` | Chunk inputs and cached LLM outputs |
| `works/faust/assets/` | `assets.json` manifest, generated/processed images |
| `game/` | Generated Ren'Py project (committed so the repo is playable) |
| `docs/` | Design and process docs |

## Steps

1. **Text** — fetch, clean, cut scope (`docs/scope.md`), deterministic parser + tests,
   `docs/licensing.md`.
2. **Annotation** — JSON Schema, chunker, merge/validate, cache. Haiku sub-agents
   annotate chunks in parallel. Adaptation rules in `docs/adaptation-rules.md`.
3. **Art** — `docs/art-bible.md` with a fixed base prompt. Backgrounds and sprites via
   the ChatGPT image MCP (max 20 generations/hour), background removal, manifest,
   placeholders for anything missing.
4. **Ren'Py** — generator from `annotated.json` + manifest; `renpy lint` clean;
   web/desktop build if feasible.
5. **Report** — `docs/report.md`: automation vs human judgment, cost/time, weaknesses,
   next steps.

## Parallelisation

- Text stage and art bible / first background generations run in parallel.
- Annotation chunks are independent → parallel Haiku agents.
- Ren'Py generator is written against the schemas while annotation and art run.
- Image generation is sequential (MCP queue) and runs in the background throughout.

## Model allocation

| Work | Model |
|---|---|
| Design, schemas, adaptation rules, art direction, review | Opus (main) |
| Parser, generator, tooling, tests | Sonnet sub-agents |
| Line annotation, formatting, mechanical edits | Haiku sub-agents |
