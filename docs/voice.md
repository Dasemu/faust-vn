# Voice track (German original under the Spanish text)

The German original of *Faust I* is read by LibriVox's public-domain dramatic reading
("Faust: Der Tragödie erster Teil", one reader per role, 28 sections = our 28 scenes in order).
`vnpipe voice` (see `../vnpipe/docs/voice.md`) cuts one clip per German speech and the game plays
it under the matching Spanish speech. Speeches it cannot map with confidence stay silent.

## Data

- `work.toml` `[voice]`: source URLs, `scenes` (optional subset; omit to run all 28),
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

All 28 scenes, 854/942 speeches voiced, 72 MB of clips.

| Scene | Voiced speeches | ASR coverage |
|---|---|---|
| `aposento_margarita` | 1/1 | 90,2 % |
| `bosques_cavernas` | 18/20 | 90,3 % |
| `calle_1` | 23/25 | 92,4 % |
| `calle_2` | 17/17 | 88,0 % |
| `calle_noche` | 33/36 | 89,5 % |
| `carcel` | 48/52 | 94,6 % |
| `casa_vecina` | 56/62 | 90,2 % |
| `catedral` | 8/12 | 87,4 % |
| `cocina_bruja` | 53/61 | 88,4 % |
| `cuartito` | 9/11 | 85,1 % |
| `dedicatoria` | 1/1 | 93,2 % |
| `dia_nebuloso` | 13/13 | 90,1 % |
| `fuente` | 12/14 | 88,2 % |
| `gabinete_1` | 37/41 | 91,6 % |
| `gabinete_2` | 84/87 | 90,3 % |
| `intermedio` | 42/44 | 90,3 % |
| `jardin` | 46/52 | 87,8 % |
| `jardin_marta` | 41/42 | 94,6 % |
| `muros` | 1/1 | 95,2 % |
| `noche` | 32/32 | 87,5 % |
| `noche_campo` | 5/6 | 93,3 % |
| `pabelloncito` | 13/15 | 94,7 % |
| `paseo` | 11/13 | 91,5 % |
| `prologo_cielo` | 19/19 | 90,3 % |
| `prologo_teatro` | 11/11 | 93,5 % |
| `puertas_ciudad` | 52/53 | 91,8 % |
| `taberna_auerbach` | 97/124 | 87,5 % |
| `valpurgis` | 71/77 | 90,7 % |
| **Total** | **854/942** (91 %) | |

The unvoiced ones are speeches Llorente added, merged or split (worst: the rapid-fire exchange at the end of `taberna_auerbach`); see `voice/report/`.

Faust's reader is the roughest, so `[voice.filters] faust` applies a gentle highpass + `afftdn` + presence EQ before loudnorm. Whisper re-transcription of 30 Faust clips: recall 94,2 % without the filter, 93,2 % with it (about 1 point lower, near ASR noise).

## Notes

- Llorente keeps the order of speeches, but he sometimes adds a speech, merges two or rewrites
  an exchange; those are dropped by the length-ratio check. The Spanish text is a verse
  translation, so a clip follows the German meaning, not the Spanish words.
- Pronunciation and reader quality vary per role; the narrator's speaker-name readings
  are excluded by alignment, not by hand.
- Licensing: LibriVox recordings are public domain; credits list the readers (`[voice].credits`).
