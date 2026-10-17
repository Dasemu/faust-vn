# Prototype report

Build of the first playable prototype (2026-10-17, one session, ~2 h wall time).
Scope: Dedicatoria, Prólogo en el teatro, Prólogo en el cielo and "De noche" up to the
Earth Spirit's rejection of Faust — 630 verse lines, 7 stage directions, 4 scenes
(`docs/scope.md`).

## What was automated

| Stage | How | Output |
|---|---|---|
| Fetch + scope cut | `vnpipe fetch` / `vnpipe parse`, markers in `work.toml` | `play.txt` (798 lines) |
| Parsing | Deterministic parser: scenes, speakers + notes, verse, stanzas, split verses, directions, cast lists; fails loudly on anything unknown | `parsed.json` (639 lines) |
| Annotation | `vnpipe annotate chunk` → 16 chunks; 8 Haiku sub-agents (2 chunks each) in parallel; `status`/`merge` validate schema, input hash, line coverage, deterministic fields, cast ids | `annotated.json`, 0 fallback chunks, 0 invalid on first pass |
| Art | One Sonnet sub-agent drove the ChatGPT image MCP (≤ 20 generations/hour), imported with sha256 verification, chroma-keyed sprites, reviewed every image | 7 backgrounds + 17 sprites, all approved |
| Ren'Py | `vnpipe renpy`: GUI from the SDK's `generate_gui` template, characters, images, script with title cards, NVL/ADV, cues, tints, flash/shake, expression mapping | `vn/faust/`, `renpy lint` clean |
| Builds | Ren'Py launcher `web_build` and `distribute --package linux` | `build/web/`, `build/dist/*.tar.bz2` |

Everything except the LLM and image calls is deterministic and idempotent (re-running
any stage gives byte-identical files); those two are cached by input hash / recorded in
the manifest, so the pipeline resumes instead of redoing work.

## What needed human judgment

- **Scope cut** (where ~15 printed pages ends): chose the Earth Spirit's rejection over
  ending at the heaven prologue, for a dramatic close and to include Faust himself.
- **Adaptation rules** (`docs/adaptation-rules.md`): what is drawn vs. narrated — no
  sprite for the Lord or the Earth Spirit, archangels painted into the background,
  lyric passages as full-screen text.
- **Staging cues** in `work.toml`: background changes on the macrocosm sign, the Spirit's
  sign, the apparition, heaven closing.
- **Correcting the annotator** through a generic override layer: the Haiku pass dropped
  the Clown from stage mid-scene, moved characters between positions and labelled all
  92 of Mephistopheles' lines "ironic". Fixed by pinned scene cast, sprite moves and
  emotion ranges in `work.toml` instead of hand-editing JSON.
- **Art direction**: the art bible and base prompt; the first calibration image came
  out as glossy concept art and the base prompt had to forbid it explicitly.
- **Visual review**: the art agent judged each image, then the orchestrator reviewed the
  full contact sheet.
- **Runtime QA**: playing the web build found a main-menu crash (missing GUI images)
  that `renpy lint` does not detect.

## Cost and time per stage

Costs: no paid API was used. Images came from the ChatGPT image MCP (the account's
quota, no per-image charge); ZenvairoMediaGenerator (paid) was **not** used. Tokens are
sub-agent totals reported by the harness.

| Stage | Model | Wall time | Tokens | Notes |
|---|---|---|---|---|
| Planning, schemas, config, art bible, adaptation rules, review | Opus (main) | ~35 min spread | — | design + integration |
| Text stage (parser, tests, scope/licensing docs) | Sonnet | 2.5 min | 102k | 23 tests |
| Ren'Py SDK install (8.5.3 + web) | Haiku | 1.2 min | 54k | checksum verified |
| Annotation tooling | Sonnet | 3.5 min | 116k | 50 tests |
| Annotation pass (16 chunks) | 8 × Haiku | 1.5–3.3 min each, ~3.5 min total | ~630k total | 0 rejected chunks |
| Ren'Py generator + 2 follow-ups | Sonnet | ~48 min over 3 rounds | 268k | lint clean, e2e playthrough test, web + linux builds |
| Art (31 generations incl. calibration) | Sonnet + ChatGPT MCP | 1 h 39 min | 252k | ~4 min/image; 6 regenerations |

The art stage dominates wall time: the MCP queue is sequential (1–7 min per image) and
capped at 20 generations/hour. Everything else ran in parallel with it.

## Known weaknesses

- **Emotion granularity**: the small model tends to label whole speeches with one
  emotion (Mephistopheles all "ironic", Faust mostly "melancholic"/"ecstatic"), so
  expressions change rarely. Overrides fix the worst cases by hand.
- **Annotation staging is per chunk**: chunks are annotated independently, so presence
  and positions can drift between chunks; the generator stabilises positions, and the
  pinned cast covers the rest, but it needs human review.
- **Sprite framing is inconsistent**: Mephistopheles is drawn to mid-shin, Faust to the
  knees; the image model drifts to full-body unless told "cropped below the knees". The
  clown carries an unrequested puppet.
- **Reference-image variants sometimes come back identical** to the base (seen 3 times);
  the art agent caught it by comparing sha256, but a pipeline check should enforce it.
- **No audio**: music moods are annotated and the generator supports them, but no files
  ship.
- **Text boxes of verse**: 4 lines per box keeps verse intact but long monologues (Faust,
  80 lines) feel slow; no auto-pagination by reading time.
- **Chroma key is per-pixel**: fine with the flat green field, but any green in a
  costume or a soft gradient field would break it (rembg would be the fallback).
- **Remote push** depends on the SSH host being reachable from this machine; it was not
  during the session (see final status).

## Next steps to generalise (Werther, etc.)

1. **Prose works** (Werther is epistolary prose, not verse drama): add a prose parser
   mode (paragraphs, letters with dates/headings as scenes, narrator as the letter
   writer) behind the same `parsed.schema.json`; `kind` already allows narration.
2. **Per-work config only**: everything Faust-specific already lives in `work.toml`;
   add a `vnpipe init <gutenberg id>` that scaffolds it (detect headings and speaker
   names automatically, propose cast and scenes for human approval).
3. **Annotation quality**: give each chunk the previous chunk's final on-stage state,
   ask for emotion per sentence rather than per line, and add a cheap second pass
   ("reviewer" agent) that flags monotone speeches.
4. **Art automation**: generate prompts for cast and locations from the annotated
   data + art bible template; add automatic checks (variant ≠ base hash, alpha coverage,
   framing via bbox aspect ratio) before human review.
5. **Runtime QA in CI**: keep the end-to-end playthrough test (main menu → end) next to
   `renpy lint`.
6. **Audio**: public-domain recordings (e.g. Musopen) mapped to the six moods.
