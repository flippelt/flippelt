#!/usr/bin/env python3
"""Generate assets/boot.svg. Human version is age/10 from scripts/human.json."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HUMAN_JSON = Path(__file__).resolve().parent / "human.json"
OUT = ROOT / "assets" / "boot.svg"

W = 860
N_HASH = 16
BAR_X = 408
PCT_X = 560
MSG_X = 48
ICON_X = 26
CHECK_X = 24


def _last_anniversary(today: date, month: int, day: int) -> date:
    this_year = date(today.year, month, day)
    if today >= this_year:
        return this_year
    return date(today.year - 1, month, day)


def _months_since(start: date, end: date) -> int:
    months = (end.year - start.year) * 12 + (end.month - start.month)
    if end.day < start.day:
        months -= 1
    return months


def _semver(major: int, minor: int, patch: int) -> str:
    major += minor // 10
    minor %= 10
    return f"{major}.{minor}.{patch}"


def human_version(today: date | None = None) -> str:
    cfg = json.loads(HUMAN_JSON.read_text())
    fallback = cfg.get("fallback_version", "3.7.0")
    raw = (cfg.get("birthday") or "").strip()
    if not raw:
        return fallback
    today = today or date.today()
    y, m, d = (int(p) for p in raw.split("-"))
    born = date(y, m, d)
    last = _last_anniversary(today, born.month, born.day)
    years = last.year - born.year
    months = _months_since(last, today)
    return _semver(years // 10, years % 10, months)


def daughter_version(today: date | None = None) -> str:
    cfg = json.loads(HUMAN_JSON.read_text())
    daughter = cfg.get("daughter") or {}
    base = daughter.get("version", "1.3.0")
    month = int(daughter.get("month", 10))
    day = int(daughter.get("day", 25))
    as_of_year = int(daughter.get("as_of_year", 2025))
    today = today or date.today()
    last = _last_anniversary(today, month, day)
    major, minor, _patch = (int(p) for p in base.split("."))
    minor += last.year - as_of_year
    months = _months_since(last, today)
    return _semver(major, minor, months)


def hashes_for(row: dict) -> list[float]:
    t0, t1, n = row["t0"], row["t1"], N_HASH
    if row.get("adhd"):
        span = t1 - t0
        rel = [
            0.04, 0.07, 0.10, 0.13,
            0.38, 0.40, 0.42, 0.45, 0.48,
            0.70, 0.72, 0.75,
            0.88, 0.92, 0.96, 1.00,
        ]
        return [t0 + span * r for r in rel]
    stall = row.get("stall")
    if stall:
        t_stall, pct_stall, t_resume = stall
        n_stall = round(n * pct_stall / 100)
        dt1 = (t_stall - t0) / max(n_stall, 1)
        out = [t0 + dt1 * (i + 1) for i in range(n_stall)]
        rest = n - n_stall
        dt2 = (t1 - t_resume) / max(rest, 1)
        out += [t_resume + dt2 * (i + 1) for i in range(rest)]
        return out
    dt = (t1 - t0) / n
    delays = [t0 + dt * (i + 1) for i in range(n)]
    if row.get("reverse"):
        return list(reversed(delays))
    return delays


def pct_steps(row: dict) -> list[tuple[float, float | None, str]]:
    t0, t1 = row["t0"], row["t1"]
    if row.get("adhd"):
        span = t1 - t0
        return [
            (t0 + span * 0.13, t0 + span * 0.38, " 25%"),
            (t0 + span * 0.38, t0 + span * 0.70, " 56%"),
            (t0 + span * 0.70, t0 + span * 0.88, " 75%"),
            (t0 + span * 0.88, None, "100%"),
        ]
    stall = row.get("stall")
    if stall:
        t_stall, _pct, t_resume = stall
        return [
            (t0 + 0.12, t0 + (t_stall - t0) * 0.35, "  8%"),
            (t0 + (t_stall - t0) * 0.35, t0 + (t_stall - t0) * 0.65, " 31%"),
            (t0 + (t_stall - t0) * 0.65, t_stall, " 58%"),
            (t_stall, t_resume, " 87%"),
            (t_resume, None, "100%"),
        ]
    pts = [8, 27, 49, 73, 91, 100]
    times = [t0 + (t1 - t0) * (p / 100) for p in pts]
    steps = []
    for i, p in enumerate(pts):
        hide = times[i + 1] if i + 1 < len(times) else None
        steps.append((times[i], hide, f"{p:3d}%"))
    return steps


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build() -> str:
    version = human_version()
    kid = daughter_version()

    y_whoami, y_user = 72, 96
    y_boot, y_post, y_mount = 144, 168, 192
    y_stack, y_rpg, y_ready = 216, 240, 264
    y_brew1, y_brew2, y_upd = 308, 330, 356
    y_json, y_fetch1, y_fetch2 = 380, 406, 428
    bottle_y0, bottle_dy = 454, 22

    packages = [
        dict(id="rpg",     label="Bottle rpg (0.5.0)",                      t0=4.35, t1=5.35, stall=None, reverse=False, adhd=False, note="# How do you want to do this?"),
        dict(id="human",   label=f"Bottle human ({version})",               t0=4.35, t1=8.15, stall=(6.50, 87, 7.85), reverse=False, adhd=False, note="# finally stable"),
        dict(id="humor",   label="Bottle humor (3.2.1)",                    t0=4.35, t1=6.10, stall=None, reverse=False, adhd=False, note="--with-piadas"),
        dict(id="sarcasm", label="Bottle sarcasm (4.2.0)",                  t0=4.35, t1=6.45, stall=None, reverse=False, adhd=False, note="--as-defense-mechanism"),
        dict(id="brain",   label="Bottle brain (1.0.0)",                    t0=4.35, t1=6.90, stall=None, reverse=False, adhd=False, note="--with-hiperfocus"),
        dict(id="creativity", label="Bottle creativity (0.9.0)",             t0=4.35, t1=5.90, stall=None, reverse=False, adhd=False, note="--unbounded"),
        dict(id="daughter", label=f"Bottle daughter ({kid})",               t0=4.35, t1=6.20, stall=None, reverse=False, adhd=False, note="# unplanned feature"),
        dict(id="adhd",    label="Bottle adhd (0.4.1)",                     t0=4.35, t1=5.15, stall=None, reverse=False, adhd=True,  note=None, ribbon=True),
        dict(id="totb",    label="Bottle thinking-outside-the-box (0.1.0)", t0=4.35, t1=7.35, stall=None, reverse=True,  adhd=False, note="# poured sideways"),
        dict(id="goblin",  label="Bottle dice-goblin (13.0.0)",             t0=4.35, t1=6.65, stall=None, reverse=False, adhd=False, note="# shiny math rocks", d20=True),
    ]
    for i, p in enumerate(packages):
        p["y"] = bottle_y0 + i * bottle_dy

    y_sum = bottle_y0 + len(packages) * bottle_dy + 16
    y_keg = y_sum + 22
    y_cat = y_keg + 40
    y_const = y_cat + 24
    y_pronouns = y_const + 24
    y_role = y_pronouns + 24
    y_location = y_role + 24
    y_langs = y_location + 24
    y_code = y_langs + 24
    y_tools = y_code + 24
    y_focus = y_tools + 24
    y_learning = y_focus + 24
    y_end = y_learning + 24
    cursor_y = y_end + 16
    h = cursor_y + 18

    json_row = dict(
        id="json", y=y_json, label="JSON API formula.jws.json",
        t0=3.45, t1=3.95, stall=None, reverse=False, adhd=False, note=None,
    )
    rows = [json_row] + packages

    css = [
        "    .term { font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace; font-size: 14px; }",
        "    .prompt { fill: #3fb950; }",
        "    .cmd    { fill: #c9d1d9; }",
        "    .user   { fill: #58a6ff; }",
        "    .ok     { fill: #3fb950; }",
        "    .mid    { fill: #8b949e; }",
        "    .val    { fill: #58a6ff; }",
        "    .ready  { fill: #f0b429; }",
        "    .kw     { fill: #ff7b72; }",
        "    .var    { fill: #c9d1d9; }",
        "    .type   { fill: #ffa657; }",
        "    .key    { fill: #79c0ff; }",
        "    .str    { fill: #a5d6ff; }",
        "    .punc   { fill: #8b949e; }",
        "    .eq     { fill: #3fb950; }",
        "    .track  { fill: #484f58; }",
        "    .hash   { fill: #3fb950; }",
        "    .pct    { fill: #8b949e; }",
        "    .pct-end{ fill: #3fb950; }",
        "    .note   { fill: #6e7681; }",
        "    .beer   { fill: #c9d1d9; }",
        "    .spin-g { opacity: 0; }",
        "    .check  { opacity: 1; }",
        "    .bar    { opacity: 0; }",
        "    .ln     { opacity: 1; }",
        "    .sf     { fill: #58a6ff; opacity: 0; }",
        "    .s0 { animation: sp0 .48s steps(1) infinite; }",
        "    .s1 { animation: sp1 .48s steps(1) infinite; }",
        "    .s2 { animation: sp2 .48s steps(1) infinite; }",
        "    .s3 { animation: sp3 .48s steps(1) infinite; }",
        "    @keyframes appear { from { opacity: 0 } to { opacity: 1 } }",
        "    @keyframes vanish { to { opacity: 0 } }",
        "    @keyframes blink  { 50% { opacity: 0 } }",
        "    @keyframes sp0 { 0%,24% { opacity: 1 } 25%,100% { opacity: 0 } }",
        "    @keyframes sp1 { 0%,24% { opacity: 0 } 25%,49% { opacity: 1 } 50%,100% { opacity: 0 } }",
        "    @keyframes sp2 { 0%,49% { opacity: 0 } 50%,74% { opacity: 1 } 75%,100% { opacity: 0 } }",
        "    @keyframes sp3 { 0%,74% { opacity: 0 } 75%,100% { opacity: 1 } }",
        "    .cursor { fill: #c9d1d9; opacity: 1; animation: appear .1s linear 11.75s both, blink 1.05s step-end 11.85s infinite; }",
        "",
    ]

    line_delays = [
        ("ln-whoami", 0.15), ("ln-user", 0.50), ("ln-boot", 1.00),
        ("ln-post", 1.30), ("ln-mount", 1.60), ("ln-stack", 1.90),
        ("ln-engines", 2.20), ("ln-ready", 2.50),
        ("ln-brew1", 2.90), ("ln-brew2", 3.05), ("ln-upd", 3.25),
        ("ln-json", 3.45), ("ln-fetch1", 4.10), ("ln-fetch2", 4.20),
        ("ln-rpg", 4.35), ("ln-human", 4.35), ("ln-humor", 4.35),
        ("ln-sarcasm", 4.35), ("ln-brain", 4.35), ("ln-creativity", 4.35),
        ("ln-daughter", 4.35), ("ln-adhd", 4.35),
        ("ln-totb", 4.35), ("ln-goblin", 4.35),
        ("ln-sum", 8.40), ("ln-keg", 8.60),
        ("ln-cat", 9.00), ("ln-const", 9.30), ("ln-pronouns", 9.55),
        ("ln-role", 9.80), ("ln-location", 10.05), ("ln-langs", 10.30),
        ("ln-code", 10.55), ("ln-tools", 10.80), ("ln-focus", 11.05),
        ("ln-learning", 11.30), ("ln-end", 11.55),
    ]
    for cls, delay in line_delays:
        css.append(f"    .{cls} {{ animation: appear .15s ease {delay:.2f}s both; }}")

    for row in rows:
        i, t0, t1 = row["id"], row["t0"], row["t1"]
        css.append(
            f"    .spin-{i} {{ animation: appear 0s linear {t0:.2f}s both, vanish 0s linear {t1:.2f}s forwards; }}"
        )
        css.append(f"    .check-{i} {{ animation: appear .18s ease {t1:.2f}s both; }}")
        css.append(
            f"    .bar-{i} {{ animation: appear 0s linear {t0:.2f}s both, vanish .18s ease {t1:.2f}s forwards; }}"
        )
        if row.get("note") or row.get("ribbon"):
            css.append(f"    .note-{i} {{ animation: appear .25s ease {t1 + 0.05:.2f}s both; }}")

    css.append("")
    css.append("    @media (prefers-reduced-motion: reduce) {")
    css.append("      .ln, .spin-g, .check, .bar, .note, .cursor, .sf, .h, .pstep { animation: none !important; }")
    css.append("      .spin-g, .bar { opacity: 0 !important; }")
    css.append("      .check, .ln, .note { opacity: 1 !important; }")
    css.append("      .cursor { opacity: 1 !important; }")
    css.append("    }")

    def spinner(row_id: str, y: int) -> str:
        frames = [("s0", "⠋"), ("s1", "⠙"), ("s2", "⠹"), ("s3", "⠸")]
        inner = "\n".join(
            f'        <text x="{ICON_X}" y="{y}" class="term sf {cls}">{ch}</text>'
            for cls, ch in frames
        )
        return f'      <g class="spin-g spin-{row_id}">\n{inner}\n      </g>'

    def check(row_id: str, y: int) -> str:
        cy = y - 11
        return (
            f'      <g class="check check-{row_id}" transform="translate({CHECK_X} {cy})">\n'
            f'        <circle cx="7" cy="7" r="7" fill="#3fb950"/>\n'
            f'        <path d="M3.8 7.2 6 9.4 11.2 4.2" fill="none" stroke="#0d1117" '
            f'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>\n'
            f'      </g>'
        )

    def bar(row: dict) -> str:
        i, y = row["id"], row["y"]
        tspans = "".join(
            f'<tspan class="h" style="opacity:0;animation:appear .01s linear {d:.2f}s both">#</tspan>'
            for d in hashes_for(row)
        )
        pcts = []
        for ts, th, lab in pct_steps(row):
            end = " pct-end" if lab.strip() == "100%" else ""
            if th is None:
                anim = f"appear 0s linear {ts:.2f}s both"
            else:
                anim = f"appear 0s linear {ts:.2f}s both, vanish 0s linear {th:.2f}s forwards"
            pcts.append(
                f'        <text x="{PCT_X}" y="{y}" class="term pct{end} pstep" '
                f'style="opacity:0;animation:{anim}">{lab}</text>'
            )
        return (
            f'      <g class="bar bar-{i}">\n'
            f'        <text x="{BAR_X}" y="{y}" class="term track">{"-" * N_HASH}</text>\n'
            f'        <text x="{BAR_X}" y="{y}" class="term hash">{tspans}</text>\n'
            + "\n".join(pcts) + "\n"
            f'      </g>'
        )

    def orange_ribbon(row_id: str, x: int, y: int) -> str:
        # ADHD awareness ribbon (laço laranja) — first loop shape, not the long-tail one.
        top = y - 12
        return (
            f'      <g class="note note-{row_id}" transform="translate({x} {top})">\n'
            f'        <path fill="#F58220" d="M7 1.1c-2.5 0-4.3 1.9-4.3 4.3 0 1.8.9 3.3 2.7 5.1L3.1 15h2.4l1.5-3.5L8.5 15H11l-2.3-4.5c1.8-1.8 2.7-3.3 2.7-5.1 0-2.4-1.8-4.3-4.4-4.3zm0 1.8c1.3 0 2.4 1 2.4 2.5 0 1.3-.8 2.5-2.4 4.2-1.6-1.7-2.4-2.9-2.4-4.2 0-1.5 1.1-2.5 2.4-2.5z"/>\n'
            f'      </g>\n'
        )

    def d20_icon(kind: str = "a") -> str:
        # Orthographic icosahedron (16x20), no face number. A regular hex of
        # 6 triangles reads as an isometric cube at this size; these are
        # real 20-face projections. Fills on the polygons so .note { fill }
        # on the parent does not grey them out.
        faces_a = (
            "14.23,14.47 8.35,9.73 5.67,17.07",
            "14.23,14.47 14.39,5.53 8.35,9.73",
            "1.61,14.47 5.67,17.07 0.55,9.73",
            "5.94,2.60 1.77,5.53 0.55,9.73",
            "10.33,2.93 5.94,2.60 14.39,5.53",
            "10.06,17.40 1.61,14.47 5.67,17.07",
            "10.33,2.93 5.94,2.60 1.77,5.53",
            "10.33,2.93 15.45,10.27 14.39,5.53",
            "7.65,10.27 1.77,5.53 1.61,14.47",
            "7.65,10.27 10.33,2.93 1.77,5.53",
        )
        fills_a = (
            "#f65249", "#ce413b", "#9d2b2a", "#791c1d", "#791c1d",
            "#791c1d", "#f45148", "#9d2b2a", "#ce413b", "#f65249",
        )
        faces_b = (
            "11.47,15.35 14.30,7.23 6.59,8.82",
            "11.47,15.35 6.59,8.82 2.97,15.35",
            "13.03,4.65 7.55,2.21 14.30,7.23",
            "1.70,12.77 2.97,15.35 0.55,7.23",
            "15.45,12.77 11.47,15.35 8.45,17.79",
            "13.03,4.65 15.45,12.77 14.30,7.23",
            "8.45,17.79 1.70,12.77 2.97,15.35",
            "13.03,4.65 7.55,2.21 4.53,4.65",
            "9.41,11.18 13.03,4.65 4.53,4.65",
            "9.41,11.18 4.53,4.65 1.70,12.77",
        )
        fills_b = (
            "#d7443e", "#e24942", "#791c1d", "#791c1d", "#e84c44",
            "#791c1d", "#791c1d", "#ed4e46", "#e24942", "#d7443e",
        )
        faces, fills = (faces_a, fills_a) if kind == "a" else (faces_b, fills_b)
        polys = "".join(
            f'<polygon fill="{fill}" stroke="#2a0709" stroke-width="0.5" '
            f'stroke-linejoin="round" points="{pts}"/>'
            for fill, pts in zip(fills, faces)
        )
        return polys

    def flanked_note(row: dict) -> str:
        # One d20 on each end of the note: [die] # shiny math rocks [die]
        text = row["note"]
        y = row["y"]
        rid = row["id"]
        die_w, gap = 16, 5
        top = y - 16
        text_x = BAR_X + die_w + gap
        right_x = text_x + round(len(text) * 8.4) + gap
        return (
            f'      <g class="note note-{rid}" transform="translate({BAR_X} {top})">'
            f"{d20_icon('a')}</g>\n"
            f'      <text x="{text_x}" y="{y}" class="term note note-{rid}">{esc(text)}</text>\n'
            f'      <g class="note note-{rid}" transform="translate({right_x} {top})">'
            f"{d20_icon('b')}</g>\n"
        )

    def note(row: dict) -> str:
        if row.get("ribbon"):
            return orange_ribbon(row["id"], BAR_X, row["y"])
        if not row.get("note"):
            return ""
        if row.get("d20"):
            return flanked_note(row)
        return (
            f'      <text x="{BAR_X}" y="{row["y"]}" class="term note note-{row["id"]}">'
            f'{esc(row["note"])}</text>\n'
        )

    def row_group(row: dict, ln_class: str) -> str:
        body = [
            f'    <g class="ln {ln_class}">',
            spinner(row["id"], row["y"]),
            check(row["id"], row["y"]),
            f'      <text x="{MSG_X}" y="{row["y"]}" class="cmd">{esc(row["label"])}</text>',
            bar(row),
        ]
        n = note(row)
        if n:
            body.append(n.rstrip("\n"))
        body.append("    </g>")
        return "\n".join(body)

    aria = (
        "Terminal: $ whoami and ./boot.sh; then $ brew install rpg "
        "human humor sarcasm brain creativity daughter adhd thinking-outside-the-box dice-goblin "
        "with # progress bars, percents and green checks; then $ cat felipe.ts "
        "prints const felipe_lippelt: Dev = { pronouns, role, location, langs, code, tools, focus, learning }"
    )

    bottle_rows = "\n".join(row_group(p, f"ln-{p['id']}") for p in packages)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" role="img" aria-label="{esc(aria)}">
  <defs>
    <style>
{chr(10).join(css)}
    </style>
  </defs>

  <rect x="1" y="1" width="{W-2}" height="{h-2}" rx="10" fill="#0d1117" stroke="#30363d" stroke-width="1.5"/>
  <line x1="1" y1="40" x2="{W-1}" y2="40" stroke="#30363d" stroke-width="1"/>
  <circle cx="24" cy="20.5" r="6" fill="#ff5f56"/>
  <circle cx="44" cy="20.5" r="6" fill="#ffbd2e"/>
  <circle cx="64" cy="20.5" r="6" fill="#27c93f"/>
  <text x="{W//2}" y="25" text-anchor="middle" class="term" fill="#6e7681" font-size="13">felipe@github ~ /profile</text>

  <g class="term" xml:space="preserve">
    <text x="24" y="{y_whoami}" class="ln ln-whoami"><tspan class="prompt">$ </tspan><tspan class="cmd">whoami</tspan></text>
    <text x="24" y="{y_user}" class="ln ln-user"><tspan class="user">felipe_lippelt</tspan></text>

    <text x="24" y="{y_boot}" class="ln ln-boot"><tspan class="prompt">$ </tspan><tspan class="cmd">./boot.sh</tspan></text>
    <text x="24" y="{y_post}" class="ln ln-post"><tspan class="ok">[ OK ]</tspan><tspan class="mid">  POST .............................. </tspan><tspan class="val">passed</tspan></text>
    <text x="24" y="{y_mount}" class="ln ln-mount"><tspan class="ok">[ OK ]</tspan><tspan class="mid">  mount /dev/felipe ................. </tspan><tspan class="val">ready</tspan></text>
    <text x="24" y="{y_stack}" class="ln ln-stack"><tspan class="ok">[ OK ]</tspan><tspan class="mid">  load stack: typescript rust node .. </tspan><tspan class="val">done</tspan></text>
    <text x="24" y="{y_rpg}" class="ln ln-engines"><tspan class="ok">[ OK ]</tspan><tspan class="mid">  init rpg-tooling engines .......... </tspan><tspan class="val">online</tspan></text>
    <text x="24" y="{y_ready}" class="ln ln-ready"><tspan class="ok">[ OK ]</tspan><tspan class="mid">  system ready ▸ </tspan><tspan class="ready">welcome! 🕶️</tspan></text>

    <text x="24" y="{y_brew1}" class="ln ln-brew1"><tspan class="prompt">$ </tspan><tspan class="cmd">brew install rpg human humor sarcasm brain creativity daughter \\</tspan></text>
    <text x="24" y="{y_brew2}" class="ln ln-brew2"><tspan class="cmd">               adhd thinking-outside-the-box dice-goblin</tspan></text>
    <text x="24" y="{y_upd}" class="ln ln-upd"><tspan class="eq">==&gt;</tspan><tspan class="mid"> Updating Homebrew...</tspan></text>
{row_group(json_row, "ln-json")}
    <text x="24" y="{y_fetch1}" class="ln ln-fetch1"><tspan class="eq">==&gt;</tspan><tspan class="mid"> Fetching downloads for: rpg, human, humor, sarcasm, brain,</tspan></text>
    <text x="24" y="{y_fetch2}" class="ln ln-fetch2"><tspan class="mid">    creativity, daughter, adhd, thinking-outside-the-box, dice-goblin</tspan></text>
{bottle_rows}
    <text x="24" y="{y_sum}" class="ln ln-sum"><tspan class="beer">🍺  10 installed</tspan></text>
    <text x="24" y="{y_keg}" class="ln ln-keg"><tspan class="mid">    human is keg-only — macOS already shipped one</tspan></text>

    <text x="24" y="{y_cat}" class="ln ln-cat"><tspan class="prompt">$ </tspan><tspan class="cmd">cat felipe.ts</tspan></text>
    <text x="24" y="{y_const}" class="ln ln-const"><tspan class="kw">const </tspan><tspan class="var">felipe_lippelt</tspan><tspan class="punc">: </tspan><tspan class="type">Dev</tspan><tspan class="punc"> = {{</tspan></text>
    <text x="24" y="{y_pronouns}" class="ln ln-pronouns"><tspan class="key">&#160;&#160;pronouns</tspan><tspan class="punc">: </tspan><tspan class="str">"he/him"</tspan><tspan class="punc">,</tspan></text>
    <text x="24" y="{y_role}" class="ln ln-role"><tspan class="key">&#160;&#160;role</tspan><tspan class="punc">: </tspan><tspan class="str">"helpdesk analyst @ ICL"</tspan><tspan class="punc">,</tspan></text>
    <text x="24" y="{y_location}" class="ln ln-location"><tspan class="key">&#160;&#160;location</tspan><tspan class="punc">: </tspan><tspan class="str">"São Paulo, BR"</tspan><tspan class="punc">,</tspan></text>
    <text x="24" y="{y_langs}" class="ln ln-langs"><tspan class="key">&#160;&#160;langs</tspan><tspan class="punc">: [</tspan><tspan class="str">"pt-BR", "en"</tspan><tspan class="punc">],</tspan></text>
    <text x="24" y="{y_code}" class="ln ln-code"><tspan class="key">&#160;&#160;code</tspan><tspan class="punc">: [</tspan><tspan class="str">"TypeScript", "JavaScript", "Rust", "Python", "Dart"</tspan><tspan class="punc">],</tspan></text>
    <text x="24" y="{y_tools}" class="ln ln-tools"><tspan class="key">&#160;&#160;tools</tspan><tspan class="punc">: [</tspan><tspan class="str">"React", "Node.js", "Astro", "Vite", "Socket.io"</tspan><tspan class="punc">],</tspan></text>
    <text x="24" y="{y_focus}" class="ln ln-focus"><tspan class="key">&#160;&#160;focus</tspan><tspan class="punc">: </tspan><tspan class="str">"TTRPG tooling — VTTs, immersive props, SRDs as code"</tspan><tspan class="punc">,</tspan></text>
    <text x="24" y="{y_learning}" class="ln ln-learning"><tspan class="key">&#160;&#160;learning</tspan><tspan class="punc">: </tspan><tspan class="str">"Rust + TTRPG system design"</tspan><tspan class="punc">,</tspan></text>
    <text x="24" y="{y_end}" class="ln ln-end"><tspan class="punc">}};</tspan></text>
  </g>

  <rect class="cursor" x="24" y="{cursor_y}" width="9" height="4"/>
</svg>
'''


def main() -> None:
    svg = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    previous = OUT.read_text() if OUT.exists() else ""
    if previous == svg:
        print(f"unchanged {OUT} (human {human_version()}, daughter {daughter_version()})")
        return
    OUT.write_text(svg)
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes, human {human_version()}, daughter {daughter_version()})")


if __name__ == "__main__":
    main()
