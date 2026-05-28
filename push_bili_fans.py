#!/usr/bin/env python3
"""
Push a Bilibili follower count image to Zectrix e-paper devices.

The upload path intentionally matches the original stable script:
- requests.post
- multipart field name: images
- upload filename: photo.jpg
- upload MIME: image/jpeg
- pageId + dither form fields
"""

from __future__ import annotations

import os
import time
from datetime import datetime
from pathlib import Path

import matplotlib
import requests

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager


BILI_UID = os.environ.get("BILI_UID", "13131424")
ZECTRIX_MACS = [
    mac.strip()
    for mac in os.environ.get("ZECTRIX_MACS", "AC:A7:04:EA:62:30").split(",")
    if mac.strip()
]
ZECTRIX_API_KEY = os.environ.get("ZECTRIX_API_KEY", "")
TARGET_PAGE = os.environ.get("TARGET_PAGE", "1")
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", "/volume1/web/test"))

WIDTH = 400
HEIGHT = 300
DPI = 100

NUMBER_TOP_PX = 104
TIME_TOP_PX = 275
RIGHT_SAFE_X_PX = 386
MAX_NUMBER_WIDTH_PX = 396
MAX_NUMBER_HEIGHT_PX = 190

FONT_CANDIDATES = [
    Path(__file__).resolve().parent / "Arial Narrow Bold.ttf",
    Path("/System/Library/Fonts/Supplemental/Arial Narrow Bold.ttf"),
    Path("/Library/Fonts/Arial Narrow Bold.ttf"),
]


def load_number_font():
    for font_path in FONT_CANDIDATES:
        if font_path.exists():
            font_manager.fontManager.addfont(str(font_path))
            return font_manager.FontProperties(fname=str(font_path), weight="bold")

    return font_manager.FontProperties(family="Arial Narrow", weight="bold")


def fetch_bilibili_followers(uid: str) -> int:
    print(f"Fetching Bilibili followers for UID:{uid}...")
    url = f"https://api.bilibili.com/x/relation/stat?vmid={uid}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    data = response.json()
    if data.get("code") != 0:
        raise RuntimeError(f"Bilibili API returned error: {data}")

    followers = int(data["data"]["follower"])
    print(f"Followers: {followers:,}")
    return followers


def fit_number_font_size(fig, text_artist) -> int:
    for font_size in range(190, 20, -1):
        text_artist.set_fontsize(font_size)
        fig.canvas.draw()
        bbox = text_artist.get_window_extent(renderer=fig.canvas.get_renderer())
        if bbox.width <= MAX_NUMBER_WIDTH_PX and bbox.height <= MAX_NUMBER_HEIGHT_PX:
            return font_size
    return 20


def generate_follower_image(followers: int, output_path: Path) -> Path:
    font_props = load_number_font()
    fig = plt.figure(figsize=(WIDTH / DPI, HEIGHT / DPI), dpi=DPI)
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor("white")
    ax.axis("off")

    number_artist = ax.text(
        0.5,
        1 - NUMBER_TOP_PX / HEIGHT,
        f"{followers:,}",
        ha="center",
        va="top",
        color="black",
        fontproperties=font_props,
    )
    fit_number_font_size(fig, number_artist)

    ax.text(
        RIGHT_SAFE_X_PX / WIDTH,
        1 - TIME_TOP_PX / HEIGHT,
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        ha="right",
        va="top",
        color="black",
        fontsize=10,
        fontproperties=font_props,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        output_path,
        format="jpg",
        dpi=DPI,
        facecolor="white",
        pil_kwargs={"quality": 95},
    )
    plt.close(fig)
    print(f"Image written: {output_path}")
    return output_path


def push_to_zectrix(image_path: Path) -> None:
    if not ZECTRIX_API_KEY:
        raise RuntimeError("Missing required environment variable: ZECTRIX_API_KEY")

    headers = {"X-API-Key": ZECTRIX_API_KEY}
    data = {"pageId": TARGET_PAGE, "dither": "true"}
    image_bytes = image_path.read_bytes()

    for mac in ZECTRIX_MACS:
        api_url = f"https://cloud.zectrix.com/open/v1/devices/{mac}/display/image"
        last_text = ""

        for attempt in range(1, 4):
            files = {"images": ("photo.jpg", image_bytes, "image/jpeg")}
            print(f"Pushing to Zectrix {mac}, attempt {attempt}/3...")
            try:
                response = requests.post(
                    api_url,
                    headers=headers,
                    data=data,
                    files=files,
                    timeout=15,
                )
                last_text = response.text
                print(f"HTTP {response.status_code}: {response.text}")
                if response.status_code == 200 and '"code":0' in response.text.replace(" ", ""):
                    break
            except Exception as exc:
                last_text = str(exc)
                print(f"Push error: {exc}")

            if attempt < 3:
                time.sleep(2)
        else:
            raise RuntimeError(f"Push failed for {mac}: {last_text}")


def main() -> None:
    followers = fetch_bilibili_followers(BILI_UID)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = OUTPUT_DIR / f"bili_fans_{timestamp}.jpg"
    generate_follower_image(followers, output_path)
    push_to_zectrix(output_path)


if __name__ == "__main__":
    main()
