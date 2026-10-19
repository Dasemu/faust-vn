# Adaptation rules (Faust)

The generic rules (text is never rewritten, NVL for lyric passages, text rhythm, sprites and
expressions, transitions, music, the `work.toml` override layer) live in vnpipe:
`../vnpipe/docs/adaptation-rules.md`. This file records how they apply to Faust; the
decisions themselves are in `work.toml` (`[staging.*]`, `[[cues]]`, `[[overrides]]`).

## Application to Faust

- Sprites appear in dialogue scenes only: the theatre, Mephistopheles before the Lord,
  Faust in his study.
- The ineffable is never drawn. The Lord is a radiance (`bg_heaven_lord`); the Earth Spirit
  is a lighting change plus a flash and a shake (`bg_study_spirit`). Their lines still
  carry a name and colour.
- The Dedicatoria (the poet's own voice) and the archangels' hymn are NVL poems over a
  background.
- The three archangels are painted into `bg_heaven`, not drawn as three sprites.
- One background per location, plus variants only where the text changes the light
  (macrocosm sign, Earth Spirit, heaven closing).
- The prototype ships without audio; music moods are annotated but only played if
  `vn/game/audio/<mood>.ogg` exists.

## Staging (work.toml)

| Scene | Base | Notes |
|---|---|---|
| Dedicatoria | `bg_dedication`, NVL | The poet's voice; no speaker name. |
| Prólogo en el teatro | `bg_theatre`, ADV | Director, Poet and Clown as sprites. |
| Prólogo en el cielo | `bg_heaven`, NVL | Hymn as full-screen text; switches to ADV + `bg_heaven_lord` when Mephistopheles speaks; heaven closes → dark tint. |
| De noche | `bg_study`, ADV | Macrocosm sign → `bg_study_macrocosm`; Earth Spirit's sign → red tint; apparition → `bg_study_spirit` + flash + shake. |
