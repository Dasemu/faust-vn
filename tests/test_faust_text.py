"""Faust-specific checks on the real text and the committed data."""

import argparse
import json
import shutil
from pathlib import Path

import pytest
from vnpipe import renpy_gen, text
from vnpipe.config import load_work
from vnpipe.schema import validate

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data/raw/pg68566.txt"


@pytest.mark.skipif(not RAW.is_file(), reason="raw Gutenberg file not downloaded")
def test_real_file_integration():
    work = load_work(ROOT)
    _, parsed = text.build(RAW.read_bytes(), work.data)
    assert [s["id"] for s in parsed["scenes"]] == [
        "dedicatoria",
        "prologo_teatro",
        "prologo_cielo",
        "noche",
    ]
    known = set(work.speakers.values())
    for s in parsed["scenes"]:
        assert s["lines"]
        assert {ln["speaker"] for ln in s["lines"]} - {None} <= known


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
