from __future__ import annotations
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
USERNAME = os.getenv("USER_NAME", "notmekabir")
TOKEN = os.getenv("GITHUB_TOKEN", "")

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

def fetch_stats():
    if not TOKEN:
        return {
            "repositories": 0,
            "stars": 0,
            "followers": 0,
            "following": 0,
            "contributions": 0,
            "sync": "run GitHub Actions",
        }

    now = datetime.now(timezone.utc)
    start = now - timedelta(days=365)
    r = requests.post(
        "https://api.github.com/graphql",
        json={
            "query": QUERY,
            "variables": {
                "login": USERNAME,
                "from": start.isoformat(),
                "to": now.isoformat(),
            },
        },
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/json",
        },
        timeout=30,
    )
    r.raise_for_status()
    payload = r.json()
    if payload.get("errors"):
        raise RuntimeError(payload["errors"])

    u = payload["data"]["user"]
    return {
        "repositories": u["repositories"]["totalCount"],
        "stars": sum(n["stargazerCount"] for n in u["repositories"]["nodes"]),
        "followers": u["followers"]["totalCount"],
        "following": u["following"]["totalCount"],
        "contributions": u["contributionsCollection"]["contributionCalendar"]["totalContributions"],
        "sync": now.strftime("%Y-%m-%d %H:%M UTC"),
    }

def load_font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationMono-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf",
    ]
    for c in candidates:
        if Path(c).exists():
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()

def fit_image(img, w, h):
    img = img.convert("RGB")
    scale = max(w / img.width, h / img.height)
    nw, nh = int(img.width * scale), int(img.height * scale)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    x = (nw - w) // 2
    y = (nh - h) // 2
    return img.crop((x, y, x + w, y + h))

def make_card(light, s):
    W, H = 1400, 720

    BG = (245, 250, 248) if light else (2, 9, 7)
    PANEL = (255, 255, 255) if light else (7, 18, 14)
    PANEL2 = (237, 247, 243) if light else (10, 27, 21)
    TEXT = (19, 48, 39) if light else (212, 239, 228)
    MUTED = (91, 119, 107) if light else (81, 114, 101)
    GREEN = (5, 128, 84) if light else (52, 242, 164)
    CYAN = (16, 122, 151) if light else (88, 215, 255)
    PURPLE = (106, 67, 178) if light else (179, 140, 255)
    RED = (204, 59, 76) if light else (255, 102, 122)
    STROKE = (196, 220, 210) if light else (21, 53, 43)

    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)

    # Outer frame
    d.rounded_rectangle((8, 8, W - 8, H - 8), 22, fill=BG, outline=STROKE, width=2)
    d.rounded_rectangle((18, 18, W - 18, 62), 12, fill=PANEL2, outline=STROKE, width=1)

    # Terminal chrome
    d.ellipse((34, 30, 46, 42), fill=RED)
    d.ellipse((55, 30, 67, 42), fill=PURPLE)
    d.ellipse((76, 30, 88, 42), fill=GREEN)
    d.text((105, 27), "notmekabir@github:~", font=load_font(14), fill=MUTED)
    d.text((1168, 27), "PROFILE.PNG", font=load_font(12), fill=CYAN)
    d.text((1278, 27), "● LIVE", font=load_font(12), fill=MUTED)

    # Left panel
    d.rounded_rectangle((18, 74, 430, 694), 14, fill=PANEL, outline=STROKE, width=1)
    d.text((38, 95), "[ MATRIX_IDENTITY ]", font=load_font(12, True), fill=GREEN)
    d.line((38, 120, 410, 120), fill=STROKE, width=1)

    portrait = Image.open(ASSETS / "matrix-portrait.png")
    portrait = fit_image(portrait, 350, 540)
    im.paste(portrait, (45, 130))

    # Subtle scan lines, keeping the supplied image clearly visible.
    overlay = Image.new("RGBA", (350, 540), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for yy in range(0, 540, 8):
        od.line((0, yy, 350, yy), fill=(*GREEN, 18), width=1)
    im.paste(overlay, (45, 130), overlay)
    d.rounded_rectangle((45, 130, 395, 670), 10, outline=(*GREEN, 50), width=1)

    # Right panel
    x = 465
    d.text((x, 95), "$ whoami", font=load_font(15, True), fill=CYAN)
    d.text((x, 123), "Abhishek Kabiraj", font=load_font(29, True), fill=TEXT)
    d.text((x, 163), "@notmekabir · full-stack / custom software developer", font=load_font(14), fill=MUTED)
    d.line((x, 190, 1165, 190), fill=STROKE, width=1)

    def row(y, label, value):
        d.text((x, y), label, font=load_font(14), fill=MUTED)
        d.text((x + 150, y), value, font=load_font(14), fill=TEXT)

    d.text((x, 211), "SYSTEM", font=load_font(12, True), fill=GREEN)
    row(238, "role........", "developer / builder")
    row(265, "focus.......", "full-stack systems + custom tools")
    row(292, "mindset.....", "understand → build → break → refine")
    row(319, "principle...", "fit the tool to the problem")

    d.text((x, 351), "STACK", font=load_font(12, True), fill=GREEN)
    d.text((x, 378), "JavaScript · Python · C++ · HTML · CSS", font=load_font(14), fill=TEXT)
    d.text((x, 405), "Git · GitHub · VS Code · APIs · automation", font=load_font(14), fill=TEXT)

    d.text((x, 445), "GITHUB // LIVE TELEMETRY", font=load_font(12, True), fill=GREEN)

    row(474, "repositories..", f"{s['repositories']:,}")
    row(501, "stars........", f"{s['stars']:,}")
    row(528, "followers....", f"{s['followers']:,}")
    row(555, "following....", f"{s['following']:,}")
    row(582, "contributions.", f"{s['contributions']:,}")
    row(609, "last sync....", s["sync"])

    d.line((x, 635, 1165, 635), fill=STROKE, width=1)
    d.text((x, 649), "$ ./build-something-useful.sh", font=load_font(13), fill=MUTED)
    d.text((x + 308, 649), "Original ideas. Thoughtful engineering. Software with purpose.", font=load_font(13), fill=TEXT)

    out = ASSETS / ("profile-light.png" if light else "profile-dark.png")
    im.save(out, format="PNG", optimize=True)
    return out

if __name__ == "__main__":
    s = fetch_stats()
    print("Stats:", s)
    make_card(False, s)
    make_card(True, s)
    print("Generated profile-dark.png and profile-light.png")
