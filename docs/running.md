# Running, linting and building the game

The Ren'Py project in `vn/faust/` is generated; never edit it by hand. All commands run
from the repository root.

## 1. Ren'Py SDK

The SDK is not committed (`tools/` is gitignored). Install **Ren'Py 8.5.3** (SDK
archive from <https://www.renpy.org/latest.html>, `renpy-8.5.3-sdk.tar.bz2`) so that
`tools/renpy-sdk/renpy.sh` exists:

```sh
mkdir -p tools && tar -xjf renpy-8.5.3-sdk.tar.bz2 -C tools && mv tools/renpy-8.5.3-sdk tools/renpy-sdk
```

The SDK already contains the web runtime (`tools/renpy-sdk/web`) and the Linux, Windows
and macOS distribution templates. Inside the sandbox set `HOME=$TMPDIR/renpy-home` for
SDK commands, since Ren'Py writes to `~/.renpy`.

## 2. Regenerate the project

```sh
uv run vnpipe renpy                 # from works/faust/data/annotated.json
uv run vnpipe renpy --from-parsed   # trivial annotations built from parsed.json
uv run vnpipe renpy --out some/dir  # default output: vn/<work id>
```

Generation is deterministic: running it twice gives identical files (no timestamps).
It rewrites `game/{options,gui,screens,support,characters,images,script}.rpy`,
`game/gui/`, `game/fonts/` and `game/images/`; anything else (for example `game/audio/`)
is left alone. Music only appears in the script for moods that have a matching
`game/audio/<mood>.ogg`, so drop files there and regenerate.

Images come from `works/<id>/assets/assets.json` (statuses `processed`, `approved`,
`placeholder`); anything missing or unusable is replaced by a generated placeholder so
the game always runs.

### GUI template and licences

`src/vnpipe/renpy_templates/` holds the default Ren'Py GUI (`gui.rpy`, `screens.rpy`,
`options.rpy` and `gui/*.png`). It was generated once with the SDK's own command and then
edited minimally (dark palette, ivory text, accent `#c9a25b`, Roboto Slab font, NVL
tweaks, `@@TOKEN@@` placeholders for title/build name/about text/menu background):

```sh
tools/renpy-sdk/renpy.sh tools/renpy-sdk/launcher generate_gui OUT --width 1920 --height 1080 \
  --accent '#c9a25b' --boring '#14110e' --template "$PWD/tools/renpy-sdk/gui" --start
```

These files are part of Ren'Py (MIT licence, Tom Rothamel and contributors). The font
`game/fonts/RobotoSlab-*.ttf` is Roboto Slab (Apache 2.0), taken from the SDK
documentation assets.

## 3. Lint

```sh
HOME=$TMPDIR/renpy-home tools/renpy-sdk/renpy.sh vn/faust lint
```

The expected result is a statistics block with no warnings above it.

## 4. Play

```sh
tools/renpy-sdk/renpy.sh vn/faust
```

## 5. Builds (output under `build/`, gitignored)

```sh
# Web (HTML5)
tools/renpy-sdk/renpy.sh tools/renpy-sdk/launcher web_build vn/faust --destination build/web
python3 -m http.server -d build/web 8000     # then open http://localhost:8000

# Linux desktop
tools/renpy-sdk/renpy.sh tools/renpy-sdk/launcher distribute vn/faust --package linux --destination build/dist
```

`--package` also accepts `win` and `mac`; omit it to build every package. The web build
also leaves a `build/web.zip` next to the folder. A web build writes
`vn/faust/progressive_download.txt`; delete it (it is not part of the generated project).
