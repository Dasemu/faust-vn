# Lessons

Recurring problems and what worked. Read before starting; add an entry when a mistake repeats.

- The sandbox masks `.git/config` (and `.git/config.lock`); git commands that write config
  (`git remote add`) must run outside the sandbox.
- `~/.cache/uv` is read-only inside the sandbox: export `UV_CACHE_DIR=$TMPDIR/uv-cache`
  before any `uv` command.
