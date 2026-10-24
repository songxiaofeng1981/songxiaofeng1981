"""Draw my profile cards (SVG) and point README.md at my latest-pushed public repos.

Text you may want to change lives in the CONFIG block below.
"""
import json
import os
import re
import urllib.request
from html import escape

# ---------------- CONFIG ----------------
USER = "songxiaofeng1981"
TOP_LABEL = "SONG'S WORKBENCH"
TITLE_DARK = "Song 的 "
TITLE_GREEN = "项目工作台"
SUBTITLE = "最近更新的项目排在最前面 · 每 6 小时自动刷新"
NOW_DOING = [
    ("本地文件 Chrome 插件：", "用 Mac 本机助手整理图片、HTML 资料和 iPhone 照片"),
    ("投资笔记：", "stock-blog 与 my-blog 双站点同步写作"),
    ("投研工具：", "个人股票投研工作台，把研究流程沉淀成工具"),
]
FOCUS_TAGS = ["Chrome 插件", "Mac 工具", "投资研究", "AI 视频"]
FOOTER_NOTE = "最新的放最前面，给自己看"
SMALL_COUNT = 4  # cards after the big "01" card
# ----------------------------------------

START = "<!-- RECENT:START -->"
END = "<!-- RECENT:END -->"
FONT = "-apple-system, BlinkMacSystemFont, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'Noto Sans CJK SC', sans-serif"
MONO = "'JetBrains Mono', 'SFMono-Regular', Menlo, Consolas, monospace"

NAVY = "#0D1B2E"
GREEN = "#159A62"
ORANGE = "#EE792F"
SUB = "#3A4856"
MUTED = "#6B7785"


def fetch_repos():
    req = urllib.request.Request(
        f"https://api.github.com/users/{USER}/repos?sort=pushed&per_page=100",
        headers={"Accept": "application/vnd.github+json"},
    )
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def char_w(c):
    if ord(c) > 0x2E80:
        return 1.0
    if c == " ":
        return 0.3
    if c.isupper() or c in "MW@%&":
        return 0.68
    if c in "il.,:;|!'":
        return 0.3
    return 0.57


def text_w(s, size, weight=1.0):
    return sum(char_w(c) for c in s) * size * weight


def wrap(s, size, width, max_lines):
    """Greedy wrap that keeps Latin words whole; ellipsis on the last line if cut."""
    tokens = re.findall(r"[A-Za-z0-9'’\-./:]+|\s+|.", s)
    lines, cur = [], ""
    for tok in tokens:
        if text_w(cur + tok, size) <= width:
            cur += tok
            continue
        if cur.strip():
            lines.append(cur.strip())
        cur = tok.lstrip()
        if len(lines) == max_lines:
            break
    if len(lines) < max_lines and cur.strip():
        lines.append(cur.strip())
    cut = len(lines) == max_lines and "".join(lines).replace(" ", "") != s.replace(" ", "")
    if cut:
        last = lines[-1]
        while last and text_w(last + "…", size) > width:
            last = last[:-1]
        lines[-1] = last.rstrip() + "…"
    return lines


def pick_desc(desc):
    desc = (desc or "").strip()
    if " / " in desc:
        tail = desc.split(" / ")[-1]
        if re.search(r"[一-鿿]", tail):
            return tail
    return desc or "（还没写简介）"


def svg(w, h, body, defs=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
        f"<defs>{defs}</defs>"
        f'<g font-family="{FONT}">{body}</g></svg>\n'
    )


def t(x, y, s, size, weight, fill, anchor="start", extra=""):
    return (
        f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
        f'text-anchor="{anchor}" {extra}>{escape(s)}</text>'
    )


def badge(x, y, num, size=40):
    return (
        f'<rect x="{x}" y="{y + 3}" width="{size}" height="{size}" rx="10" fill="{GREEN}" opacity="0.25"/>'
        f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="10" fill="{GREEN}"/>'
        + t(x + size / 2, y + size / 2 + 7, num, size / 2, 800, "#fff", "middle")
    )


def pill(x_right, cy, label, size, fill, color):
    w = text_w(label, size, 1.05) + 16
    return (
        f'<rect x="{x_right - w}" y="{cy - 12}" width="{w}" height="24" rx="6" fill="{fill}"/>'
        + t(x_right - w / 2, cy + size * 0.36, label, size, 800, color, "middle")
    )


def header_svg(latest_date):
    w, h = 840, 250
    label_end = 42 + text_w(TOP_LABEL, 14) + len(TOP_LABEL) * 3 + 20
    body = (
        f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="20" fill="#FBF9F3" stroke="#0D1B2E" stroke-opacity="0.06"/>'
        + t(42, 56, TOP_LABEL, 14, 600, MUTED, extra='letter-spacing="3"')
        + f'<line x1="{label_end}" y1="51" x2="{w - 122}" y2="51" stroke="#CBD2D9" stroke-width="1.5"/>'
        + f'<circle cx="{w - 100}" cy="51" r="5.5" fill="#199C65"/>'
        + f'<circle cx="{w - 79}" cy="51" r="5.5" fill="#26B479"/>'
        + f'<circle cx="{w - 58}" cy="51" r="5.5" fill="#F07B2C"/>'
        + f'<text x="42" y="138" font-size="56" font-weight="900" letter-spacing="-1" fill="{NAVY}">'
        f'{escape(TITLE_DARK)}<tspan fill="{GREEN}">{escape(TITLE_GREEN)}</tspan></text>'
        + '<rect x="42" y="158" width="160" height="8" rx="4" fill="url(#ul)"/>'
        + t(42, 208, SUBTITLE, 16.5, 600, SUB)
        + t(w - 42, 208, f"最近一次更新 {latest_date}", 14.5, 800, "#D9601A", "end")
    )
    defs = (
        f'<linearGradient id="ul" x1="0" x2="1"><stop offset="0" stop-color="{GREEN}"/>'
        f'<stop offset="1" stop-color="{GREEN}" stop-opacity="0.15"/></linearGradient>'
    )
    return svg(w, h, body, defs)


def hero_svg(r):
    w, h = 840, 236
    name = r["name"]
    name_end = 82 + text_w(name, 28, 1.08)
    lines = wrap(pick_desc(r["description"]), 16.5, 420, 3)
    desc = "".join(t(82, 100 + i * 25, ln, 16.5, 600, SUB) for i, ln in enumerate(lines))
    url = f"github.com/{USER}/{name}"
    url_w = text_w(url + "  →", 14, 1.12) + 28

    px, py, pw = 548, 28, 264
    slots = [
        ("最近更新", r["pushed_at"][:10], "rgba(21,154,98,0.3)", "#4ADE80"),
        ("主要语言", r["language"] or "—", "rgba(238,121,47,0.2)", "#FFA263"),
        ("Star", f"★ {r['stargazers_count']}", "rgba(148,163,184,0.2)", "#CBD5E1"),
    ]
    panel = f'<rect x="{px}" y="{py}" width="{pw}" height="{h - 56}" rx="14" fill="#1C2D42"/>'
    for i, (label, value, bg, fg) in enumerate(slots):
        sy = py + 16 + i * 52
        panel += (
            f'<rect x="{px + 16}" y="{sy}" width="{pw - 32}" height="42" rx="8" fill="#293E58"/>'
            + t(px + 30, sy + 26, label, 13, 700, "#CBD5E1")
            + pill(px + pw - 28, sy + 21, value, 13, bg, fg)
        )

    body = (
        f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="18" fill="url(#g1)" stroke="{GREEN}" stroke-opacity="0.1"/>'
        + badge(28, 30, "01")
        + t(82, 61, name, 28, 900, NAVY, extra='letter-spacing="-0.5"')
        + f'<rect x="{name_end + 12}" y="40" width="72" height="24" rx="12" fill="{ORANGE}"/>'
        + t(name_end + 48, 57, "最新 NEW", 12.5, 800, "#fff", "middle")
        + desc
        + f'<rect x="82" y="{h - 62}" width="{url_w}" height="34" rx="10" fill="{GREEN}"/>'
        + t(82 + url_w / 2, h - 40, url + "  →", 14, 800, "#fff", "middle")
        + panel
    )
    defs = (
        '<linearGradient id="g1" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#EEF8F2"/><stop offset="1" stop-color="#E3F3EA"/></linearGradient>'
    )
    return svg(w, h, body, defs)


def small_svg(r, num):
    w, h = 412, 196
    lines = wrap(pick_desc(r["description"]), 15, 366, 2)
    desc = "".join(t(24, 92 + i * 22, ln, 15, 600, SUB) for i, ln in enumerate(lines))
    lang = r["language"] or "—"
    body = (
        f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="18" fill="url(#g2)" stroke="{GREEN}" stroke-opacity="0.1"/>'
        + badge(24, 22, num, 36)
        + t(72, 48, r["name"], 22, 900, NAVY, extra='letter-spacing="-0.4"')
        + f'<rect x="24" y="{h - 64}" width="{w - 48}" height="42" rx="12" fill="#102034"/>'
        + f'<circle cx="40" cy="{h - 43}" r="4" fill="#EF4444"/>'
        + f'<circle cx="53" cy="{h - 43}" r="4" fill="#F59E0B"/>'
        + f'<circle cx="66" cy="{h - 43}" r="4" fill="#10B981"/>'
        + f'<text x="82" y="{h - 38}" font-family="{MONO}" font-size="13.5" font-weight="700" fill="#F8FAFC">'
        f'updated {r["pushed_at"][:10]} <tspan fill="#34D399">→ {escape(lang)}</tspan></text>'
        + desc
    )
    defs = (
        '<linearGradient id="g2" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#F3F8F5"/><stop offset="1" stop-color="#EBF4EE"/></linearGradient>'
    )
    return svg(w, h, body, defs)


def footer_svg():
    w = 840
    box_h = 40 + len(NOW_DOING) * 28
    h = box_h + 96
    items = ""
    for i, (key, text) in enumerate(NOW_DOING):
        y = 50 + i * 28
        items += (
            t(128, y, "•", 15.5, 900, NAVY)
            + f'<text x="144" y="{y}" font-size="15.5" font-weight="700" fill="{NAVY}">'
            f'<tspan fill="#C8500B">{escape(key)}</tspan>{escape(text)}</text>'
        )
    tags_y = box_h + 44
    tags = "  |  ".join(FOCUS_TAGS)
    body = (
        f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="20" fill="#FBF9F3" stroke="#0D1B2E" stroke-opacity="0.06"/>'
        f'<rect x="20" y="16" width="{w - 40}" height="{box_h}" rx="16" fill="#FAEDE1"/>'
        f'<circle cx="68" cy="{16 + box_h / 2}" r="26" fill="{ORANGE}"/>'
        + t(68, 16 + box_h / 2 + 10, "!", 30, 900, "#fff", "middle")
        + f'<rect x="108" y="{16 + box_h / 2 - 32}" width="1.5" height="64" fill="{ORANGE}" fill-opacity="0.3"/>'
        + items
        + f'<text x="42" y="{tags_y}" font-size="14.5" font-weight="800" fill="{NAVY}">'
        f'<tspan fill="#D9601A">关注方向：</tspan>{escape(tags)}</text>'
        + t(w - 42, tags_y, FOOTER_NOTE, 13, 600, "#7C8894", "end")
        + f'<line x1="42" y1="{tags_y + 14}" x2="{w - 42}" y2="{tags_y + 14}" stroke="#CBD2D9" stroke-width="1.5"/>'
        + t(42, tags_y + 36, "SONG'S WORKBENCH v1.0", 13, 700, MUTED)
        + t(w - 42, tags_y + 36, f"github.com/{USER}", 13, 700, MUTED, "end")
    )
    return svg(w, h, body)


def main():
    repos = [
        r for r in fetch_repos()
        if not r["fork"] and not r["archived"] and not r["private"] and r["name"] != USER
    ]
    repos.sort(key=lambda r: r["pushed_at"], reverse=True)
    top = repos[: 1 + SMALL_COUNT]

    os.makedirs("cards", exist_ok=True)
    files = {
        "cards/header.svg": header_svg(top[0]["pushed_at"][:10]),
        "cards/project-1.svg": hero_svg(top[0]),
        "cards/footer.svg": footer_svg(),
    }
    for i, r in enumerate(top[1:], start=2):
        files[f"cards/project-{i}.svg"] = small_svg(r, f"{i:02d}")
    for path, content in files.items():
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def link(i, r, width):
        return f'<a href="{r["html_url"]}"><img src="cards/project-{i}.svg" width="{width}" alt="{r["name"]}"></a>'

    parts = ['<img src="cards/header.svg" width="100%" alt="Song 的项目工作台">', "", link(1, top[0], "100%"), ""]
    rest = list(enumerate(top[1:], start=2))
    for k in range(0, len(rest), 2):
        parts.append("<p>\n" + "\n".join(link(i, r, "49%") for i, r in rest[k:k + 2]) + "\n</p>")
    parts += ["", '<img src="cards/footer.svg" width="100%" alt="现在在做">']
    block = f"{START}\n" + "\n".join(parts) + f"\n{END}"

    with open("README.md", encoding="utf-8") as f:
        readme = f.read()
    readme = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: block, readme, flags=re.S)
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)


if __name__ == "__main__":
    main()
