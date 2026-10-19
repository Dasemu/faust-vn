# Voice track (German original under the Spanish text)

The German original of *Faust I* is read by LibriVox's public-domain dramatic reading
("Faust: Der Tragödie erster Teil", one reader per role, 28 sections = our 28 scenes in order).
`vnpipe voice` (see `../vnpipe/docs/voice.md`) cuts one clip per German speech and the game plays
it under the matching Spanish speech. Speeches it cannot map with confidence stay silent.

## Data

- `work.toml` `[voice]`: source URLs, `scenes` (the pilot subset; delete the key to run all 28),
  `[voice.asr]` (GPU host), `[voice.speakers]` (German label -> cast id), `[[voice.sections]]`
  (scene id, audio section number, German heading), `credits` (the "Voces" credits section).
- `voice/asr/NN.json`: faster-whisper word timestamps per section. Committed, so everything
  after ASR is local and deterministic.
- `voice/map.json`, `voice/report/<scene>.txt`: speech mapping and per-scene coverage report.
- `voice/clips/<first Spanish line id>.ogg`: mono Opus 40 kbps, loudness-normalised
  (about 5 KB/s). Copied by `vnpipe renpy` to `vn/game/voice/` (gitignored there).
- `data/raw/librivox/NN.mp3` and `data/raw/pg2229.txt` (German text, Gutenberg #2229): gitignored.

## Run it

```sh
export UV_CACHE_DIR=$TMPDIR/uv-cache
uv run vnpipe voice fetch          # mp3s + German text
uv run vnpipe voice asr            # GPU host from [voice.asr]; skips sections already in voice/asr
uv run vnpipe voice build          # align + map + reports
uv run vnpipe voice cut            # clips
uv run vnpipe renpy                # voice statements, clips, credits
```

Add `--scenes a,b` to restrict. Unreleased vnpipe: `uv run --with-editable ../vnpipe ...`.

## Scenes done and coverage

| Scene | Voiced speeches | ASR coverage |
|---|---|---|
| `calle_1` | 23/25 | 92.4 % |
| `jardin_marta` | 41/42 | 94.6 % |

The unvoiced ones are speeches Llorente added or merged (see the reports).

## Notes

- Llorente keeps the order of speeches, but he sometimes adds a speech, merges two or rewrites
  an exchange; those are dropped by the length-ratio check. The Spanish text is a verse
  translation, so a clip follows the German meaning, not the Spanish words.
- Pronunciation and reader quality vary per role; the narrator's speaker-name readings
  are excluded by alignment, not by hand.
- Licensing: LibriVox recordings are public domain; credits list the readers (`[voice].credits`).
