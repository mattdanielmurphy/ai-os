"""Fetch Cyanide and Happiness comic images from Explosm."""

import asyncio
import json
import logging
import re
from html.parser import HTMLParser
from typing import Optional, Tuple
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

logger = logging.getLogger("assistant.briefing.comic")

EXPLOSM_BASE_URL = "https://explosm.net"
EXPLOSM_LATEST_URL = "https://explosm.net/comics/latest"
ALLOWED_COMIC_HOSTS = {"static.explosm.net", "files.explosm.net"}


class _ExplosmComicParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.image_url: Optional[str] = None
        self.og_image: Optional[str] = None

    def handle_starttag(self, tag: str, attrs) -> None:
        attrs_dict = dict(attrs)
        if tag == "meta":
            key = attrs_dict.get("property") or attrs_dict.get("name")
            if key == "og:image" and attrs_dict.get("content"):
                self.og_image = attrs_dict["content"]
        elif tag == "img":
            src = attrs_dict.get("src")
            if not src:
                return
            parsed = urlsplit(src)
            if parsed.hostname in ALLOWED_COMIC_HOSTS:
                # The primary comic strip has data-nimg="fill"
                if attrs_dict.get("data-nimg") == "fill" and not self.image_url:
                    self.image_url = src


def cyanide_and_happiness_page_url(slug_or_url: Optional[str] = None) -> str:
    """Return the Explosm comic page URL."""
    if not slug_or_url:
        return EXPLOSM_LATEST_URL
    clean = str(slug_or_url).strip()
    if clean.startswith("http://") or clean.startswith("https://"):
        return clean
    return f"{EXPLOSM_BASE_URL}/comics/{clean.lstrip('/')}"


def _fetch_comic_image_and_page(target_url: str) -> Tuple[str, str]:
    """Fetch the page and extract both the comic image URL and canonical page URL."""
    request = Request(
        target_url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-CA,en;q=0.9",
            "Referer": EXPLOSM_BASE_URL,
        },
    )
    with urlopen(request, timeout=12) as response:
        canonical_page_url = response.geturl()
        html_content = response.read(2_000_000).decode("utf-8", "replace")

    parser = _ExplosmComicParser()
    parser.feed(html_content)
    image_url = parser.image_url

    # Fallback 1: Extract from Next.js state (__NEXT_DATA__)
    if not image_url:
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html_content)
        if match:
            try:
                data = json.loads(match.group(1))
                urql = data.get("props", {}).get("pageProps", {}).get("urqlState", {})
                for entry in urql.values():
                    try:
                        inner = json.loads(entry.get("data", "{}"))
                        if "comic" in inner and isinstance(inner["comic"], dict):
                            details = inner["comic"].get("comicDetails", {})
                            bucket = details.get("comicimgstaticbucketurl") or {}
                            cand = bucket.get("mediaItemUrl") or details.get("comicimgurl")
                            if cand:
                                if cand.startswith("http://") or cand.startswith("https://"):
                                    image_url = cand
                                else:
                                    image_url = f"https://files.explosm.net/comics/{cand.lstrip('/')}"
                                break
                    except Exception:
                        pass
            except Exception:
                pass

    # Fallback 2: OpenGraph image tag if hosted on an allowed domain
    if not image_url and parser.og_image:
        parsed_og = urlsplit(parser.og_image)
        if parsed_og.hostname in ALLOWED_COMIC_HOSTS:
            image_url = parser.og_image

    parsed_url = urlsplit(image_url or "")
    if (
        parsed_url.scheme != "https"
        or parsed_url.hostname not in ALLOWED_COMIC_HOSTS
        or not parsed_url.path
    ):
        raise ValueError("Explosm page did not provide a supported Cyanide and Happiness comic image URL")

    return image_url, canonical_page_url


async def fetch_daily_cyanide_and_happiness_comic(
    page_url: Optional[str] = None,
) -> Tuple[str, str]:
    """Return the publisher-hosted image URL and its Explosm archive page URL."""
    target = page_url or cyanide_and_happiness_page_url()
    return await asyncio.to_thread(_fetch_comic_image_and_page, target)


# Compatibility aliases
fetch_daily_comic = fetch_daily_cyanide_and_happiness_comic
calvin_hobbes_page_url = cyanide_and_happiness_page_url
fetch_daily_calvin_hobbes_comic = fetch_daily_cyanide_and_happiness_comic
