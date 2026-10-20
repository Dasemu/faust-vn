# Project report

## Canonical edition

All of *Faust, Part I* (Llorente's translation, Dedicatoria to Cárcel): 28 scenes, about
2,250 dialogue blocks, built on 2026-10-19 (first commit 03:52, last 18:34, ~15 h wall time
with the art queue running in the background). The pipeline was split out of this repo into
`vnpipe`, a git dependency pinned by `uv.lock`; this repo only holds the work (`work.toml`,
data, annotations, assets, generated `vn/`).

### What was automated

| Stage | How | Output |
|---|---|---|
| Fetch + parse | `vnpipe fetch` / `parse`, markers and speaker map in `work.toml`; fails loudly on unknown input | `parsed.json`, 28 scenes |
| Annotation (v2) | `vnpipe annotate`: one Haiku call per chunk via headless `claude -p`; compact records (speech-level emotion, music, entrances/exits); cached by input hash; schema, hash and coverage validated on merge | `annotated.json`, 36 chunks |
| Art | `vnpipe assets`: prompts from the art bible, import with sha256 check, chroma key, approval manifest, per-asset renditions per style with fallback | 67 assets per style, all approved |
| Music | 14 public-domain/CC recordings by mood plus fixed scene tracks, credits manifest (`docs/music.md`) | `audio/`, credits screen |
| Ren'Py | `vnpipe renpy`: GUI, characters, script, title cards, NVL/ADV, cues, style switch | `vn/`, `renpy lint` clean |
| QA | Spanish UI, *Escenas* (chapter select), credits, headless screenshot pass (`docs/running.md` 3c), end-to-end playthrough test (~5 min) | passing |

Two art styles ship: *painterly* (default) and *anime*, selectable on first launch and in
Preferences. Every stage is deterministic and idempotent; LLM and image outputs are cached.

### What needed human judgment

- Art direction: art bible, a separate anime base prompt, calibration of the first anime
  sprites (three calibration rounds), and review of every image (some anime variants were rejected).
- Adaptation rules and staging: what is drawn or narrated, scene backgrounds and cues,
  per-scene music choices, music licence vetting.
- Correcting the annotator through `work.toml` overrides (pinned cast, emotion ranges)
  rather than editing JSON.
- Visual and runtime QA: found GUI, label and Spanish-text defects that lint does not catch.
- Image-MCP workaround: `reference_images` made the MCP echo the reference unchanged, so
  variants are generated without references, repeating the full character description and
  changing only the expression/pose sentence.

### Costs and throughput

| Item | Figure |
|---|---|
| Annotation LLM | $0.76 total, 86 Haiku calls (36 chunks; 26 retries/re-runs, 2 pilot chunks included), ~8 min of model time |
| Images | 123 generation calls in the log (including 4 marked retries and calibration), 134 approved assets over both styles; ChatGPT image MCP at 20 generations per rolling hour; no per-image charge |
| Wall time | one day, 2026-10-19; the image queue (~1-7 min per call, sequential, rate-limited) dominates and ran in parallel with the rest |

The image log starts at the first anime calibration (03:57); earlier painterly generations
are not counted in it, so the total is a lower bound.

### In progress

- German voice track from the LibriVox dramatic reading (public domain), aligned to the
  text with Whisper.

### Known limitations and next steps

- Web and Linux builds of the canonical edition are produced locally (`docs/running.md`) but
  not yet published.
- Annotation still labels long speeches with few emotions; overrides cover the worst cases.
- Sprite framing varies slightly between characters (the model drifts to full-body).

## Prototype

First playable prototype, 2026-10-17, one session (~2 h): Dedicatoria, both prologues and
"De noche" up to the Earth Spirit (630 verse lines, 4 scenes). Parser, annotation (8 parallel
Haiku sub-agents over 16 chunks, 0 rejected), 7 backgrounds + 17 sprites (31 generations,
~1 h 40 min) and the Ren'Py generator were all built then, with no paid API. It exposed the
problems the canonical edition addressed: single-emotion speeches, per-chunk staging drift,
identical reference-image variants, per-line music changes, and a menu crash that only the
playthrough test caught. The code now lives in `vnpipe`.
