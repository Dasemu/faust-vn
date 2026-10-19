# Art bible

The look of every asset is fixed here before anything is generated. Prompts are
assembled mechanically: **style base prompt + kind template + asset prompt**. The exact
strings live in `assets/assets.json` (each style's `base_prompt` and `templates`, and each
asset's `prompt`); this document explains them.

The player chooses between two art styles (first-launch picker, Preferences): **Pictórico**
(`painterly`, the default and fallback) and **Anime** (`anime`). Every asset has one
rendition per style under `assets/{bg,sprites}/<style>/`; an asset without an approved
anime rendition shows its painterly one.

## Look (painterly)

- **Era and medium**: a romantic 19th-century illustrated edition of *Faust* — oil
  painting with the drawing discipline of a steel engraving (think Delacroix's Faust
  lithographs, Kaulbach, Friedrich's skies). Painted, not photographic, not anime.
- **Palette**: muted and earthy — umber, ochre, slate blue, ivory, deep crimson as the
  only saturated accent (reserved for Mephistopheles and the Earth Spirit). Heaven gets
  warm gold and pale blue, never neon.
- **Proportions**: semi-realistic adults, natural heads (about 1:7.5), no exaggerated eyes.
- **Lighting**: one warm key light from the upper left, soft chiaroscuro, deep but not
  crushed shadows. Night scenes keep the same direction (lamp light from the left).
- **Never**: text, letters, signatures, watermarks, frames, UI, modern objects.

## Base prompt (painterly)

> Hand-painted romantic 19th-century oil painting on canvas with the fine linework of a steel engraving, as in an illustrated 1850s edition of Goethe's Faust (in the spirit of Delacroix's Faust lithographs and Caspar David Friedrich). Clearly painted, NOT photorealistic, NOT a 3D render, NOT digital concept art: visible loose brushstrokes, subtle engraved cross-hatching in the shadows, slightly aged varnish. Muted earthy palette of umber, ochre, slate blue and ivory with restrained deep crimson accents. Soft chiaroscuro, single warm key light from the upper left. Semi-realistic proportions. No text, no letters, no signature, no watermark, no frame, no border.

The first calibration image (with a softer wording) came out as glossy digital concept
art, hence the explicit "NOT photorealistic, NOT a 3D render" clause.

## Kind templates

**Background** (16:9): wide establishing shot, eye level, empty foreground band at the
bottom third so sprites can stand in front, no people unless the asset prompt says so.

**Sprite** (2:3): one character, standing, framed from the top of the head to mid-thigh (legs and feet not visible), centred, body
turned slightly to the viewer, whole head and both hands inside the frame with margin
above the head. Background is a **perfectly flat, uniform chroma-green (#00B140) field**
with no gradient, floor, shadow or props — so it can be keyed out. No green in costumes.

**Expression variant**: generated with the base sprite as `reference_images`; the prompt
demands the identical character, costume, framing, lighting and green field and changes
only face (and hands where noted). Identity drift → regenerate.

## Anime style

Same cast, scenes and per-asset prompts; only the style base prompt and the background
template change (the sprite and variant templates are shared). Adults only: expressive
eyes, but mature proportions, not chibi, not childlike, not moe. Palette: deep indigo,
umber, crimson, parchment ivory, gold accents. Backgrounds are lush painted anime
background art.

> High-quality modern Japanese visual novel art (anime style) for a gothic-romantic adaptation of Goethe's Faust. Clean, confident lineart; cel shading with soft gradient highlights and subtle rim light; expressive eyes but mature adult anatomy and proportions (not chibi, not childlike, not moe). Elegant historically grounded 16th-century German costume and architecture. Harmonious palette of deep indigo, umber, crimson and parchment ivory with gold accents. Polished commercial visual-novel finish. No text, no letters, no signature, no watermark, no frame, no border.

Background template: "Visual novel background, 16:9 wide establishing shot at eye level,
lush painted anime background art with atmospheric lighting and depth, empty foreground band
in the bottom third, no people unless described."

Generate with `vnpipe assets prompt ID --style anime`, import with `--style anime`; run
`vnpipe assets check` before approving (variants must differ from their reference, sprite
coverage and top edge, backgrounds 1920x1080). The existing painterly sprites were framed
to the knees; new generations (both styles) use the head-to-mid-thigh framing.

## Cast (only characters drawn as sprites)

| Id | Description | Expressions |
|---|---|---|
| `faust` | Scholar in his fifties, gaunt, deep-set tired eyes, greying shoulder-length hair, short grey beard; dark umber academic gown with fur collar over a black doublet; 16th-century German. | neutral (brooding), anguished, ecstatic (awed, lit from above), fearful (recoiling) |
| `mephisto` | Lean man of no clear age, sharp features, arched brows, pointed black beard, sardonic mouth; 16th-century nobleman in deep crimson and black doublet, short black cape, black beret with a single red rooster feather. No horns, no tail. | neutral, sly (smirk), scornful, deferent (mock bow, hand on chest) |
| `director` | Stout middle-aged theatre impresario, late 18th century; brown frock coat, buff waistcoat, tied grey wig, holding a ledger. | neutral, pleased, worried |
| `poet` | Young pale man, long dark wavy hair, open white shirt collar, dark slate-blue coat; holds a quill. | neutral (dreamy), inspired, indignant |
| `clown` | Jovial comedian, round ruddy face, motley of red, ochre and slate-blue diamonds, white ruff. | neutral, laughing, mocking |

Not drawn as sprites (see `docs/adaptation-rules.md`): the Lord (a throne of light), the
archangels (part of the heaven background), the Earth Spirit (a lighting change of the
study), the Dedicatoria's lyric voice (full-screen text).

## Backgrounds

| Id | Content |
|---|---|
| `bg_dedication` | Twilight sky of drifting mist; faint translucent figures half-formed in the clouds, no faces. Also the main-menu image. |
| `bg_theatre` | Empty stage of a small late-18th-century German wooden theatre, painted flats, candle footlights, rehearsal daylight from high windows. |
| `bg_heaven` | Celestial realm above luminous clouds, sun and stars; three robed, winged archangels in white and gold, small and distant, singing. |
| `bg_heaven_lord` | Same heavens; a throne-shaped radiance of golden light with no visible figure, heavenly hosts as faint silhouettes. |
| `bg_study` | Narrow, high-vaulted Gothic study at night: books, parchments, alembics, a skull, a lamp on a desk with a great open book, moonlight through leaded glass. |
| `bg_study_macrocosm` | Same study (reference `bg_study`); a golden cosmic diagram of rings and stars floats glowing above the open book. |
| `bg_study_spirit` | Same study (reference `bg_study`) flooded with trembling red light; a towering, indistinct column of flame-like presence; no clear face. |

## Process

1. Generate the base asset, inspect it, regenerate if off-model (max 20 generations/hour
   on the ChatGPT image MCP).
2. Sprites: key out the green field (`vnpipe assets process`), inspect the alpha edges.
3. Record prompt, generation id, sha256 and status in `assets.json`. Anything not
   approved falls back to a generated placeholder.
