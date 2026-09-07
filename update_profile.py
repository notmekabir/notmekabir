from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
import re
import requests
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
USERNAME = os.getenv("USER_NAME", "notmekabir")
TOKEN = os.environ["GITHUB_TOKEN"]

QUERY = """
query($login:String!, $from:DateTime!, $to:DateTime!) {
  user(login:$login) {
    repositories(first:100, ownerAffiliations:OWNER, privacy:PUBLIC) {
      totalCount
      nodes { stargazerCount }
    }
    followers { totalCount }
    following { totalCount }
    contributionsCollection(from:$from, to:$to) {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""

def github_data():
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=365)

    r = requests.post(
        "https://api.github.com/graphql",
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/json",
        },
        json={
            "query": QUERY,
            "variables": {
                "login": USERNAME,
                "from": start.isoformat(),
                "to": now.isoformat(),
            },
        },
        timeout=30,
    )
    r.raise_for_status()
    payload = r.json()
    if payload.get("errors"):
        raise RuntimeError(payload["errors"])
    return payload["data"]["user"]

def replace_svg_text(svg, element_id, value):
    pattern = re.compile(
        rf'(<text\b[^>]*\bid="{re.escape(element_id)}"[^>]*>)(.*?)(</text>)',
        re.S,
    )
    updated, count = pattern.subn(r"\g<1>" + str(value) + r"\g<3>", svg, count=1)
    if count != 1:
        raise RuntimeError(f"Missing SVG element: {element_id}")
    return updated

def update_profile_svgs(user):
    values = {
        "repo_data": user["repositories"]["totalCount"],
        "star_data": sum(n["stargazerCount"] for n in user["repositories"]["nodes"]),
        "follower_data": user["followers"]["totalCount"],
        "following_data": user["following"]["totalCount"],
        "contrib_data": user["contributionsCollection"]["contributionCalendar"]["totalContributions"],
        "sync_data": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    }

    for filename in ("dark_mode.svg", "light_mode.svg"):
        path = ASSETS / filename
        svg = path.read_text(encoding="utf-8")
        for key, value in values.items():
            svg = replace_svg_text(svg, key, value)
        # Validate after every write.
        ET.fromstring(svg)
        path.write_text(svg, encoding="utf-8")

def level(count):
    if count == 0:
        return 0
    if count <= 2:
        return 1
    if count <= 5:
        return 2
    if count <= 9:
        return 3
    return 4

def write_activity_graph(user):
    cal = user["contributionsCollection"]["contributionCalendar"]
    weeks = cal["weeks"]

    W, H = 1200, 270
    bg = "#07140f"
    stroke = "#173c30"
    text = "#d7f1e6"
    muted = "#6b9185"
    green = "#35f2a3"
    shades = ["#10251d", "#174534", "#1d7653", "#27ad76", "#35f2a3"]

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">',
        '<title id="title">GitHub contribution activity for notmekabir</title>',
        '<desc id="desc">A locally generated contribution heatmap updated by GitHub Actions.</desc>',
        f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="14" fill="{bg}" stroke="{stroke}"/>',
        f'<text x="24" y="30" fill="{green}" font-family="monospace" font-size="13">GITHUB // CONTRIBUTION ACTIVITY</text>',
        f'<text x="24" y="51" fill="{muted}" font-family="monospace" font-size="11">365 days · {cal["totalContributions"]:,} contributions · generated locally</text>',
    ]

    # Draw a 53x7 contribution grid using actual GitHub contributionCalendar data.
    cell = 15
    gap = 3
    x0, y0 = 24, 72
    for wi, week in enumerate(weeks[-53:]):
        for di, day in enumerate(week["contributionDays"]):
            x = x0 + wi * (cell + gap)
            y = y0 + di * (cell + gap)
            lvl = level(day["contributionCount"])
            title = f'{day["date"]}: {day["contributionCount"]} contributions'
            svg.append(
                f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" '
                f'fill="{shades[lvl]}"><title>{title}</title></rect>'
            )

    # Weekday labels
    for i, label in enumerate(("Mon", "Wed", "Fri")):
        y = y0 + i * 2 * (cell + gap) + 11
        svg.append(f'<text x="1105" y="{y}" fill="{muted}" font-family="monospace" font-size="10">{label}</text>')

    # Legend
    ly = 205
    svg.append(f'<text x="24" y="{ly+10}" fill="{muted}" font-family="monospace" font-size="10">less</text>')
    for i, shade in enumerate(shades):
        lx = 58 + i * 22
        svg.append(f'<rect x="{lx}" y="{ly}" width="15" height="15" rx="3" fill="{shade}"/>')
    svg.append(f'<text x="178" y="{ly+10}" fill="{muted}" font-family="monospace" font-size="10">more</text>')

    svg.append("</svg>")
    out = ASSETS / "contribution-activity.svg"
    out.write_text("\n".join(svg), encoding="utf-8")
    ET.parse(out)

if __name__ == "__main__":
    user = github_data()
    update_profile_svgs(user)
    write_activity_graph(user)
    print("Updated dynamic profile SVGs and contribution activity graph.")
