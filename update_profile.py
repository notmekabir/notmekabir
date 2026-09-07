#!/usr/bin/env python3
"""
Update the dynamic SVG profile card for @notmekabir.

Uses GitHub GraphQL with the Actions-provided GITHUB_TOKEN.
No personal access token is required.
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path
import os
import re
import requests

USERNAME = os.environ.get("USER_NAME", "notmekabir")
TOKEN = os.environ["GITHUB_TOKEN"]
ROOT = Path(__file__).resolve().parent

QUERY = """
query($login:String!, $from:DateTime!, $to:DateTime!, $cursor:String) {
  user(login:$login) {
    repositories(first:100, after:$cursor, ownerAffiliations:OWNER, privacy:PUBLIC) {
      totalCount
      nodes { stargazerCount }
      pageInfo { hasNextPage endCursor }
    }
    followers { totalCount }
    following { totalCount }
    contributionsCollection(from:$from, to:$to) {
      contributionCalendar { totalContributions }
    }
  }
}
"""

def github(query, variables):
    r = requests.post(
        "https://api.github.com/graphql",
        json={"query": query, "variables": variables},
        headers={"Authorization": f"Bearer {TOKEN}"},
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    if "errors" in data:
        raise RuntimeError(data["errors"])
    return data["data"]

def fetch_stats():
    now = datetime.now(timezone.utc)
    year_ago = now - timedelta(days=365)
    cursor = None
    repos = 0
    stars = 0
    first = True
    followers = following = contributions = 0

    while first or cursor:
        first = False
        data = github(QUERY, {
            "login": USERNAME,
            "from": year_ago.isoformat(),
            "to": now.isoformat(),
            "cursor": cursor,
        })["user"]

        if not repos:
            followers = data["followers"]["totalCount"]
            following = data["following"]["totalCount"]
            contributions = data["contributionsCollection"]["contributionCalendar"]["totalContributions"]

        page = data["repositories"]
        repos += len(page["nodes"])
        stars += sum(node["stargazerCount"] for node in page["nodes"])

        if page["pageInfo"]["hasNextPage"]:
            cursor = page["pageInfo"]["endCursor"]
        else:
            cursor = None

    return {
        "repo_data": repos,
        "star_data": stars,
        "follower_data": followers,
        "following_data": following,
        "contrib_data": contributions,
        "sync_data": now.strftime("%Y-%m-%d %H:%M UTC"),
    }

def replace_id(svg, element_id, value):
    pattern = rf'(<(?:text|tspan)[^>]*\bid="{re.escape(element_id)}"[^>]*>)(.*?)(</(?:text|tspan)>)'
    new_svg, count = re.subn(pattern, rf'\1{value}\3', svg, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f"Could not find SVG element: {element_id}")
    return new_svg

def update_file(path, stats):
    svg = path.read_text(encoding="utf-8")
    for key, value in stats.items():
        svg = replace_id(svg, key, str(value))
    path.write_text(svg, encoding="utf-8")

if __name__ == "__main__":
    stats = fetch_stats()
    for filename in ("assets/dark_mode.svg", "assets/light_mode.svg"):
        update_file(ROOT / filename, stats)
    print("Updated profile SVGs:", stats)
