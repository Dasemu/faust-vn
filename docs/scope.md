# Scope

The adaptation covers all of *Fausto*, Part I (Goethe, transl. Teodoro Llorente), from
Project Gutenberg #68566.

## Included

From the `DEDICATORIA` heading (raw line 1092) up to, but excluding, the first `BREVE RESEÑA`
line (raw line 11038), the title of Llorente's prose summary of Part II, which is out of scope.
The last scene is `CÁRCEL` (the printed heading; the prison scene), ending with the
voice from within, "¡Enrique! ¡Enrique!".

| Scene id | Heading | Verse lines | Directions | Cast lines | Speeches |
|---|---|---|---|---|---|
| `dedicatoria` | DEDICATORIA | 32 | 0 | 0 | (no speaker) |
| `prologo_teatro` | PRÓLOGO EN EL TEATRO | 254 | 0 | 1 | 11 |
| `prologo_cielo` | PRÓLOGO EN EL CIELO | 162 | 2 | 1 | 19 |
| `noche` | DE NOCHE | 543 | 10 | 0 | 32 |
| `puertas_ciudad` | A LAS PUERTAS DE LA CIUDAD | 550 | 7 | 1 | 53 |
| `gabinete_1` | GABINETE DE ESTUDIO | 425 | 2 | 0 | 41 |
| `gabinete_2` | GABINETE DE ESTUDIO | 753 | 7 | 1 | 87 |
| `taberna_auerbach` | TABERNA DE AUERBACH EN LEIPZIG | 396 | 19 | 1 | 124 |
| `cocina_bruja` | COCINA DE LA BRUJA | 342 | 24 | 1 | 61 |
| `calle_1` | CALLE | 105 | 4 | 1 | 25 |
| `cuartito` | AL CAER LA TARDE | 180 | 11 | 1 | 11 |
| `paseo` | PASEO | 88 | 1 | 1 | 13 |
| `casa_vecina` | CASA DE LA VECINA | 237 | 4 | 0 | 63 |
| `calle_2` | CALLE | 73 | 0 | 1 | 17 |
| `jardin` | JARDÍN | 223 | 9 | 1 | 52 |
| `pabelloncito` | UN PABELLONCITO EN EL JARDÍN | 27 | 3 | 1 | 15 |
| `bosques_cavernas` | BOSQUES Y CAVERNAS | 235 | 1 | 0 | 20 |
| `aposento_margarita` | APOSENTO DE MARGARITA | 40 | 0 | 0 | 1 |
| `jardin_marta` | JARDÍN DE MARTA | 211 | 2 | 1 | 42 |
| `fuente` | EN LA FUENTE | 74 | 1 | 1 | 14 |
| `muros` | EN LOS MUROS DE LA CIUDAD | 28 | 1 | 0 | 1 |
| `calle_noche` | DE NOCHE | 221 | 5 | 0 | 36 |
| `catedral` | CATEDRAL | 57 | 3 | 0 | 12 |
| `valpurgis` | NOCHE DE SANTA VALPURGIS | 530 | 2 | 1 | 77 |
| `intermedio` | INTERMEDIO | 176 | 1 | 0 | 44 |
| `dia_nebuloso` | DÍA NEBULOSO | 22 | 2 | 0 | 13 |
| `noche_campo` | NOCHE | 6 | 1 | 0 | 6 |
| `carcel` | CÁRCEL | 229 | 9 | 1 | 52 |

Total: 6,219 verse lines (the Spanish translation is longer than the 4,612 lines of the
German; in the two prose scenes a paragraph counts as one line).

## Scene rules

- Repeated headings get an `occurrence` in `work.toml`: `GABINETE DE ESTUDIO` (`gabinete_1`,
  `gabinete_2`), `CALLE` (`calle_1`, `calle_2`) and `DE NOCHE` (`noche`, `calle_noche`).
  Scenes in the same place share a `location` (`study`, `street`, `garden`, `margaret_room`).
- `noche` keeps its prototype lines (ids up to `noche_0187`); the scope used to
  end at `(Llaman.)` (`noche_0188`) and the scene now continues with Wagner and the Easter bells.
- `CAMPESINOS BAJO LOS TILOS` is a section title inside `puertas_ciudad`; `INTERMEDIO` is the
  *Sueño de la noche de Walpurgis* (its illustration caption is dropped).
- `dia_nebuloso` and `noche_campo` (`NOCHE`) are printed in prose (`format = "prose"`).
- Capitalised lines such as `ENTRA UN ESTUDIANTE` are listed in `[parser] direction_headings`.
- `CANCIÓN DE LOS SOLDADOS` is mapped as a speaker (`soldiers`) because verse follows it.
- Times of day are editorial: the text rarely says; `timeless` is used for the witch's kitchen
  and the heavens.

## Cast

Named characters have their own id; anonymous one-off speakers are grouped
(`artisans`, `servant_girls`, `students`, `citizens`, `peasants`, `apes`, `witches`,
`walpurgis_guests`, `dream_figures`, `voices`, ...; see `[speakers]`). The grouped speaker's
printed heading is not kept. `sprite = true` for faust, mephisto, wagner, margarita, marta,
valentin, witch, student, director, poet and clown; the new ones map every emotion to
`neutral` until their art exists.

## Stripped

- Gutenberg header/footer, transcriber's note and licence text.
- Title pages, table of contents, and Llorente's prologue letter ("A Vicente W. Querol").
- `[Ilustración...]` markers (the book's own engravings), including multi-line captions.
- Llorente's footnotes (definitions and `[12]` markers).
- Everything after the end marker.

## Scope rule

Defined in `work.toml` under `[scope]` and applied by `vnpipe.text.clean`:

- Start: the first line whose stripped text equals `start_marker`. Table of contents entries
  carry page numbers, so they never match as whole lines.
- End: the `end_occurrence`-th line after the start whose stripped text equals `end_marker`
  (exclusive).
- Illustrations and footnotes are dropped, trailing whitespace is removed, blank runs collapse
  to one.

`vnpipe parse` writes the result to `data/play.txt` and the structured form to
`data/parsed.json` (line ids `<scene>_<NNNN>`, numbered from 0001 per scene;
`src_line` points back to the raw file).
