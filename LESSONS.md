# Lessons

Recurring problems and what worked. Read before starting; add an entry when a mistake repeats.

- The sandbox masks `.git/config` (and `.git/config.lock`); git commands that write config
  (`git remote add`) must run outside the sandbox.
- `~/.cache/uv` is read-only inside the sandbox: export `UV_CACHE_DIR=$TMPDIR/uv-cache`
  before any `uv` command.
- The sandbox mounts char-device placeholders (`.claude/`, `.mcp.json`, dotfiles) in the
  working dir; they are gitignored, never `git add` them.
- `renpy lint` passing does not mean the game runs: the main menu crashed on missing GUI
  images. Always run the end-to-end playthrough (`vnpipe renpy --with-test` + `renpy.sh test`,
  see docs/running.md) and, ideally, click through the web build.
- Ren'Py SDK commands write to `~/.renpy`: prefix them with `HOME=$TMPDIR/renpy-home`
  inside the sandbox. `web_build` leaves `vn/progressive_download.txt` (gitignored).
- ChatGPT image MCP: reference-image variants sometimes come back byte-identical to the
  base; compare sha256 against the base before approving. Sprites drift to full-body
  unless the prompt says "cropped just below the knees".
- Small-model annotators label whole speeches with one emotion and lose stage presence
  across chunks; fix with `work.toml` overrides (pinned cast, emotion ranges), not by
  hand-editing annotated.json.
- The pipeline lives in `../vnpipe`: a pipeline bug is fixed there (and tested with its
  fixtures), then `uv run vnpipe renpy` is re-run here; `vn/` must not change unless intended.
