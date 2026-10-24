"""Rewrite the "recent projects" block in README.md with my latest-pushed public repos."""
import json
import os
import re
import urllib.request

USER = "songxiaofeng1981"
COUNT = 6
START = "<!-- RECENT:START -->"
END = "<!-- RECENT:END -->"


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


def main():
    repos = [
        r for r in fetch_repos()
        if not r["fork"] and not r["archived"] and not r["private"] and r["name"] != USER
    ]
    repos.sort(key=lambda r: r["pushed_at"], reverse=True)

    lines = ["| 项目 | 简介 | 最近更新 |", "| --- | --- | --- |"]
    for r in repos[:COUNT]:
        desc = (r["description"] or "").replace("|", "\\|")
        lines.append(f"| [{r['name']}]({r['html_url']}) | {desc} | {r['pushed_at'][:10]} |")
    block = f"{START}\n" + "\n".join(lines) + f"\n{END}"

    with open("README.md", encoding="utf-8") as f:
        readme = f.read()
    readme = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: block, readme, flags=re.S)
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)


if __name__ == "__main__":
    main()
