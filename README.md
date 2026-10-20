# faust-vn

A visual novel of the whole of *Faust, Part I* (Goethe), in Teodoro Llorente's public-domain
Spanish translation: 28 scenes from the Dedicatoria to the prison, about 31,000 words of
verse, never rewritten. It is the first work built with [`vnpipe`](../vnpipe), the reusable
"classic novels to visual novels" pipeline.

The game is in Spanish. Art is AI-generated (see [docs/licensing.md](docs/licensing.md)).

## What is in the game

- **Art styles**: *Pictórico* (an 1850s oil-and-engraving look, the default) and *Anime*.
  The player picks one at the first launch and can change it any time in Preferences.
- **Music**: public-domain and CC BY-SA classical recordings. Each line's mood
  (contemplative, comic, sacred, ominous, mystical) picks a looping playlist; some scenes have
  their own piece (Mephisto Waltz in Auerbach's tavern, Dies irae in the cathedral, Gretchen am
  Spinnrade in Margarita's room, Bach's Easter cantata for the Easter choruses). See
  [docs/music.md](docs/music.md).
- **Voice**: the German original read by LibriVox's public-domain dramatic reading
  plays under the Spanish text, like subtitled anime; all 28 scenes. Volume slider in Preferences. See [docs/voice.md](docs/voice.md).
- **Main menu**: title and subtitle over the study, *Escenas* (replay any scene you have
  reached) and *Créditos* (text, art and music attributions).
- **Reading**: each scene opens with a title card (heading plus place and time); text types at
  40 characters/second (change it in Preferences) and a blinking arrow marks the end of a box;
  verse boxes hold at most 4 lines, and the lyric scenes use full-page stanzas.

## How to play

Needs the [Ren'Py](https://www.renpy.org/) 8.5 SDK (`tools/renpy-sdk` or `RENPY_SDK`):

```bash
tools/renpy-sdk/renpy.sh vn   # play the generated project
```

## Quick start

`vnpipe` is a path dependency: clone it next to this repo and adjust
`[tool.uv.sources]` in `pyproject.toml` if it lives elsewhere.

```bash
uv sync
uv run vnpipe fetch          # download the source into data/raw
uv run vnpipe parse          # data/raw -> data/parsed.json
uv run vnpipe renpy          # data/annotated.json + audio/ -> vn/
tools/renpy-sdk/renpy.sh vn  # play (Ren'Py 8.5.3 SDK, see docs/running.md)
```

`vn/` is generated and its `game/audio/` is not committed (it copies `audio/`): run
`uv run vnpipe renpy` after cloning. Web and desktop builds: [docs/running.md](docs/running.md).
Everything specific to this text (cast, scenes and their subtitles, staging, music
overrides, menu background) is in `work.toml`.

Lint, tests and build instructions: [docs/running.md](docs/running.md).
Plan and layout: [docs/plan.md](docs/plan.md).
