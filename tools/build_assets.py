#!/usr/bin/env python3
"""Generate the animated SVG art for the rootmaybe GitHub profile README.

    python tools/build_assets.py

The SVGs in ../assets are build output: change the constants below and re-run.
GitHub shows README images through <img>, so CSS and SMIL animation work but
JavaScript and web fonts do not. Text uses the system monospace stack and the
big title is drawn as vector paths so it looks the same everywhere.
Standard library only.
"""
from __future__ import annotations

import random
from pathlib import Path
from xml.sax.saxutils import escape

ASSETS = Path(__file__).resolve().parent.parent / "assets"

# ── identity ────────────────────────────────────────────────────────────────
TITLE = "ROOTMAYBE"
USER, HOST = "root", "maybe"

# ── palette: matrix green + cyberpunk accents ───────────────────────────────
MX, MXD = "#1dff6a", "#0b8a37"          # matrix rain: bright head, dim trail
GREEN, CYAN = "#39ff88", "#3ef2ff"
RED, AMBER, MAGENTA = "#ff3b5c", "#ffb000", "#ff2bd6"
INK, SOFT, DIM = "#e8ffef", "#8fb9a0", "#53785f"
BG = "#02060a"

MONO = ("ui-monospace,'Cascadia Mono','SF Mono',Menlo,Consolas,"
        "'DejaVu Sans Mono','Liberation Mono',monospace")
BASE_CSS = ("text{font-family:%s}" % MONO
            + "@media (prefers-reduced-motion:reduce){*{animation:none!important}}")

# Matrix rain glyphs: half-width katakana + hex, with a few cyber tokens mixed in.
GLYPHS = [chr(c) for c in range(0xFF66, 0xFF9E)] + list("0123456789ABCDEF<>/\\#$%*+=")

# Angular "neon tube" glyphs on a 44x64 grid (top-left / bottom-right chamfers).
LETTERS = {
    "A": "M0,64V12L12,0H44V64M0,36H44",
    "B": "M0,0H34L44,10V24L38,32L44,40V54L34,64H0ZM0,32H38",
    "C": "M44,0H12L0,12V64H44",
    "D": "M0,0H32L44,12V52L32,64H0Z",
    "E": "M44,0H0V64H44M0,32H32",
    "F": "M44,0H0V64M0,32H32",
    "M": "M0,64V0L22,26L44,0V64",
    "O": "M12,0H44V52L32,64H0V12Z",
    "R": "M0,64V0H32L44,12V22L34,32H0M20,32L44,64",
    "T": "M0,0H44M22,0V64",
    "Y": "M0,0L22,30L44,0M22,30V64",
}


# ── helpers ─────────────────────────────────────────────────────────────────
def num(v: float) -> str:
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


def svg(w: int, h: int, title: str, defs: str, body: str, css: str = "") -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img"><title>{escape(title)}</title>'
            f"<style>{BASE_CSS}{css}</style><defs>{defs}</defs>{body}</svg>\n")


def glow(fid: str, std: float, passes: int = 1) -> str:
    merge = '<feMergeNode in="b"/>' * passes
    return (f'<filter id="{fid}" x="-60%" y="-60%" width="220%" height="220%">'
            f'<feGaussianBlur stdDeviation="{std}" result="b"/>'
            f'<feMerge>{merge}<feMergeNode in="SourceGraphic"/></feMerge></filter>')


def key_times(ts: list[float], dur: float) -> str:
    out = [f"{t / dur:.4f}" for t in ts]
    out[0], out[-1] = "0", "1"
    return ";".join(out)


def timeline(attr: str, frames, dur: float, *, calc: str = "spline",
             ease: str = ".45 0 .55 1", transform: str | None = None) -> str:
    """One looping SMIL animation built from (seconds, value) frames."""
    merged: list[tuple[float, object]] = []
    for t, v in frames:  # same timestamp twice -> keep the later value
        if merged and t <= merged[-1][0] + 1e-6:
            merged[-1] = (merged[-1][0], v)
        else:
            merged.append((t, v))
    frames = merged
    if frames[0][0] > 0:
        frames.insert(0, (0, frames[0][1]))
    if frames[-1][0] < dur:
        frames.append((dur, frames[-1][1]))
    tag = "animateTransform" if transform else "animate"
    out = (f'<{tag} attributeName="{attr}"' + (f' type="{transform}"' if transform else "")
           + f' dur="{num(dur)}s" repeatCount="indefinite" calcMode="{calc}"'
           + f' keyTimes="{key_times([t for t, _ in frames], dur)}"'
           + f' values="{";".join(str(v) for _, v in frames)}"')
    if calc == "spline":
        out += f' keySplines="{";".join([ease] * (len(frames) - 1))}"'
    return out + "/>"


def mono_text(x: float, y: float, segs, size: float, char_w: float, **attrs) -> str:
    """<text> with coloured tspans, forced to a fixed advance per character."""
    chars = sum(len(s) for s, _ in segs)
    extra = "".join(f' {k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    spans = "".join(f'<tspan fill="{c}">{escape(s)}</tspan>' for s, c in segs)
    return (f'<text x="{num(x)}" y="{num(y)}" font-size="{size}" xml:space="preserve" '
            f'textLength="{num(chars * char_w)}" lengthAdjust="spacing"{extra}>{spans}</text>')


def title_paths(text: str) -> tuple[str, int]:
    parts = [f'<path transform="translate({i * 60} 0)" d="{LETTERS[ch]}"/>'
             for i, ch in enumerate(text.upper()) if ch != " "]
    return "".join(parts), len(text) * 60 - 16


# ── 1. matrix hero ──────────────────────────────────────────────────────────
HERO_CSS = """
.flick{animation:flick 6s linear infinite}
@keyframes flick{0%,38%,40%,43%,100%{opacity:1}39%,42%{opacity:.4}}
.gr{animation:gr 3.6s steps(1) infinite}
.gb{animation:gb 3.6s steps(1) infinite}
@keyframes gr{0%{transform:translate(-2px,0)}84%{transform:translate(-7px,1px)}87%{transform:translate(5px,-1px)}90%{transform:translate(-3px,1px)}93%{transform:translate(-2px,0)}}
@keyframes gb{0%{transform:translate(2px,0)}84%{transform:translate(7px,-1px)}87%{transform:translate(-5px,1px)}90%{transform:translate(3px,-1px)}93%{transform:translate(2px,0)}}
.sl{opacity:0;animation:sl 3.6s steps(1) infinite}
@keyframes sl{0%{opacity:0;transform:translateX(0)}84%{opacity:1;transform:translateX(12px)}87%{opacity:1;transform:translateX(-9px)}90%{opacity:1;transform:translateX(5px)}93%{opacity:0;transform:translateX(0)}}
.blink{animation:blink 1.05s steps(1) infinite}
@keyframes blink{50%{opacity:0}}
.beam{animation:beam 6s linear infinite}
@keyframes beam{from{transform:translateY(-120px)}to{transform:translateY(300px)}}
"""


def matrix_rain(W: int, H: int, rnd: random.Random) -> str:
    """Classic green digital rain: per-column strips scrolling down, head-lit."""
    cols, lh, fs = [], 19, 17
    rows = H // lh + 2
    x = 14
    while x < W:
        n = rows
        glyphs_a = [rnd.choice(GLYPHS) for _ in range(n)]
        glyphs_b = [rnd.choice(GLYPHS) for _ in range(n)]

        def strip(gl, y0):
            spans = "".join(f'<tspan x="{x}" dy="{lh if i else 0}">{escape(g)}</tspan>'
                            for i, g in enumerate(gl))
            return f'<text x="{x}" y="{y0}" font-size="{fs}" fill="url(#mg)">{spans}</text>'

        span_h = n * lh
        dur = rnd.uniform(5.5, 11)
        delay = -rnd.uniform(0, dur)
        # two identical copies stacked, wrapper slides one strip-height for a seamless loop
        cols.append(
            f'<g transform="translate(0 {-span_h})">'
            f'<animateTransform attributeName="transform" type="translate" from="0 {-span_h}" to="0 0" '
            f'dur="{dur:.2f}s" begin="{delay:.2f}s" repeatCount="indefinite"/>'
            f'{strip(glyphs_a, span_h)}{strip(glyphs_b, span_h * 2)}</g>')
        x += rnd.choice([25, 26, 27])
    return "".join(cols)


def hero() -> str:
    W, H = 1200, 300
    rnd = random.Random(1337)
    defs = [glow("g1", 2.2), glow("g2", 6, 2),
            f'<linearGradient id="mg" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{MXD}" stop-opacity="0"/>'
            f'<stop offset=".55" stop-color="{MXD}" stop-opacity=".55"/>'
            f'<stop offset=".9" stop-color="{MX}"/><stop offset="1" stop-color="#d7ffe4"/></linearGradient>',
            f'<radialGradient id="vig"><stop offset=".35" stop-color="{BG}" stop-opacity="0"/>'
            f'<stop offset="1" stop-color="{BG}" stop-opacity=".9"/></radialGradient>',
            f'<radialGradient id="halo"><stop offset="0" stop-color="{BG}" stop-opacity=".92"/>'
            f'<stop offset="1" stop-color="{BG}" stop-opacity="0"/></radialGradient>',
            f'<linearGradient id="frame" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{MX}"/>'
            f'<stop offset=".5" stop-color="{CYAN}"/><stop offset="1" stop-color="{MX}"/></linearGradient>',
            f'<linearGradient id="beam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{MX}" stop-opacity="0"/>'
            f'<stop offset=".5" stop-color="{MX}" stop-opacity=".06"/><stop offset="1" stop-color="{MX}" stop-opacity="0"/></linearGradient>',
            '<pattern id="scan" width="3" height="3" patternUnits="userSpaceOnUse"><rect width="3" height="1" fill="#000" opacity=".32"/></pattern>',
            f'<clipPath id="card"><rect width="{W}" height="{H}" rx="16"/></clipPath>']

    b = [f'<g clip-path="url(#card)"><rect width="{W}" height="{H}" fill="{BG}"/>',
         f'<g opacity=".92">{matrix_rain(W, H, rnd)}</g>',
         f'<rect width="{W}" height="{H}" fill="url(#vig)"/>',
         f'<ellipse cx="{W/2}" cy="118" rx="410" ry="112" fill="url(#halo)"/>']

    # glitch title
    paths, tw_ = title_paths(TITLE)
    scale = 1.45
    tx = (W - tw_ * scale) / 2
    stroke = 'fill="none" stroke-linejoin="miter" stroke-linecap="square"'
    defs.append('<clipPath id="slice"><rect x="-20" y="26" width="900" height="14"/></clipPath>')
    b.append(f'<g transform="translate({num(tx)} 48) scale({scale})" {stroke}>'
             f'<g class="gr" stroke="{RED}" stroke-width="5" opacity=".85" style="mix-blend-mode:screen">{paths}</g>'
             f'<g class="gb" stroke="{CYAN}" stroke-width="5" opacity=".85" style="mix-blend-mode:screen">{paths}</g>'
             f'<g class="flick"><g stroke="{MX}" stroke-width="11" opacity=".45" filter="url(#g2)">{paths}</g>'
             f'<g stroke="#eafff0" stroke-width="5">{paths}</g></g>'
             f'<g class="sl" clip-path="url(#slice)" stroke="{CYAN}" stroke-width="5">{paths}</g></g>')

    # prompt line: `root@maybe:~#` types `whoami`, then ` -> root` appears + cursor
    py, step, fs = 236, 11.2, 18
    pre = [(USER, MX), ("@", DIM), (HOST, CYAN), (":~# ", SOFT)]
    pre_n = sum(len(s) for s, _ in pre)
    cmd = "whoami"
    cmd_x = W / 2 - (pre_n + len(cmd) / 2) * step      # centre prompt + command
    cmd_start = cmd_x + pre_n * step
    end_type = 1 + len(cmd) * .09
    widths = ";".join(str(k * step + 2) for k in range(len(cmd) + 1))
    xs = ";".join(num(cmd_start + k * step) for k in range(len(cmd) + 1))
    b.append(mono_text(cmd_x, py, pre, fs, step, filter="url(#g1)"))
    defs.append(f'<clipPath id="cmd"><rect x="{num(cmd_start - 1)}" y="{py - 15}" height="22" width="0">'
                f'<animate attributeName="width" values="{widths}" begin="1s" dur="{num(len(cmd) * .09)}s" '
                f'calcMode="discrete" fill="freeze"/></rect></clipPath>')
    b.append(f'<g clip-path="url(#cmd)">' + mono_text(cmd_start, py, [(cmd, INK)], fs, step) + "</g>")
    b.append('<g opacity="0">'
             f'<animate attributeName="opacity" values="0;1" dur=".4s" begin="{num(end_type + .25)}s" fill="freeze"/>'
             + mono_text(cmd_start + (len(cmd) + 1) * step, py, [("→ ", DIM), ("root", MX)], fs, step, filter="url(#g1)")
             + "</g>")
    b.append(f'<rect y="{py - 15}" x="{num(cmd_start)}" width="{num(step - 1)}" height="20" fill="{MX}" class="blink">'
             f'<animate attributeName="x" values="{xs}" begin="1s" dur="{num(len(cmd) * .09)}s" calcMode="discrete" fill="freeze"/></rect>')

    # HUD corners + scanlines + beam + frame
    b.append(f'<g fill="none" stroke="{MX}" stroke-width="2" opacity=".6">'
             f'<path d="M14,42V14H42M{W-42},14H{W-14}V42M{W-14},{H-42}V{H-14}H{W-42}M42,{H-14}H14V{H-42}"/></g>'
             f'<circle cx="34" cy="31" r="4" fill="{RED}" class="blink"/>'
             f'<text x="46" y="35" font-size="11.5" fill="{DIM}"><tspan fill="{MX}">SYS</tspan> ONLINE · SECURE SHELL</text>'
             f'<text x="{W-30}" y="35" font-size="11.5" fill="{DIM}" text-anchor="end">{escape("uptime 1337d // 0 incidents open")}</text>')
    b.append(f'<rect width="{W}" height="{H}" fill="url(#scan)" opacity=".5"/>'
             f'<rect width="{W}" height="120" fill="url(#beam)" class="beam"/></g>'
             f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="16" fill="none" stroke="url(#frame)" stroke-width="2" opacity=".8"/>')
    return svg(W, H, f"{TITLE} - matrix", "".join(defs), "".join(b), HERO_CSS)


# ── 2. terminal ─────────────────────────────────────────────────────────────
TERM_CSS = """
.blink{animation:blink 1.05s steps(1) infinite}
@keyframes blink{50%{opacity:0}}
.beam{animation:beam 6s linear infinite}
@keyframes beam{from{transform:translateY(0)}to{transform:translateY(430px)}}
"""


def terminal() -> str:
    W, H = 860, 328
    FS, CW, LH, X0, Y0 = 14, 8.4, 22, 26, 74
    prompt = [(USER, MX), ("@", DIM), (HOST, CYAN), (":", DIM), ("~", SOFT), ("$ ", INK)]
    plen = sum(len(s) for s, _ in prompt)
    ok = [("[ ", DIM), ("OK", GREEN), (" ] ", DIM)]

    def hit(src: str, detail: str, technique: str, tool: str):
        return [("[!] ", RED), (f"{src:<10}", AMBER), (f"{detail:<31}", SOFT), (f"{technique:<11}", CYAN), (tool, MAGENTA)]

    script = [
        ("cmd", "whoami && uname -sr"),
        ("out", [("> ", DIM), ("root", MX), ("   Linux 6.8.0-secure", SOFT)]),
        ("cmd", "./hunt --since 7d --map attack"),
        ("out", hit("SYSMON 10", "lsass.exe GrantedAccess=0x1010", "T1003.001", "mimikatz")),
        ("out", hit("EID 4769", "TicketEncryptionType=0x17", "T1558.003", "rubeus")),
        ("out", hit("EID 7045", "ImagePath=%COMSPEC% /Q /c", "T1569.002", "smbexec")),
        ("out", hit("SYSMON 3", "rclone → mega.nz", "T1567.002", "exfil")),
        ("bar", 20),
        ("out", ok + [("4 alerts → 1 incident → ", INK), ("contained", GREEN)]),
        ("cmd", ""),
    ]

    t = 0.8
    lines, cursor, bar = [], [(0, X0, Y0)], None
    for i, (kind, data) in enumerate(script):
        y = Y0 + i * LH
        if kind == "cmd":
            frames = [(t, plen * CW)]
            cursor.append((t, X0 + plen * CW, y))
            t += .4
            for k in range(1, len(data) + 1):
                frames.append((t, (plen + k) * CW))
                cursor.append((t, X0 + (plen + k) * CW, y))
                t += .055
            t += .35
            segs = prompt + [(data, INK)]
        elif kind == "out":
            segs = data
            frames = [(t, sum(len(s) for s, _ in segs) * CW)]
            t += .3 if segs[0][0] == "[!] " else .16
            cursor.append((t, X0, y + LH))
        else:  # progress bar
            segs = [("[", DIM), (" " * data, DIM), ("]", DIM), (" 100%", GREEN),
                    ("  4 alerts → 1 incident → isolated", SOFT)]
            frames = [(t, (data + 2) * CW)]
            bar = (y, data, t)
            t += 1.5
            frames.append((t, sum(len(s) for s, _ in segs) * CW))
            t += .2
            cursor.append((t, X0, y + LH))
        lines.append((y, segs, frames))
    dur = t + 4.0

    defs = [glow("g1", 1.6)]
    defs.append(f'<linearGradient id="edge" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{MX}"/>'
                f'<stop offset=".5" stop-color="{CYAN}"/><stop offset="1" stop-color="{MX}"/>'
                f'<animateTransform attributeName="gradientTransform" type="rotate" values="0 .5 .5;360 .5 .5" '
                f'dur="9s" repeatCount="indefinite"/></linearGradient>')
    defs.append('<pattern id="grid" width="22" height="22" patternUnits="userSpaceOnUse">'
                '<path d="M22,0H0V22" fill="none" stroke="#0a2217" stroke-width="1"/></pattern>')
    defs.append('<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">'
                '<rect width="4" height="1" fill="#000" opacity=".3"/></pattern>')
    defs.append(f'<linearGradient id="beam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{MX}" stop-opacity="0"/>'
                f'<stop offset=".5" stop-color="{MX}" stop-opacity=".05"/><stop offset="1" stop-color="{MX}" stop-opacity="0"/></linearGradient>')
    defs.append(f'<clipPath id="card"><rect width="{W}" height="{H}" rx="14"/></clipPath>')
    if bar:
        defs.append(f'<pattern id="blk" x="{num(X0 + CW)}" width="{CW}" height="14" patternUnits="userSpaceOnUse">'
                    f'<rect x=".9" width="{num(CW - 1.8)}" height="14" fill="{GREEN}"/></pattern>')

    b = [f'<g clip-path="url(#card)"><rect width="{W}" height="{H}" fill="#03080c"/>'
         f'<rect y="40" width="{W}" height="{H - 40}" fill="url(#grid)" opacity=".6"/>'
         f'<rect width="{W}" height="40" fill="#061009"/><path d="M0,40.5H{W}" stroke="#113322"/>'
         f'<circle cx="24" cy="20" r="6" fill="{RED}"/><circle cx="44" cy="20" r="6" fill="{AMBER}"/>'
         f'<circle cx="64" cy="20" r="6" fill="{GREEN}"/>'
         f'<text x="{W / 2}" y="25" font-size="12" fill="{DIM}" text-anchor="middle">{USER}@{HOST}: ~/soc — zsh</text>'
         f'<circle cx="{W - 66}" cy="20" r="4" fill="{MX}" class="blink"/>'
         f'<text x="{W - 24}" y="24.5" font-size="11.5" fill="{MX}" text-anchor="end">LIVE</text>']

    for i, (y, segs, frames) in enumerate(lines):
        defs.append(f'<clipPath id="ln{i}"><rect x="{X0 - 2}" y="{num(y - FS)}" height="{LH - 2}" width="0">'
                    + timeline("width", [(0, 0)] + [(ft, num(w + 2)) for ft, w in frames], dur, calc="discrete")
                    + "</rect></clipPath>")
        b.append(f'<g clip-path="url(#ln{i})">' + mono_text(X0, y, segs, FS, CW) + "</g>")
    if bar:
        y, blocks, t0 = bar
        steps = [(0, 0), (t0, 0)] + [(t0 + k * 1.4 / blocks, num(k * CW)) for k in range(1, blocks + 1)]
        b.append(f'<rect x="{num(X0 + CW)}" y="{y - 10.5}" height="12.5" width="0" fill="url(#blk)" filter="url(#g1)">'
                 + timeline("width", steps, dur, calc="discrete") + "</rect>")
    b.append(f'<rect width="{num(CW - 1)}" height="{FS + 2}" fill="{INK}" opacity=".9" class="blink">'
             + timeline("x", [(ct, num(cx)) for ct, cx, _ in cursor], dur, calc="discrete")
             + timeline("y", [(ct, num(cy - FS + 1)) for ct, _, cy in cursor], dur, calc="discrete") + "</rect>")

    b.append(f'<rect width="{W}" height="{H}" fill="url(#scan)" opacity=".45"/>'
             f'<rect y="-80" width="{W}" height="80" fill="url(#beam)" class="beam"/></g>'
             f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="none" stroke="url(#edge)" stroke-width="2"/>')
    return svg(W, H, "rootmaybe terminal", "".join(defs), "".join(b), TERM_CSS)


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    for name, build in (("hero", hero), ("terminal", terminal)):
        out = ASSETS / f"{name}.svg"
        out.write_text(build(), encoding="utf-8", newline="\n")
        print(f"assets/{out.name:<16}{out.stat().st_size / 1024:6.1f} KB")


if __name__ == "__main__":
    main()
