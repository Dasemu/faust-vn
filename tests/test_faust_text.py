"""Faust-specific checks on the real text and the committed data."""

import argparse
import hashlib
import json
import shutil
from pathlib import Path

import pytest
from vnpipe import renpy_gen, text
from vnpipe.config import load_work
from vnpipe.schema import validate

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data/raw/pg68566.txt"


SCENE_IDS = [
    "dedicatoria",
    "prologo_teatro",
    "prologo_cielo",
    "noche",
    "puertas_ciudad",
    "gabinete_1",
    "gabinete_2",
    "taberna_auerbach",
    "cocina_bruja",
    "calle_1",
    "cuartito",
    "paseo",
    "casa_vecina",
    "calle_2",
    "jardin",
    "pabelloncito",
    "bosques_cavernas",
    "aposento_margarita",
    "jardin_marta",
    "fuente",
    "muros",
    "calle_noche",
    "catedral",
    "valpurgis",
    "intermedio",
    "dia_nebuloso",
    "noche_campo",
    "carcel",
]
# (line count, sha256 prefix of the lines) of the four prototype scenes before the full text.
# `noche` grew when the scope was extended; its first 187 lines are the old scene.
PROTOTYPE = {
    "dedicatoria": (32, "3934c9136e9e107d"),
    "prologo_teatro": (255, "df9c96c1e5923065"),
    "prologo_cielo": (165, "3725ec49b88b3470"),
    "noche": (187, "f4faeb265d7df507"),
}


def _digest(lines):
    payload = json.dumps(lines, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


@pytest.fixture(scope="module")
def parsed():
    return json.loads((ROOT / "data/parsed.json").read_text(encoding="utf-8"))


def _scene(parsed, scene_id):
    return next(s for s in parsed["scenes"] if s["id"] == scene_id)


@pytest.mark.skipif(not RAW.is_file(), reason="raw Gutenberg file not downloaded")
def test_real_file_integration():
    work = load_work(ROOT)
    _, parsed = text.build(RAW.read_bytes(), work.data)
    assert [s["id"] for s in parsed["scenes"]] == SCENE_IDS
    known = set(work.speakers.values())
    assert known <= set(work.cast)
    for s in parsed["scenes"]:
        assert s["lines"]
        assert {ln["speaker"] for ln in s["lines"]} - {None} <= known


def test_scene_config(parsed):
    work = load_work(ROOT)
    assert [s["id"] for s in work.scenes] == SCENE_IDS
    assert len({s["id"] for s in work.scenes}) == len(SCENE_IDS)
    for s in work.scenes:
        assert s["time_of_day"] in {"dawn", "day", "dusk", "night", "timeless"}
        assert s["location"]
    assert _scene(parsed, "gabinete_2")["heading"] == _scene(parsed, "gabinete_1")["heading"]
    assert _scene(parsed, "calle_noche")["heading"] == _scene(parsed, "noche")["heading"]
    locations = {s["id"]: s["location"] for s in work.scenes}
    assert locations["gabinete_2"] == locations["gabinete_1"] == locations["noche"] == "study"
    assert locations["cuartito"] == locations["aposento_margarita"]


def test_cast_config():
    work = load_work(ROOT)
    for cid, c in work.cast.items():
        assert c["color"].startswith("#")
        if c.get("sprite") is True:
            assert "neutral" in c["expressions"], cid
    sprites = {cid for cid, c in work.cast.items() if c.get("sprite") is True}
    assert sprites >= {
        "faust",
        "mephisto",
        "wagner",
        "margarita",
        "marta",
        "valentin",
        "witch",
        "student",
        "lisa",
        "director",
        "poet",
        "clown",
    }
    for cid in ("frosch", "brander", "siebel", "altmayer", "evil_spirit", "artisans"):
        assert work.cast[cid]["sprite"] is False


def test_prototype_scenes_unchanged(parsed):
    for scene_id, (count, digest) in PROTOTYPE.items():
        lines = _scene(parsed, scene_id)["lines"][:count]
        assert _digest(lines) == digest, scene_id
    noche = _scene(parsed, "noche")["lines"]
    assert noche[144]["id"] == "noche_0145" and noche[144]["kind"] == "direction"
    assert noche[187]["text"] == "Llaman."


def test_scope_ends_before_the_part_two_summary(parsed):
    last = _scene(parsed, "carcel")["lines"]
    assert last[-1]["text"] == "¡Enrique! ¡Enrique!" and last[-1]["speaker"] == "voices"
    assert last[-2]["kind"] == "direction" and last[-2]["text"].startswith("Desaparece con")
    assert last[-3]["text"] == "¡Tú, conmigo!" and last[-3]["speaker"] == "mephisto"
    assert "BREVE RESEÑA" not in (ROOT / "data/play.txt").read_text(encoding="utf-8")


def test_spinning_wheel_song(parsed):
    rueca = _scene(parsed, "aposento_margarita")["lines"]
    assert [ln["text"] for ln in rueca[:2]] == ["Huyeron del alma", "la dicha y la paz,"]
    assert {ln["speaker"] for ln in rueca} == {"margarita"}
    assert len(rueca) == 40 and rueca[-1]["text"] == "de tanto besar!"


def test_prose_scenes(parsed):
    for scene_id, count in (("dia_nebuloso", 22), ("noche_campo", 6)):
        verse = [ln for ln in _scene(parsed, scene_id)["lines"] if ln["kind"] == "verse"]
        assert len(verse) == count
        assert all(ln["indent"] == 0 for ln in verse)
    first = _scene(parsed, "dia_nebuloso")["lines"]
    assert first[1]["speaker"] == "faust" and first[1]["text"].startswith("¡En la miseria!")


def test_grouped_and_named_speakers(parsed):
    def speakers(scene_id):
        return {ln["speaker"] for ln in _scene(parsed, scene_id)["lines"]} - {None}

    assert {"artisans", "citizens", "students", "peasants", "soldiers"} <= speakers(
        "puertas_ciudad"
    )
    assert {"frosch", "brander", "siebel", "altmayer"} <= speakers("taberna_auerbach")
    assert {"valentin", "crowd"} <= speakers("calle_noche")
    assert {"witches", "walpurgis_guests", "trio"} <= speakers("valpurgis")
    assert {"oberon", "titania", "puck", "ariel", "dream_figures"} <= speakers("intermedio")
    assert "evil_spirit" in speakers("catedral")


@pytest.mark.skipif(not RAW.is_file(), reason="raw Gutenberg file not downloaded")
def test_cli_parse_is_byte_identical(tmp_path):
    work_dir = tmp_path / "faust"
    (work_dir / "data/raw").mkdir(parents=True)
    shutil.copy(ROOT / "work.toml", work_dir / "work.toml")
    shutil.copy(RAW, work_dir / "data/raw/pg68566.txt")
    args = argparse.Namespace(work=work_dir)
    assert text.cmd_parse(args) == 0
    first = (work_dir / "data/parsed.json").read_bytes()
    assert text.cmd_parse(args) == 0
    assert (work_dir / "data/parsed.json").read_bytes() == first
    assert first.endswith(b"\n")
    assert (work_dir / "data/play.txt").read_text(encoding="utf-8").startswith("DEDICATORIA\n")
    # the committed data is what the parser produces
    assert first == (ROOT / "data/parsed.json").read_bytes()


def test_from_parsed_annotations():
    work = load_work(ROOT)
    parsed = json.loads((ROOT / "data/parsed.json").read_text(encoding="utf-8"))
    annotated = renpy_gen.annotations_from_parsed(work, parsed)
    validate(annotated, "annotated")
    teatro = next(s for s in annotated["scenes"] if s["id"] == "prologo_teatro")
    stage = [ln["ann"]["on_stage"] for ln in teatro["lines"] if ln["kind"] == "verse"]
    assert stage[0] == [{"character": "director", "position": "left"}]
    assert {e["character"]: e["position"] for e in stage[-1]} == {
        "director": "left",
        "poet": "right",
        "clown": "center",
    }
    dedication = annotated["scenes"][0]["lines"][0]["ann"]
    assert dedication["speaker"] == "poet_voice" and dedication["on_stage"] == []
    cielo = next(s for s in annotated["scenes"] if s["id"] == "prologo_cielo")
    assert cielo["lines"][0]["ann"]["on_stage"] == []
    # the real project generates (cues all resolve) without writing anything
    renpy_gen.render_script(work, annotated, set())


def test_annotated_data_is_valid():
    data = json.loads((ROOT / "data/annotated.json").read_text(encoding="utf-8"))
    validate(data, "annotated")
