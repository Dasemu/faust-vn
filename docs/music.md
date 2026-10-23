# Music

Background music lives in `audio/<mood>/` (moods used by the game: `contemplative`, `comic`,
`sacred`, `ominous`, `mystical`; `none` is silence) and `audio/scenes/` (pieces tied to specific
Faust scenes). `audio/credits.toml` is the manifest: one `[[track]]` per file with title,
composer, performer, source page, direct file URL, exact license, attribution text, original and
processed duration and the sha256 of the downloaded original.

## How it plays

`vnpipe renpy` copies `audio/**/*.ogg` into `vn/game/audio/`. A line's annotation mood plays
`audio/<mood>/` as a looping playlist (sorted by file name; a track that already plays is not
restarted). `work.toml` overrides it: `[staging.<scene>].music` fixes a scene's music and a cue
`music = ...` switches from its line on (`"<mood>"`, `"track:<path under audio/>"`, `"none"`,
and `"auto"` to return to the annotation moods). Current choices:

| Where | Music |
|---|---|
| `catedral` | `scenes/mozart-dies-irae.ogg` |
| `taberna_auerbach` | `scenes/mephisto-waltz-1.ogg` |
| `aposento_margarita` | `scenes/gretchen-am-spinnrade.ogg` |
| `noche`, from `noche_0473` (bells and Easter choruses, to the end of the scene) | `scenes/bach-bwv4-christ-lag.ogg` |

The game credits screen prints every `attribution` of `credits.toml` verbatim (CC BY-SA); when a track has
`attribution_es` (the same credit in Spanish) that one is shown instead.

## Licensing rule

A track is accepted only if **both** hold:

1. The composition is in the public domain (all composers here died before 1950).
2. The *recording* is public domain, CC0, CC-BY or CC-BY-SA, as stated on the source page
   (Wikimedia Commons file page, or an archive.org item page). No NC/ND, no YouTube rips.

Most tracks are Musopen recordings (Musopen Kickstarter / Set Chopin Free projects) dedicated to
the public domain. CC BY-SA tracks (`mephisto-waltz-1`, `mozart-dies-irae`, `bach-bwv4-christ-lag`)
require the attribution text in `credits.toml` to be shown (the *Créditos* screen does) and derived
audio to stay under the same license. `gretchen-am-spinnrade` is a 1927 US recording (public domain
in the US since 2023, marked Public Domain Mark 1.0 on archive.org).

## Selection

Instrumental where possible, since the text is Spanish verse. Scene pieces follow the Faust
tradition: Liszt's Mephisto Waltz No. 1 (Auerbach's tavern), Mozart's Dies irae (cathedral),
Schubert's Gretchen am Spinnrade (Margarita's spinning wheel), Bach's Easter cantata BWV 4
(Easter chorus).

## Processing

Originals are kept outside the repo. Files are converted with ffmpeg to OGG Vorbis (`-q:a 2.5`,
stereo, 44.1 kHz), normalised with `loudnorm=I=-20:TP=-2`, and trimmed to at most 4 minutes with a
3 s fade-out when trimmed. Total size is about 31 MB.
