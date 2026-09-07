from __future__ import annotations
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
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
      contributionCalendar { totalContributions }
    }
  }
}
"""

def get_stats():
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=365)

    response = requests.post(
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
    response.raise_for_status()
    payload = response.json()

    if payload.get("errors"):
        raise RuntimeError(payload["errors"])

    user = payload["data"]["user"]

    return {
        "repo_data": user["repositories"]["totalCount"],
        "star_data": sum(n["stargazerCount"] for n in user["repositories"]["nodes"]),
        "follower_data": user["followers"]["totalCount"],
        "following_data": user["following"]["totalCount"],
        "contrib_data": user["contributionsCollection"]["contributionCalendar"]["totalContributions"],
        "sync_data": now.strftime("%Y-%m-%d %H:%M UTC"),
    }

def replace_text(svg, element_id, value):
    pattern = re.compile(
        rf'(<text\b[^>]*\bid="{re.escape(element_id)}"[^>]*>)(.*?)(</text>)',
        flags=re.DOTALL,
    )
    updated, count = pattern.subn(rf'\g<1>{value}\g<3>', svg, count=1)
    if count != 1:
        raise RuntimeError(f"SVG element not found: {element_id}")
    return updated

def update_svg(path, values):
    svg = path.read_text(encoding="utf-8")
    for key, value in values.items():
        svg = replace_text(svg, key, str(value))
    path.write_text(svg, encoding="utf-8")

if __name__ == "__main__":
    values = get_stats()
    for filename in ("assets/dark_mode.svg", "assets/light_mode.svg"):
        update_svg(ROOT / filename, values)
    print("Updated SVG telemetry:", values)
