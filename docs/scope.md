# Scope

The prototype adapts the opening of *Fausto* (Goethe, transl. Teodoro Llorente) from
Project Gutenberg #68566.

## Included

Raw file lines 1092-1921 (`data/raw/pg68566.txt`), i.e. from the `DEDICATORIA`
heading up to, but excluding, the `(_Llaman._)` direction at line 1923.

| Scene id | Heading | Verse lines | Directions | Cast lines | Speeches |
|---|---|---|---|---|---|
| `dedicatoria` | DEDICATORIA | 32 | 0 | 0 | 1 (no speaker) |
| `prologo_teatro` | PRÓLOGO EN EL TEATRO | 254 | 0 | 1 | 11 |
| `prologo_cielo` | PRÓLOGO EN EL CIELO | 162 | 2 | 1 | 19 |
| `noche` | DE NOCHE | 182 | 5 | 0 | 11 |

Total: 630 verse lines (about 15-20 printed pages).

## Where and why it is cut

The scope ends at the Earth Spirit's rejection of Faust ("¿No a ti? Pues dime: ¿a quién?"),
right before the knock that announces Wagner. It is a natural dramatic break: the evocation
ends in Faust's collapse, and the next beat (Wagner, the Easter walk, the pact) is a new
movement.

## Stripped

- Gutenberg header/footer, transcriber's note and licence text.
- Title pages, table of contents, and Llorente's prologue letter ("A Vicente W. Querol").
- `[Ilustración...]` markers (the book's own engravings).
- Everything after the end marker.

## Scope rule

Defined in `work.toml` under `[scope]` and applied by `vnpipe.text.clean`:

- Start: the first line whose stripped text equals `start_marker`. Table of contents entries
  carry page numbers, so they never match as whole lines.
- End: the `end_occurrence`-th line after the start whose stripped text equals `end_marker`
  (exclusive).
- Illustration lines are dropped, trailing whitespace is removed, blank runs collapse to one.

`vnpipe parse` writes the result to `data/play.txt` and the structured form to
`data/parsed.json` (line ids `<scene>_<NNNN>`, numbered from 0001 per scene;
`src_line` points back to the raw file).
