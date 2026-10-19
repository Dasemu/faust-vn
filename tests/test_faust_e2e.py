"""End-to-end playthrough of the generated Faust project (needs the Ren'Py SDK)."""

import json
import os
import subprocess
from pathlib import Path

import pytest
from vnpipe import renpy_gen
from vnpipe.config import load_work

ROOT = Path(__file__).resolve().parent.parent
SDK = Path(os.environ.get("RENPY_SDK") or ROOT / "tools/renpy-sdk") / "renpy.sh"


@pytest.mark.skipif(not SDK.exists(), reason="Ren'Py SDK not found (set RENPY_SDK)")
def test_e2e_playthrough_faust(tmp_path):
    work = load_work(ROOT)
    data = json.loads((ROOT / "data/annotated.json").read_text(encoding="utf-8"))
    out = tmp_path / "faust"
    renpy_gen.generate(work, data, out, with_test=True)
    home = tmp_path / "home"
    home.mkdir()
    env = {
        **os.environ,
        "HOME": str(home),
        "SDL_VIDEODRIVER": "dummy",
        "SDL_AUDIODRIVER": "dummy",
        "RENPY_RENDERER": "sw",
    }
    result = subprocess.run(
        [str(SDK), str(out), "test"], capture_output=True, text=True, env=env, timeout=900
    )
    report = result.stdout + result.stderr
    for name in ("traceback.txt", "errors.txt"):
        assert not (out / name).exists(), (out / name).read_text(encoding="utf-8")
    assert result.returncode == 0, report
    assert "Traceback" not in report and "FAIL" not in report, report
