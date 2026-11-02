#!/usr/bin/env python3
"""Gera top-langs.svg e codeforces.json (tema tokyonight).

Uso: python scripts/cards.py   (GITHUB_TOKEN opcional, evita limite da API)
"""
import json
import os
import urllib.request
from html import escape

GH_USER = "CaioParanaiba"
CF_HANDLE = "CaioParanaiba"
LANGS_COUNT = 6
IGNORE_REPOS = {"ganbatte"}  # projetos de teste, não refletem o que programo
IGNORE_LANGS = {"HTML", "Makefile", "CMake", "Shell", "Dockerfile"}

BG, TITLE, TEXT = "#1a1b27", "#70a5fd", "#a9b1d6"
FONT = "'Segoe UI', Ubuntu, Sans-Serif"

LANG_COLORS = {
    "C": "#A8B9CC", "C++": "#f34b7d", "Go": "#00ADD8", "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6", "Python": "#3572A5", "HTML": "#e34c26",
    "CSS": "#663399", "Java": "#b07219", "Lua": "#000080", "Rust": "#dea584",
}

CF_RANKS = [  # (rating mínimo, nome, cor)
    (3000, "Legendary Grandmaster", "#ff0000"),
    (2600, "International Grandmaster", "#ff0000"),
    (2400, "Grandmaster", "#ff0000"),
    (2300, "International Master", "#ff8c00"),
    (2100, "Master", "#ff8c00"),
    (1900, "Candidate Master", "#aa00aa"),
    (1600, "Expert", "#3b5bdb"),
    (1400, "Specialist", "#03a89e"),
    (1200, "Pupil", "#008000"),
    (0, "Newbie", "#808080"),
]


def get(url, token=None):
    req = urllib.request.Request(url, headers={"User-Agent": "readme-cards"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def top_langs():
    token = os.environ.get("GITHUB_TOKEN")
    repos = get(f"https://api.github.com/users/{GH_USER}/repos?per_page=100", token)
    total = {}
    for repo in repos:
        if repo["fork"] or repo["name"] in IGNORE_REPOS:
            continue
        for lang, n in get(repo["languages_url"], token).items():
            if lang not in IGNORE_LANGS:
                total[lang] = total.get(lang, 0) + n
    top = sorted(total.items(), key=lambda kv: -kv[1])[:LANGS_COUNT]
    soma = sum(n for _, n in top) or 1
    return [(lang, n / soma * 100) for lang, n in top if n / soma >= 0.01]


def svg_top_langs(langs):
    """Barra fina sem moldura, fundo transparente: funciona no tema claro e escuro."""
    w, h, bar_w = 720, 76, 720
    muted = "#8b949e"
    parts, x = [], 0.0
    for lang, pct in langs:
        seg = bar_w * pct / 100
        parts.append(f'<rect x="{x:.2f}" y="0" width="{seg + 0.5:.2f}" height="10" '
                     f'fill="{LANG_COLORS.get(lang, "#858585")}"/>')
        x += seg
    legend, lx = [], 0
    for lang, pct in langs:
        label = f"{lang} {pct:.1f}%"
        legend.append(
            f'<circle cx="{lx + 5}" cy="61" r="5" fill="{LANG_COLORS.get(lang, "#858585")}"/>'
            f'<text x="{lx + 15}" y="66" class="t">{escape(label)}</text>')
        lx += 30 + len(label) * 8
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<style>.h{{font:600 12px {FONT};fill:{muted};letter-spacing:2px}}.t{{font:400 14px {FONT};fill:{muted}}}</style>
<text x="0" y="14" class="h">MOST USED LANGUAGES</text>
<clipPath id="c"><rect x="0" y="0" width="{bar_w}" height="10" rx="5"/></clipPath>
<g transform="translate(0,28)" clip-path="url(#c)">{"".join(parts)}</g>
{"".join(legend)}
</svg>
'''


def codeforces_badge():
    """JSON no formato do shields.io (endpoint badge), na cor do rank atual."""
    u = get(f"https://codeforces.com/api/user.info?handles={CF_HANDLE}")["result"][0]
    rating = u.get("rating", 0)
    rank, cor = next((n, c) for r, n, c in CF_RANKS if rating >= r)
    return {
        "schemaVersion": 1,
        "label": "Codeforces",
        "message": f"{rank} · {rating}",
        "color": cor.lstrip("#"),
        "namedLogo": "codeforces",
        "logoColor": "white",
    }


if __name__ == "__main__":
    with open("top-langs.svg", "w") as f:
        f.write(svg_top_langs(top_langs()))
    with open("codeforces.json", "w") as f:
        json.dump(codeforces_badge(), f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("ok: top-langs.svg, codeforces.json")
