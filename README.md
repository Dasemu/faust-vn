# faust-vn

A visual novel of the whole of *Faust, Part I* (Goethe), in Teodoro Llorente's public-domain
Spanish translation: 28 scenes from the Dedicatoria to the prison, about 31,000 words of
verse, never rewritten. It is the first work built with [`vnpipe`](https://github.com/Dasemu/vnpipe), the reusable
"classic novels to visual novels" pipeline.

The game is in Spanish, with an English version (Bayard Taylor's public-domain verse
translation, verbatim) selectable in Preferences. Art is AI-generated (see [docs/licensing.md](docs/licensing.md)).
Released under the [GNU GPL v3](LICENSE); the source text and voice recordings are public domain.

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

## Play from a clean clone

For ready-to-run packages, see [Releases](https://github.com/Dasemu/faust-vn/releases).
To run from source, install Git, [uv](https://docs.astral.sh/uv/) and the
**Ren'Py 8.5.3 SDK** as described in [docs/running.md](docs/running.md).
The following commands use Bash on Linux x86-64:

```bash
git clone https://github.com/Dasemu/faust-vn.git
cd faust-vn
uv sync --locked
uv run vnpipe --work . renpy
tools/renpy-sdk/renpy.sh vn
```

Python >=3.12 is required; uv can provision it. `uv sync --locked` installs vnpipe
from the Git revision recorded in `uv.lock`. No sibling checkout or edit to
`[tool.uv.sources]` is needed. To reproduce a release, check out its tag before syncing.

The committed data is sufficient to generate the game: fetching, parsing, annotation
and translation commands are content-development steps, not prerequisites for playing.
`vn/` is generated, including a copy of `audio/` in `vn/game/audio/`; regenerate after cloning.
Separate desktop, web and Android setup and commands are in [docs/running.md](docs/running.md).

Everything specific to this text (cast, scenes and their subtitles, staging, music
overrides, menu background) is in `work.toml`.

Lint, tests and build instructions: [docs/running.md](docs/running.md).
Plan and layout: [docs/plan.md](docs/plan.md).

## Downloads

Releases ship Windows, Linux, macOS and web builds. The Android APK is included only
when CI has the signing secret configured. See [docs/running.md](docs/running.md)
for local builds.
