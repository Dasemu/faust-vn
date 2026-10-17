import json
import os
import subprocess
from pathlib import Path

import pytest

from vnpipe import renpy_gen
from vnpipe.config import load_work
from vnpipe.schema import validate

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).parent / "fixtures"
SDK = ROOT / "tools/renpy-sdk/renpy.sh"


@pytest.fixture(scope="module")
def work():
    return load_work(FIXTURES / "mini_work")


@pytest.fixture(scope="module")
def annotated():
    data = json.loads((FIXTURES / "annotated_mini.json").read_text(encoding="utf-8"))
    validate(data, "annotated")
    return data


@pytest.fixture(scope="module")
def project(work, annotated, tmp_path_factory):
    out = tmp_path_factory.mktemp("proj")
    renpy_gen.generate(work, annotated, out)
    return out


@pytest.fixture(scope="module")
def script(project) -> str:
    return (project / "game/script.rpy").read_text(encoding="utf-8")


def scene_block(script: str, scene_id: str) -> list[str]:
    lines = script.split("\n")
    start = lines.index(f"label scene_{scene_id}:")
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("label ")), None)
    if end is None:
        end = len(lines)
    return [ln.strip() for ln in lines[start:end]]


def say_lines(block: list[str]) -> list[str]:
    return [ln for ln in block if ln.startswith("c_")]


def test_escape_text():
    assert renpy_gen.escape_text("a [b] {c}") == "a [[b] {{c}"
    assert renpy_gen.escape_text('say "hi"\\') == 'say \\"hi\\"\\\\'
    assert renpy_gen.escape_text("a\nb") == "a\\nb"


def test_escaping_in_script(script):
    assert "¿qué pensáis [[ahora]?" in script
    assert "Es mi {{anhelo} preferente" in script
    assert 'lo \\"mejor\\" que pueda.' in script


def test_title_card_and_end(script):
    block = scene_block(script, "talk")
    assert 'show text "{size=60}CONVERSACIÓN{/size}" as title_card at truecenter' in block
    assert "with fade" in block
    assert "scene bg theatre at tint_none" in block
    assert script.rstrip().endswith("return")
    assert "Continuará…" in script


def test_nvl_pages_per_stanza(script):
    block = scene_block(script, "lyric")
    says = say_lines(block)
    # 9-line stanza -> pages of 8 and 1, then the 2-line second stanza
    assert [s.count("\\n") + 1 for s in says] == [8, 1, 2]
    assert all(s.startswith("c_poet_voice_nvl ") for s in says)
    assert block.count("nvl clear") == 3
    assert block[-2:] == ["nvl hide dissolve", ""]
    assert not any(ln.startswith("show ") and "vn_" in ln for ln in block)


def test_adv_grouping(script):
    says = say_lines(scene_block(script, "talk"))
    # director's 6 verse lines -> 4 + 2
    assert says[0].count("\\n") == 3
    assert says[1].count("\\n") == 1
    assert says[0].startswith("c_director ")
    # split lines (indent >= 6) get their own boxes
    assert says[2] == 'c_poet "¡Vete, profano!"'
    assert says[3] == 'c_director "Calla, que oye."'
    # stage direction: narrator, own box
    assert says[4] == 'c_narrator "Se aleja."'
    # poet's 3 lines in one box
    assert says[5].count("\\n") == 2


def test_cue_forces_box_break_and_emits_before_line(script):
    block = scene_block(script, "talk")
    cue_start = block.index("# talk_0014 .. talk_0015")
    prefix = block[:cue_start]
    # cue 1: slow bg change with dark tint and sprites hidden, before the Lord's lines
    assert "show bg heaven at tint_dark" in prefix
    assert prefix[prefix.index("show bg heaven at tint_dark") + 1] == "with vn_slow"
    assert "hide poet" in prefix[-6:]
    # Poet's box ended before the cue (box break at cue line)
    assert any("y el ocaso llega." in ln for ln in prefix)


def test_mode_switch_and_flash_shake(script):
    block = scene_block(script, "talk")
    i_nvl = block.index("# talk_0016")
    # nvl cue at 0016: sprites hidden (nothing changes the bg), director spoke in nvl mode
    assert block[i_nvl + 1].startswith("c_director_nvl ")
    assert "nvl clear" in block[i_nvl:]
    # lyric voice lines in nvl are grouped into one page
    pages = [ln for ln in block if ln.startswith("c_poet_voice_nvl")]
    assert pages == ['c_poet_voice_nvl "Callan los pájaros;\\nla noche cae."']
    # cue 3: leave nvl, flash + shake, tint reset
    i_cue = block.index("# talk_0019")
    assert block[i_cue - 4 : i_cue] == [
        "nvl hide dissolve",
        "show bg theatre at tint_none",
        "with vn_flash",
        "show layer master at vn_shake",
    ]


def test_expression_mapping(script):
    block = scene_block(script, "talk")
    # first line of the first box is joyful -> director "pleased"
    assert "show director pleased at vn_left" in block
    # poet angry -> indignant (split box); director stays pleased/neutral as per his own lines
    assert "show poet indignant at vn_right" in block
    # poet melancholic -> neutral
    assert "show poet neutral at vn_right" in block


def test_stable_positions(script):
    block = scene_block(script, "talk")
    shows = [ln for ln in block if ln.startswith("show poet ")]
    assert shows and all(ln.endswith("at vn_right") for ln in shows)
    assert not any("vn_center" in ln for ln in block)  # annotated centre was never used


def test_sprite_false_never_shown(script):
    assert "show lord" not in script
    assert "show poet_voice" not in script
    assert "c_lord " in script  # still speaks, with name and colour


def test_characters_and_images(project):
    chars = (project / "game/characters.rpy").read_text(encoding="utf-8")
    assert 'define c_director = Character("El Director", who_color="#c9a25b")' in chars
    assert 'define c_director_nvl = Character("El Director", kind=nvl' in chars
    assert "define c_narrator = Character(None, what_color=" in chars
    assert "what_italic=True" in chars
    nameless_nvl = next(ln for ln in chars.split("\n") if ln.startswith("define c_poet_voice_nvl"))
    assert "None" in nameless_nvl and "nvl_thought" in nameless_nvl
    images = (project / "game/images.rpy").read_text(encoding="utf-8")
    assert 'image bg dedication = "images/bg/dedication.webp"' in images
    assert 'image director pleased = "images/sprites/director_pleased.webp"' in images
    assert (project / "game/images/sprites/poet_indignant.webp").is_file()
    assert (project / "game/images/bg/theatre.webp").is_file()
    assert not (project / "game/images/sprites/lord_neutral.webp").exists()


def test_options_substitution(project):
    options = (project / "game/options.rpy").read_text(encoding="utf-8")
    assert 'config.name = _("Mini")' in options
    assert 'build.name = "mini-vn"' in options
    assert "@@" not in options
    gui = (project / "game/gui.rpy").read_text(encoding="utf-8")
    assert 'gui.main_menu_background = "bg dedication"' in gui
    assert (project / "game/gui/textbox.png").is_file()
    assert (project / "game/fonts/RobotoSlab-Regular.ttf").is_file()


def test_music_only_when_audio_exists(work, annotated, tmp_path):
    out = tmp_path / "p"
    renpy_gen.generate(work, annotated, out)
    assert "play music" not in (out / "game/script.rpy").read_text(encoding="utf-8")
    (out / "game/audio").mkdir()
    (out / "game/audio/sacred.ogg").write_bytes(b"OggS")
    renpy_gen.generate(work, annotated, out)
    text = (out / "game/script.rpy").read_text(encoding="utf-8")
    assert 'play music "audio/sacred.ogg" fadeout 1.0 fadein 1.0' in text
    assert "stop music fadeout 1.0" in text  # mood "none" on the Lord's first line
    assert (out / "game/audio/sacred.ogg").is_file()  # regeneration keeps user audio


def test_unknown_cue_target_fails(work, annotated):
    broken = json.loads(json.dumps(annotated))
    broken["scenes"][1]["lines"] = broken["scenes"][1]["lines"][:5]
    with pytest.raises(ValueError, match="unknown line ids"):
        renpy_gen.render_script(work, broken, set())


def test_unknown_speaker_fails(work, annotated):
    broken = json.loads(json.dumps(annotated))
    broken["scenes"][1]["lines"][1]["ann"]["speaker"] = "ghost"
    with pytest.raises(ValueError, match="ghost"):
        renpy_gen.render_script(work, broken, set())


def tree(root: Path) -> dict[str, bytes]:
    return {
        str(p.relative_to(root)): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()
    }


def test_deterministic(work, annotated, tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    renpy_gen.generate(work, annotated, a)
    renpy_gen.generate(work, annotated, b)
    renpy_gen.generate(work, annotated, b)  # regenerating over an existing tree
    assert tree(a) == tree(b)


def test_from_parsed_annotations():
    work = load_work(ROOT / "works/faust")
    parsed = json.loads((ROOT / "works/faust/data/parsed.json").read_text(encoding="utf-8"))
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


@pytest.mark.skipif(not SDK.exists(), reason="Ren'Py SDK not installed in tools/renpy-sdk")
def test_renpy_lint(work, annotated, tmp_path):
    out = tmp_path / "mini"
    renpy_gen.generate(work, annotated, out)
    env = {**os.environ, "HOME": str(tmp_path / "home")}
    (tmp_path / "home").mkdir()
    result = subprocess.run(
        [str(SDK), str(out), "lint"], capture_output=True, text=True, env=env, timeout=300
    )
    report = result.stdout + result.stderr
    assert result.returncode == 0, report
    assert "Traceback" not in report and "error" not in report.lower(), report
