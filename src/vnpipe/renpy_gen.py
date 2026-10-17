"""Ren'Py generator: annotated play + asset manifest -> a complete Ren'Py 8 project.

The output is deterministic (no timestamps, sorted iteration, copied bytes), so
re-running the command yields identical files. Staging rules are documented in
``docs/adaptation-rules.md``; work-specific choices come from ``work.toml``.

The GUI files in ``renpy_templates/`` were produced once with the Ren'Py SDK's
``generate_gui`` command and are MIT-licensed Ren'Py files (see ``docs/running.md``).
"""

import argparse
import hashlib
import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from vnpipe import PACKAGE_DIR
from vnpipe.assets import USABLE, load_manifest, placeholder
from vnpipe.config import Work, load_work
from vnpipe.schema import validate

TEMPLATE_DIR = PACKAGE_DIR / "renpy_templates"
USABLE_STATUS = USABLE | {"placeholder"}

ADV_MAX_LINES = 4
NVL_MAX_LINES = 8
SPLIT_INDENT = 6  # parsed `indent` at or above this marks a split verse line
TITLE_PAUSE = 2.0
END_PAUSE = 3.0

POSITIONS = ("left", "right", "center")  # order in which --from-parsed assigns positions
TRANSITIONS = {
    "dissolve": "dissolve",
    "fade": "fade",
    "slow": "vn_slow",
    "flash": "vn_flash",
}
TINTS = ("none", "dark", "red")
DEFAULT_LYRIC_VOICE = "poet_voice"
DEFAULT_END_TEXT = "Continuará…"
MENU_BG_FALLBACK = "gui/main_menu.png"

ABOUT_LABELS = {
    "es": ("Texto", "Traducción", "Adaptación a novela visual generada con vnpipe."),
    "en": ("Text", "Translation", "Visual novel adaptation generated with vnpipe."),
}


# --- text helpers -------------------------------------------------------------


def escape_text(text: str) -> str:
    """Escape a text for use inside a double-quoted Ren'Py say/define string."""
    return (
        text.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("[", "[[")
        .replace("{", "{{")
        .replace("\n", "\\n")
    )


def quote(text: str) -> str:
    return f'"{escape_text(text)}"'


def _plain_quote(text: str) -> str:
    """Quote a path or identifier-like string (no Ren'Py text markup)."""
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def char_var(cast_id: str, nvl: bool = False) -> str:
    """Ren'Py variable of a cast member's Character (prefixed: `director` etc. are built-ins)."""
    return f"c_{cast_id}" + ("_nvl" if nvl else "")


def bg_image_name(asset_id: str) -> str:
    """``bg_heaven_lord`` -> ``bg heaven_lord`` (tag ``bg``, attribute ``heaven_lord``)."""
    return "bg " + asset_id.removeprefix("bg_")


# --- annotations ----------------------------------------------------------------


def lyric_voice(work: Work) -> str:
    return work.data["work"].get("lyric_voice", DEFAULT_LYRIC_VOICE)


def annotations_from_parsed(work: Work, parsed: dict[str, Any]) -> dict[str, Any]:
    """Trivial in-memory annotations (used before the LLM annotations exist)."""
    voice = lyric_voice(work)
    scene_cfg = {s["id"]: s for s in work.scenes}
    digest = hashlib.sha256(
        json.dumps(parsed, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    scenes = []
    for scene in parsed["scenes"]:
        cfg = scene_cfg.get(scene["id"], {})
        spoken: list[str] = []
        positions: dict[str, str] = {}
        lines = []
        for line in scene["lines"]:
            speaker = line["speaker"]
            if line["kind"] == "direction":
                ann_speaker, kind = "narrator", "stage_direction"
            elif speaker:
                ann_speaker, kind = speaker, "dialogue"
            else:
                ann_speaker, kind = voice, "narration"
            if line["kind"] == "verse" and speaker and work.cast.get(speaker, {}).get("sprite"):
                if speaker not in positions:
                    positions[speaker] = POSITIONS[len(positions) % len(POSITIONS)]
                if speaker not in spoken:
                    spoken.append(speaker)
            lines.append(
                {
                    **line,
                    "ann": {
                        "speaker": ann_speaker,
                        "kind": kind,
                        "emotion": "neutral",
                        "location": cfg.get("location", "unknown"),
                        "time_of_day": cfg.get("time_of_day", "timeless"),
                        "on_stage": [{"character": c, "position": positions[c]} for c in spoken],
                    },
                }
            )
        scenes.append({"id": scene["id"], "heading": scene["heading"], "lines": lines})
    return {
        "work": parsed["work"],
        "parsed_sha256": digest,
        "fallback_chunks": [],
        "scenes": scenes,
    }


# --- assets -----------------------------------------------------------------------


@dataclass
class ImageEntry:
    name: str  # Ren'Py image name, e.g. "bg heaven" or "faust neutral"
    rel: str  # path below game/images/
    asset: dict[str, Any]
    source: Path | None  # file to copy, or None to generate a placeholder


def _sprite_asset(character: str, expression: str) -> dict[str, Any]:
    return {
        "id": f"sprite_{character}_{expression}",
        "kind": "sprite",
        "character": character,
        "expression": expression,
        "file": f"sprites/{character}_{expression}.webp",
    }


def _bg_asset(asset_id: str) -> dict[str, Any]:
    return {
        "id": asset_id,
        "kind": "background",
        "file": f"bg/{asset_id.removeprefix('bg_')}.webp",
    }


def _needed_bg_ids(work: Work) -> list[str]:
    ids = [cfg["bg"] for cfg in work.data.get("staging", {}).values() if cfg.get("bg")]
    ids += [cue["bg"] for cue in work.data.get("cues", []) if cue.get("bg")]
    return ids


def collect_images(work: Work, manifest: dict[str, Any] | None) -> list[ImageEntry]:
    """Every image the project declares: manifest assets plus anything the staging needs."""
    assets: dict[str, dict[str, Any]] = {}
    for asset in (manifest or {}).get("assets", []):
        assets[asset["id"]] = asset
    for asset_id in _needed_bg_ids(work):
        assets.setdefault(asset_id, _bg_asset(asset_id))
    for cid, info in work.cast.items():
        if not info.get("sprite"):
            continue
        for expression in sorted(set(info.get("expressions", {}).values())):
            sprite = _sprite_asset(cid, expression)
            assets.setdefault(sprite["id"], sprite)
    entries = []
    for asset_id in sorted(assets):
        asset = assets[asset_id]
        if asset["kind"] == "background":
            name = bg_image_name(asset_id)
        else:
            name = f"{asset['character']} {asset['expression']}"
        source = None
        if asset.get("status") in USABLE_STATUS and asset.get("file"):
            candidate = work.path("assets") / asset["file"]
            if candidate.is_file():
                source = candidate
        entries.append(ImageEntry(name, asset["file"], asset, source))
    return entries


# --- script generation ----------------------------------------------------------------


@dataclass
class Box:
    lines: list[dict[str, Any]] = field(default_factory=list)
    key: tuple | None = None
    speaker: str = ""
    is_direction: bool = False


def _is_direction(line: dict[str, Any]) -> bool:
    return line["kind"] == "direction" or line["ann"]["kind"] == "stage_direction"


class SceneWriter:
    """Turns one scene's lines into Ren'Py statements, tracking staging state."""

    def __init__(
        self, work: Work, scene: dict[str, Any], moods: set[str], music_state: dict[str, str | None]
    ):
        self.work = work
        self.scene = scene
        self.moods = moods
        self.voice = lyric_voice(work)
        self.cues = {c["at"]: c for c in work.data.get("cues", [])}
        staging = work.data.get("staging", {}).get(scene["id"], {})
        self.mode: str = staging.get("mode", "adv")
        self.bg: str | None = staging.get("bg")
        self.tint = "none"
        self.music_state = music_state  # {'playing': mood}, shared across scenes
        self.shown: dict[str, str] = {}  # character -> expression currently shown
        self.positions: dict[str, str] = {}  # character -> stable position for this scene
        self.out: list[str] = []
        self.box: Box | None = None

    def emit(self, text: str = "") -> None:
        self.out.append(("    " + text) if text else "")

    # -- speakers ---------------------------------------------------------------

    def speaker_of(self, line: dict[str, Any]) -> str:
        if _is_direction(line):
            return "narrator"
        speaker = line["ann"]["speaker"] or self.voice
        if speaker != "narrator" and speaker not in self.work.cast:
            raise ValueError(f"{line['id']}: speaker {speaker!r} is not in [cast]")
        return speaker

    # -- cues ----------------------------------------------------------------------

    def apply_cue(self, cue: dict[str, Any]) -> None:
        changes = False
        new_mode = cue.get("mode", self.mode)
        if self.mode == "nvl" and new_mode != "nvl":
            self.emit("nvl hide dissolve")
        if new_mode == "nvl" or cue.get("hide_all"):
            changes |= self.hide_sprites(list(self.shown))
        self.mode = new_mode
        if cue.get("tint") is not None:
            if cue["tint"] not in TINTS:
                raise ValueError(f"cue at {cue['at']}: unknown tint {cue['tint']!r}")
            self.tint = cue["tint"]
        if cue.get("bg") or cue.get("tint") is not None:
            self.bg = cue.get("bg") or self.bg
            self.emit(f"show {bg_image_name(self.bg)} at tint_{self.tint}")
            changes = True
        if changes:
            transition = cue.get("transition", "dissolve")
            if transition not in TRANSITIONS:
                raise ValueError(f"cue at {cue['at']}: unknown transition {transition!r}")
            self.emit(f"with {TRANSITIONS[transition]}")
        if cue.get("shake"):
            self.emit("show layer master at vn_shake")

    def hide_sprites(self, characters: list[str]) -> bool:
        for cid in characters:
            self.emit(f"hide {cid}")
            del self.shown[cid]
        return bool(characters)

    # -- boxes ----------------------------------------------------------------------

    def limit(self) -> int:
        return NVL_MAX_LINES if self.mode == "nvl" else ADV_MAX_LINES

    def feed(self, line: dict[str, Any]) -> None:
        if line["kind"] == "cast":
            return
        cue = self.cues.get(line["id"])
        if cue:
            self.flush()
            self.apply_cue(cue)
        direction = _is_direction(line)
        key = (self.speaker_of(line), line["speech"], line["stanza"])
        split = self.mode == "adv" and not direction and line["indent"] >= SPLIT_INDENT
        box = self.box
        if box and (
            direction
            or box.is_direction
            or key != box.key
            or len(box.lines) >= self.limit()
            or split
            or (self.mode == "adv" and box.lines[-1]["indent"] >= SPLIT_INDENT)
        ):
            self.flush()
        if self.box is None:
            self.box = Box(key=key, speaker=key[0], is_direction=direction)
        self.box.lines.append(line)

    def flush(self) -> None:
        box = self.box
        if not box:
            return
        self.box = None
        first, last = box.lines[0], box.lines[-1]
        ids = first["id"] if first is last else f"{first['id']} .. {last['id']}"
        self.emit(f"# {ids}")
        self.music(first["ann"].get("music"))
        if self.mode == "adv":
            self.stage(box)
        text = "\\n".join(escape_text(line["text"]) for line in box.lines)
        variable = char_var(box.speaker, nvl=self.mode == "nvl")
        self.emit(f'{variable} "{text}"')
        if self.mode == "nvl":
            self.emit("nvl clear")

    def music(self, mood: str | None) -> None:
        if mood is None:
            return
        if mood == "none":
            if self.music_state["playing"]:
                self.emit("stop music fadeout 1.0")
                self.music_state["playing"] = None
        elif mood in self.moods and self.music_state["playing"] != mood:
            self.emit(f'play music "audio/{mood}.ogg" fadeout 1.0 fadein 1.0')
            self.music_state["playing"] = mood

    # -- sprites ---------------------------------------------------------------------

    def stage(self, box: Box) -> None:
        first = box.lines[0]
        ann = first["ann"]
        desired: list[str] = []
        for entry in ann["on_stage"]:
            cid = entry["character"]
            if cid not in self.work.cast:
                raise ValueError(f"{first['id']}: on_stage character {cid!r} is not in [cast]")
            if not self.work.cast[cid].get("sprite"):
                continue
            self.positions.setdefault(cid, entry["position"])
            desired.append(cid)
        changed = self.hide_sprites([c for c in list(self.shown) if c not in desired])
        for cid in desired:
            expressions = self.work.cast[cid].get("expressions", {})
            neutral = expressions.get("neutral", "neutral")
            if cid == box.speaker:
                expression = expressions.get(ann["emotion"], neutral)
            else:
                expression = self.shown.get(cid, neutral)
            if self.shown.get(cid) != expression:
                self.emit(f"show {cid} {expression} at vn_{self.positions[cid]}")
                self.shown[cid] = expression
                changed = True
        if changed:
            self.emit("with dissolve")

    # -- scene ---------------------------------------------------------------------------

    def render(self) -> list[str]:
        scene = self.scene
        self.out.append(f"label scene_{scene['id']}:")
        self.emit("scene black")
        self.emit(
            f'show text "{{size=60}}{escape_text(scene["heading"])}{{/size}}" '
            "as title_card at truecenter"
        )
        self.emit("with fade")
        self.emit(f"pause {TITLE_PAUSE}")
        self.emit("hide title_card")
        if self.bg:
            self.emit(f"scene {bg_image_name(self.bg)} at tint_{self.tint}")
        self.emit("with fade")
        for line in scene["lines"]:
            self.feed(line)
        self.flush()
        if self.mode == "nvl":
            self.emit("nvl hide dissolve")
        self.out.append("")
        return self.out


def render_script(work: Work, annotated: dict[str, Any], moods: set[str]) -> str:
    end_text = work.data["work"].get("end_text", DEFAULT_END_TEXT)
    out = [
        "## Generated by `vnpipe renpy`. Do not edit: regenerate instead.",
        "",
        "label start:",
        "    window auto",
        "",
    ]
    known = {c["at"] for c in work.data.get("cues", [])}
    seen: set[str] = set()
    music_state: dict[str, str | None] = {"playing": None}
    for scene in annotated["scenes"]:
        out.extend(SceneWriter(work, scene, moods, music_state).render())
        seen |= {line["id"] for line in scene["lines"]}
    missing = known - seen
    if missing:
        raise ValueError(f"cues refer to unknown line ids: {sorted(missing)}")
    out += [
        "    scene black",
        "    with fade",
        f'    show text "{{size=60}}{escape_text(end_text)}{{/size}}" as title_card at truecenter',
        "    with dissolve",
        f"    pause {END_PAUSE}",
        "    return",
        "",
    ]
    return "\n".join(out)


# --- static project files -----------------------------------------------------------------


def render_characters(work: Work) -> str:
    cast = dict(work.cast)
    cast.setdefault("narrator", {"name": "", "color": "#d8cfc0"})
    out = ["## Generated by `vnpipe renpy`. Do not edit: regenerate instead.", ""]
    for cid, info in cast.items():
        name = info.get("name") or ""
        color = info.get("color")
        who = quote(name) if name else "None"
        props: list[str] = []
        if name and color:
            props.append(f"who_color={_plain_quote(color)}")
        if not name and color:
            props.append(f"what_color={_plain_quote(color)}")
        if cid == "narrator":
            props.append("what_italic=True")
        adv = ", ".join([who, *props])
        nvl_props = ["kind=nvl", *props]
        if not name:
            nvl_props.append('what_style="nvl_thought"')
        out.append(f"define {char_var(cid)} = Character({adv})")
        out.append(f"define {char_var(cid, nvl=True)} = Character({', '.join([who, *nvl_props])})")
    out.append("")
    return "\n".join(out)


def render_images(entries: list[ImageEntry]) -> str:
    out = ["## Generated by `vnpipe renpy`. Do not edit: regenerate instead.", ""]
    for e in entries:
        out.append(f"image {e.name} = {_plain_quote('images/' + e.rel)}")
    out.append("")
    return "\n".join(out)


def _about(work: Work) -> str:
    info = work.data["work"]
    text_l, trans_l, tail = ABOUT_LABELS.get(info.get("language", "es"), ABOUT_LABELS["en"])
    parts = [info.get("subtitle", "")]
    if info.get("author"):
        parts.append(f"{text_l}: {info['author']}")
    if info.get("translator"):
        parts.append(f"{trans_l}: {info['translator']}")
    parts.append(tail)
    return "\\n\\n".join(escape_text(p) for p in parts if p)


def _substitute(text: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        text = text.replace(f"@@{key}@@", value)
    if "@@" in text:
        raise ValueError("unreplaced template token")
    return text


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _audio_moods(out: Path) -> set[str]:
    audio = out / "game" / "audio"
    return {p.stem for p in audio.glob("*.ogg")} if audio.is_dir() else set()


def generate(work: Work, annotated: dict[str, Any], out: Path) -> list[Path]:
    """Write the Ren'Py project into ``out``; returns every generated file (sorted)."""
    info = work.data["work"]
    manifest_path = work.path("assets/assets.json")
    manifest = load_manifest(work.root) if manifest_path.is_file() else None
    entries = collect_images(work, manifest)
    game = out / "game"
    for sub in ("images", "gui", "fonts"):
        shutil.rmtree(game / sub, ignore_errors=True)
    game.mkdir(parents=True, exist_ok=True)

    # GUI template: copy binaries, substitute tokens in .rpy files.
    menu_bg = MENU_BG_FALLBACK
    staging = work.data.get("staging", {})
    first_bg = info.get("menu_bg") or next((c["bg"] for c in staging.values() if c.get("bg")), None)
    if first_bg:
        menu_bg = bg_image_name(first_bg)
    values = {
        "TITLE": escape_text(info["title"]),
        "VERSION": "0.1",
        "ABOUT": _about(work),
        "BUILD_NAME": f"{info['id']}-vn",
        "SAVE_DIR": f"{info['id']}-vn",
        "MENU_BG": menu_bg,
    }
    written: list[Path] = []
    for src in sorted((TEMPLATE_DIR / "game").rglob("*")):
        if not src.is_file():
            continue
        dest = game / src.relative_to(TEMPLATE_DIR / "game")
        dest.parent.mkdir(parents=True, exist_ok=True)
        written.append(dest)
        if src.suffix == ".rpy":
            write_text(dest, _substitute(src.read_text(encoding="utf-8"), values))
        else:
            shutil.copyfile(src, dest)

    for name, text in (
        ("characters.rpy", render_characters(work)),
        ("images.rpy", render_images(entries)),
        ("script.rpy", render_script(work, annotated, _audio_moods(out))),
    ):
        write_text(game / name, text)
        written.append(game / name)

    for e in entries:
        dest = game / "images" / e.rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        written.append(dest)
        if e.source:
            shutil.copyfile(e.source, dest)
        else:
            placeholder(e.asset).save(dest, "WEBP", quality=90)

    return sorted(written)


# --- CLI ----------------------------------------------------------------------------------


def cmd_renpy(args: argparse.Namespace) -> int:
    work = load_work(args.work)
    if args.from_parsed:
        parsed = json.loads(work.path("data/parsed.json").read_text(encoding="utf-8"))
        validate(parsed, "parsed")
        annotated = annotations_from_parsed(work, parsed)
    else:
        path = work.path("data/annotated.json")
        if not path.is_file():
            raise SystemExit(f"renpy: {path} missing; run annotation or pass --from-parsed")
        annotated = json.loads(path.read_text(encoding="utf-8"))
    validate(annotated, "annotated")
    out = args.out or Path("vn") / work.id
    files = generate(work, annotated, out)
    print(f"renpy: wrote {len(files)} files under {out}")
    return 0


def register(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("renpy", help="Generate the Ren'Py project")
    parser.add_argument(
        "--from-parsed",
        action="store_true",
        help="Build trivial annotations from parsed.json instead of reading annotated.json",
    )
    parser.add_argument("--out", type=Path, help="Output directory (default: vn/<work id>)")
    parser.set_defaults(handler=cmd_renpy)
