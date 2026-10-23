# Adaptation rules (Faust)

The generic rules (text is never rewritten, NVL for lyric passages, text rhythm, sprites and
expressions, transitions, music, the `work.toml` override layer) live in vnpipe:
`../vnpipe/docs/adaptation-rules.md`. This file records how they apply to Faust; the
decisions themselves are in `work.toml` (`[staging.*]`, `[[cues]]`, `[[overrides]]`).

## Application to Faust

- Sprites appear in dialogue scenes only, and only for characters with `sprite = true`
  (Faust, Mephistopheles, Wagner, Margarita, Marta, Valentín, the Witch, the Student, Luisa,
  and the theatre trio). Crowds, choruses, spirits, the Lord and the Evil Spirit are never drawn.
- `[staging.*].cast` pins only characters who stay on stage the whole scene (Faust left,
  Mephistopheles right, a third character centre); characters who enter or leave later come
  from the annotation. A pinned character cannot leave (`hide_all` only lasts one box).
- Lyric passages use NVL: the Dedicatoria, the heavens' hymn, Margarita's songs
  (`aposento_margarita`, the ballad of Thule, `muros`), the witches' chorus and the
  Intermezzo.
- The ineffable is never drawn. The Lord is a radiance (`bg_heaven_lord`); the Earth Spirit
  is a lighting change plus a flash and a shake (`bg_study_spirit`). Their lines still
  carry a name and colour.
- The Dedicatoria (the poet's own voice) and the archangels' hymn are NVL poems over a
  background.
- The three archangels are painted into `bg_heaven`, not drawn as three sprites.
- One background per location, plus variants only where the text changes the light
  (macrocosm sign, Earth Spirit, heaven closing).
- The prototype ships without audio; music moods are annotated but only played if
  `vn/game/audio/<mood>.ogg` exists.

## Staging (work.toml)

| Scene | Base | Notes |
|---|---|---|
| Dedicatoria | `bg_dedication`, NVL | The poet's voice; no speaker name. |
| Prólogo en el teatro | `bg_theatre`, ADV | Director, Poet and Clown as sprites. |
| Prólogo en el cielo | `bg_heaven`, NVL | Hymn as full-screen text; switches to ADV + `bg_heaven_lord` when Mephistopheles speaks; heaven closes → dark tint. |
| De noche | `bg_study`, ADV | Macrocosm sign → `bg_study_macrocosm`; Earth Spirit's sign → red tint; apparition → `bg_study_spirit` + flash + shake. |
| Puertas de la ciudad | `bg_city_gates`, ADV | No pins (crowd first, Faust and Wagner enter later); dusk tint at Faust's sunset speech. |
| Gabinete 1 | `bg_study`, ADV | Faust pinned left; red tint as the poodle swells, flash + shake when Mephistopheles appears, dark tint for the spirits' lullaby. |
| Gabinete 2 | `bg_study_day`, ADV | Mephistopheles pinned right; red tint while the pact is signed in blood. |
| Taberna de Auerbach | `bg_tavern`, ADV | Students are never drawn; flame (red, flash, shake) when the wine ignites; hide all as Mephistopheles vanishes. |
| Cocina de la bruja | `bg_witch_kitchen`, ADV | Faust left, Mephistopheles right; the Witch comes from annotation; cauldron flare (flash, red, shake), then back to normal. |
| Calle 1 / Calle 2 | `bg_street`, ADV | Faust pinned left (calle 2: Mephistopheles right). |
| Al caer la tarde | `bg_margaret_room`, ADV | Ballad of Thule in NVL (cues around it). |
| Paseo | `bg_promenade`, ADV | Mephistopheles pinned right. |
| Casa de la vecina | `bg_neighbour_house`, ADV | Marta pinned left. |
| Jardín | `bg_garden`, ADV | Two couples alternate ("Pasan"); no pins, positions from annotation. |
| Pabelloncito | `bg_garden_pavilion`, ADV | Margarita pinned left. |
| Bosques y cavernas | `bg_forest_cave`, ADV | Faust pinned left. |
| Aposento de Margarita | `bg_margaret_room`, NVL | Spinning-wheel song. |
| Jardín de Marta | `bg_garden`, ADV | Faust pinned left. |
| En la fuente | `bg_fountain`, ADV | Margarita pinned right; Luisa from annotation. |
| En los muros | `bg_city_walls`, NVL | Prayer to the Mater Dolorosa. |
| De noche (calle) | `bg_street_night`, ADV | Dark tint when Valentín dies. |
| Catedral | `bg_cathedral`, ADV | Margarita pinned centre; the Evil Spirit and chorus are voices only; dark tint at the Dies irae, shake when she faints. |
| Noche de Walpurgis | `bg_harz`, ADV | Faust left, Mephistopheles right; witches' chorus in NVL on `bg_harz_summit`, then back to ADV. |
| Intermedio | `bg_intermezzo`, NVL | Oberon, Titania and the dream figures are text only. |
| Día nebuloso / Noche | `bg_field_day` / `bg_field_night`, ADV | Faust left, Mephistopheles right. |
| Cárcel | `bg_prison`, ADV | No pins; dawn at Faust's "el alba" switches to `bg_prison_dawn`. |
