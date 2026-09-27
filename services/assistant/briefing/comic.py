"""Fetch a rotating Calvin and Hobbes comic image from the GoComics archive."""

import asyncio
from datetime import date, timedelta
from html.parser import HTMLParser
from typing import Dict, Optional, Tuple
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


COMIC_RUN_START = date(1985, 11, 18)
COMIC_RUN_END = date(1995, 12, 31)


class _OpenGraphParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.values: Dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag != "meta":
            return
        values = dict(attrs)
        key = values.get("property") or values.get("name")
        if key in {"og:image", "og:title"} and values.get("content"):
            self.values[key] = values["content"]


def daily_calvin_hobbes_date(today: Optional[date] = None) -> date:
    """Select a different archive date each day and cycle through the strip's run."""
    current_day = today or date.today()
    run_length = (COMIC_RUN_END - COMIC_RUN_START).days + 1
    offset = (current_day - COMIC_RUN_START).days % run_length
    return COMIC_RUN_START + timedelta(days=offset)


def calvin_hobbes_page_url(comic_day: Optional[date] = None) -> str:
    selected_day = comic_day or daily_calvin_hobbes_date()
    return f"https://www.gocomics.com/calvinandhobbes/{selected_day:%Y/%m/%d}"


def _fetch_image_url(page_url: str) -> str:
    request = Request(
        page_url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-CA,en;q=0.9",
            "Referer": "https://www.gocomics.com/calvinandhobbes",
        },
    )
    with urlopen(request, timeout=12) as response:
        parser = _OpenGraphParser()
        parser.feed(response.read(2_000_000).decode("utf-8", "replace"))

    image_url = parser.values.get("og:image")
    parsed_url = urlsplit(image_url or "")
    if (
        parsed_url.scheme != "https"
        or parsed_url.hostname != "featureassets.gocomics.com"
        or not parsed_url.path.startswith("/assets/")
    ):
        raise ValueError("GoComics page did not provide a supported comic image URL")
    return image_url


async def fetch_daily_calvin_hobbes_comic() -> Tuple[str, str]:
    """Return the publisher-hosted image URL and its dated archive page URL."""
    page_url = calvin_hobbes_page_url()
    image_url = await asyncio.to_thread(_fetch_image_url, page_url)
    return image_url, page_url
