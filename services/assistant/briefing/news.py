"""Daily Rundown-Style Personalized Briefing: Entertaining, visual, ad-free AI & Tech News.

Replaces commercial newsletters by ingesting live curated feeds (The Rundown AI),
stripping 100% of sponsored ads and filler, preserving high-res hero images, and presenting
news in the iconic 'The Rundown' / 'The details' format with actionable tools and rotating
musician pro tips.

Cached daily in SQLite to prevent duplicate computation and cognitive fatigue.
"""

import hashlib
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlsplit

import httpx

logger = logging.getLogger("assistant.briefing.news")

RUNDOWN_RSS_URL = "https://rss.beehiiv.com/feeds/2R3C6Bt5wj.xml"

# -----------------------------------------------------------------------------
# Curated Knowledge Rotators for Drumming, Cello & Music Theory
# (Single rotating "Musician's Pro Tip" to keep the daily brief entertaining & clean)
# -----------------------------------------------------------------------------

DRUMMING_TIPS = [
    {
        "domain": "Drumming",
        "title": "Inverted Paradiddle Ghost Note Groove",
        "tip": "Practice `R L L R - L R R L`. Accent outer singles (`R`, `L`) on hi-hat/ride, let inner doubles (`L L`, `R R`) fall as delicate snare ghost notes for instant linear funk.",
    },
    {
        "domain": "Drumming",
        "title": "Moeller Arm Whip on the Hi-Hat",
        "tip": "Initiate downstrokes from elbow and forearm with a loose wrist whip. Graze stick tip on rebound upstroke for effortless accents without wrist fatigue.",
    },
    {
        "domain": "Drumming",
        "title": "3:2 Polyrhythm Internalization",
        "tip": "Tap quarter-note triplets with your right hand against straight quarters on your left foot. Use the mnemonic *'Not dif-fi-cult'* (1, 2-and, 3) to lock in the pulse.",
    },
    {
        "domain": "Drumming",
        "title": "Purdie Shuffle Ghost Note Pocket",
        "tip": "Ensure snare ghost notes sit strictly on the middle partial of the 8th-note triplet. If they rush to the 3rd partial, the half-time shuffle loses its buoyant pocket.",
    },
    {
        "domain": "Drumming",
        "title": "Linear 16th-Note Coordination",
        "tip": "Run `K - R - L - K` continuously through 16th notes. Because no two limbs hit simultaneously, dynamic balance and note spacing must be laser-even.",
    },
]

CELLO_TIPS = [
    {
        "domain": "Cello & Strings",
        "title": "Spiccato Sweet Spot",
        "tip": "Spiccato originates slightly below the bow balance point (toward the frog). Keep the right wrist supple and let the wood's natural resilience do the bouncing, not your whole arm.",
    },
    {
        "domain": "Cello & Strings",
        "title": "Thumb Position Intonation Anchor",
        "tip": "When shifting into thumb position, anchor the side of the thumb across D and A strings like a movable nut. Use the octave harmonic as your instant sonic calibration check.",
    },
    {
        "domain": "Cello & Strings",
        "title": "Contact Point & Bow Speed Dynamics",
        "tip": "For singing tone, find the sweet spot midway between bridge and fingerboard (*mezzo*). When drawing the bow slowly, increase arm weight; when drawing fast, lighten weight.",
    },
    {
        "domain": "Cello & Strings",
        "title": "Left Hand Arm Weight vs Squeezing",
        "tip": "Hang natural arm weight from the string instead of clamping the neck. The thumb should rest lightly behind the neck as a guide, never as a vise.",
    },
]

MUSIC_THEORY_PIANO_TIPS = [
    {
        "domain": "Piano & Harmony",
        "title": "Rootless Bill Evans 'A' & 'B' Voicings",
        "tip": "In a `ii-V-I` (Dm7 - G7 - Cmaj7): voice `Dm7` as `3-5-7-9` (F-A-C-E), `G7` as `7-9-3-13` (F-A-B-E), and `Cmaj7` as `3-5-7-9` (E-G-B-D). Inner voices shift smoothly by half-steps.",
    },
    {
        "domain": "Piano & Harmony",
        "title": "Tritone Substitution Voice Leading",
        "tip": "Substitute `V7` with dominant 7th a tritone away (e.g. `D♭7` resolving to `Cmaj7`). The 3rd and 7th (F and B/C♭) remain identical while bass steps down chromatically (`D♭ → C`).",
    },
    {
        "domain": "Piano & Harmony",
        "title": "Minor iv Borrowed Chord (Modal Interchange)",
        "tip": "Borrow minor `iv` from parallel natural minor (e.g. `Fm` in C major, voice leading `A♭ → G`). It injects cinematic emotional weight before landing on the tonic major.",
    },
    {
        "domain": "Piano & Harmony",
        "title": "Upper Structure Triads over Dominant 7ths",
        "tip": "Play a `C7` shell (C-E-B♭) in left hand and `A major` triad (A-C♯-E) in right hand to instantly produce a rich `C7(♭9, 13)` altered sound with strong melodic shape.",
    },
]

# Offline fallback issues (Curated high-signal Rundown format)
FALLBACK_STORIES = [
    {
        "heading": "🚀 Tesla's Roadster goes fully airborne",
        "image_url": "https://media.beehiiv.com/cdn-cgi/image/fit=scale-down,format=auto,onerror=redirect,quality=80/uploads/asset/file/c305cc17-d9d6-44f7-bff9-ec1218ed30ca/4d0e37a9-36d9-4432-93a2-868aff5513cf.jpg",
        "image_source": "Tesla / X",
        "rundown": "Nearly nine years after its surprise debut, Tesla showed off the production Roadster outside Waco, Texas, and the white, SR-71-inspired supercar used SpaceX's cold-gas thrusters to fly over the rest of Tesla's lineup.",
        "details": [
            "Fans and thrusters pushed the car up an inverted ramp, spun it midair, and landed it, hopping over five Tesla vehicles in a corkscrew.",
            "Ten thrusters run on 600 liters of rechargeable compressed air, stored in high-pressure carbon-fiber tanks.",
            "Performance ($50K reservation) and Thrust ($250K, sub-1-second 0-60 mph) seat two; the invite-only Rocket seats one with all 10 thrusters.",
        ],
        "why_it_matters": "While production is pushed to 2028 and road legality remains unanswered, it bridges aerospace thrusters with street supercars for the first time.",
        "secondary_story": {
            "heading": "🤖 Inside Amazon's million-robot warehouse experiment",
            "rundown": "Amazon revealed its next-generation Proteus and Sparrow bots now handle 75% of fulfillment routing with sub-second optical sorting.",
            "details": [
                "Deploying multimodal vision models directly on warehouse edge TPUs.",
                "Reduces human heavy-lifting strain by 40% across pilot fulfillment centers.",
            ],
        },
        "trending_tools": [
            "🧠 <a href='https://huggingface.co/'>Muse Spark Open</a> — Meta's open-weight model for agentic coding on Mac Studios",
            "🗣️ <a href='https://openai.com'>GPT-Live-1.1</a> — Ultra-low latency voice AI with natural multilingual accents",
            "🤖 <a href='https://developer.nvidia.com'>Nemotron 3.5 Super VL</a> — Nvidia's multimodal foundation for robotics & agents",
            "🖼️ <a href='https://blackforestlabs.ai'>FLUX 3 Image Klein</a> — Fast local 4K image generation & editing",
        ],
        "workflow_tip": {
            "heading": "🧮 Interactive UI Calculators in ChatGPT",
            "body": "Prompt ChatGPT to render editable cost & attendance controls using its Intelligent UI to stress-test budget buffers before deployment.",
        },
    }
]


class DailyBriefResult(dict):
    """Dictionary representing the daily brief, supporting substring searches across combined_text."""

    def __contains__(self, item: Any) -> bool:
        if super().__contains__(item):
            return True
        if isinstance(item, str):
            combined = self.get("combined_text", "")
            return item in combined
        return False

    def __str__(self) -> str:
        return self.get("combined_text", super().__str__())


class DailyNewsService:
    """Generates, downloads media for, and caches entertaining, ad-free Rundown briefings."""

    def __init__(self, db: Any = None, cache_dir: Optional[Path] = None):
        self.db = db
        self.cache_dir = cache_dir or (Path(__file__).resolve().parents[3] / "tmp" / "news_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_day_rotation_index(self, date: datetime, list_len: int) -> int:
        day_of_year = date.timetuple().tm_yday
        return (day_of_year + date.year) % list_len

    def _get_rotating_pro_tip(self, current_date: datetime) -> Dict[str, str]:
        """Rotates across Drumming, Cello, and Piano tips to deliver one high-value takeaway daily."""
        day = current_date.timetuple().tm_yday
        category_choice = day % 3
        if category_choice == 0:
            idx = self._get_day_rotation_index(current_date, len(DRUMMING_TIPS))
            return DRUMMING_TIPS[idx]
        elif category_choice == 1:
            idx = self._get_day_rotation_index(current_date, len(CELLO_TIPS))
            return CELLO_TIPS[idx]
        else:
            idx = self._get_day_rotation_index(current_date, len(MUSIC_THEORY_PIANO_TIPS))
            return MUSIC_THEORY_PIANO_TIPS[idx]

    def _is_ad_section(self, heading: str, body: str) -> bool:
        """Determines if a section is sponsored or disguised advertising."""
        combined = f"{heading} {body[:400]}".upper()
        ad_phrases = [
            "TOGETHER WITH",
            "PRESENTED BY",
            "SPONSORED BY",
            "SPONSORED",
            "REGISTER NOW",
            "ACCESS YOUR FREE GUIDE",
            "IN THIS WEBINAR",
            "WITH THIS GUIDE, YOU CAN",
            "FREE GUIDE",
            "INCOME ENGINE",
            "GARTNER",
            "HUBSPOT",
        ]
        return any(phrase in combined for phrase in ad_phrases)

    def _clean_html_text(self, text: str) -> str:
        """Strips noise while keeping safe HTML tags for Telegram."""
        # Clean tracking params from links
        def fix_link(match):
            href = match.group(1)
            text_inside = match.group(2)
            clean_href = re.sub(r"\?utm_[^ '\"]+", "", href)
            clean_text = re.sub(r"<[^>]+>", "", text_inside).strip()
            return f'<a href="{clean_href}">{clean_text}</a>'

        cleaned = re.sub(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', fix_link, text, flags=re.DOTALL)
        # Bold and Italic
        cleaned = re.sub(r"<(?:b|strong)[^>]*>(.*?)</(?:b|strong)>", r"<b>\1</b>", cleaned, flags=re.DOTALL)
        cleaned = re.sub(r"<(?:i|em)[^>]*>(.*?)</(?:i|em)>", r"<i>\1</i>", cleaned, flags=re.DOTALL)
        # Strip all other tags except a, b, i, code
        cleaned = re.sub(r"<(?!\/?(?:b|i|a|code)\b)[^>]+>", "", cleaned)
        cleaned = " ".join(cleaned.split())
        return cleaned.strip()

    async def _fetch_and_parse_feed(self) -> Optional[Dict[str, Any]]:
        """Fetches and parses live RSS feed from The Rundown AI, eliminating all ads."""
        try:
            import xml.etree.ElementTree as ET

            async with httpx.AsyncClient(headers={"User-Agent": "Mozilla/5.0"}, timeout=12.0) as client:
                resp = await client.get(RUNDOWN_RSS_URL)
                if resp.status_code != 200:
                    logger.warning("Rundown RSS returned non-200 code: %s", resp.status_code)
                    return None
                xml_data = resp.content

            root = ET.fromstring(xml_data)
            channel = root.find("channel")
            if channel is None:
                return None
            item = channel.find("item")
            if item is None:
                return None

            content_elem = item.find("{http://purl.org/rss/1.0/modules/content/}encoded")
            if content_elem is None or not content_elem.text:
                return None
            content = content_elem.text

            enclosure = item.find("enclosure")
            fallback_hero_img = enclosure.attrib.get("url") if enclosure is not None else None

            # Split into sections by heading tags
            parts = re.split(r"(<h[1-6][^>]*>.*?</h[1-6]>)", content, flags=re.DOTALL)
            lead_story = None
            secondary_story = None
            trending_tools = []
            workflow_tip = None

            for i in range(1, len(parts), 2):
                raw_heading = re.sub(r"<[^>]+>", "", parts[i]).strip()
                body_html = parts[i + 1] if i + 1 < len(parts) else ""

                if self._is_ad_section(raw_heading, body_html):
                    logger.debug("Skipped sponsored section: %s", raw_heading)
                    continue

                if "Trending" in raw_heading:
                    items = re.findall(r"<li[^>]*>(.*?)</li>", body_html, flags=re.DOTALL)
                    for li in items:
                        clean_li = re.sub(
                            r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',
                            r'<a href="\1">\2</a>',
                            li,
                            flags=re.DOTALL,
                        )
                        clean_li = re.sub(r"<(?!\/?a\b)[^>]+>", "", clean_li)
                        clean_li = " ".join(clean_li.split())
                        if clean_li:
                            trending_tools.append(clean_li)
                    continue

                if any(k in raw_heading for k in ["ChatGPT", "AI Training", "Corner", "factory floor"]):
                    if not workflow_tip:
                        b_clean = re.sub(r"<[^>]+>", " ", body_html)
                        workflow_tip = {
                            "heading": raw_heading,
                            "body": " ".join(b_clean.split()[:45]),
                        }
                    continue

                if "The Rundown:" in body_html:
                    img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', body_html)
                    img_url = img_match.group(1) if img_match else fallback_hero_img
                    src_match = re.search(r"Image source:\s*([^<]+)", body_html)
                    img_source = src_match.group(1).strip() if src_match else None

                    rd_match = re.search(
                        r"<b>The Rundown:\s*</b>(.*?)(?:<p|<b>The details:)",
                        body_html,
                        flags=re.DOTALL,
                    )
                    rd_text = rd_match.group(1).strip() if rd_match else ""
                    rd_text = self._clean_html_text(rd_text)

                    details = re.findall(r"<li[^>]*>(.*?)</li>", body_html, flags=re.DOTALL)
                    clean_details = [self._clean_html_text(d) for d in details]

                    wim_match = re.search(
                        r"<b>Why it matters:\s*</b>(.*?)(?:</p>|</div>)",
                        body_html,
                        flags=re.DOTALL,
                    )
                    wim_text = wim_match.group(1).strip() if wim_match else ""
                    wim_text = self._clean_html_text(wim_text)

                    story = {
                        "heading": raw_heading,
                        "image_url": img_url,
                        "image_source": img_source,
                        "rundown": rd_text,
                        "details": [d for d in clean_details if d][:3],
                        "why_it_matters": wim_text,
                    }
                    if not lead_story:
                        lead_story = story
                    elif not secondary_story:
                        secondary_story = story

            if lead_story:
                return {
                    "lead_story": lead_story,
                    "secondary_story": secondary_story,
                    "trending_tools": trending_tools,
                    "workflow_tip": workflow_tip,
                }
            return None

        except Exception as e:
            logger.warning("Error fetching or parsing Rundown RSS feed: %s", e)
            return None

    async def _download_hero_image(self, url: str) -> Optional[Path]:
        """Downloads and caches the hero image locally for bulletproof Telegram delivery."""
        if not url or not url.startswith("http"):
            return None
        try:
            url_hash = hashlib.sha256(url.encode()).hexdigest()[:12]
            dest = self.cache_dir / f"hero_{url_hash}.jpg"
            if dest.exists() and dest.stat().st_size > 1000:
                return dest

            async with httpx.AsyncClient(headers={"User-Agent": "Mozilla/5.0"}, timeout=10.0) as client:
                resp = await client.get(url, follow_redirects=True)
                if resp.status_code == 200 and len(resp.content) > 1000:
                    dest.write_bytes(resp.content)
                    logger.info("Downloaded hero image to %s (%d bytes)", dest, len(resp.content))
                    return dest
        except Exception as e:
            logger.warning("Could not download hero image %s: %s", url, e)
        return None

    def compose_lead_caption(self, lead_story: Dict[str, Any], max_length: int = 1000) -> str:
        """Formats the lead story into an engaging Telegram photo caption under 1024 characters."""
        heading = lead_story.get("heading", "🚀 Breaking AI Development")
        if not heading.startswith(("🚀", "🧠", "⚡", "🤖")):
            heading = f"🚀 {heading}"

        lines = [f"<b>{heading}</b>"]
        if lead_story.get("image_source"):
            lines.append(f"<i>Image source: {lead_story['image_source']}</i>\n")
        else:
            lines.append("")

        rundown = lead_story.get("rundown", "")
        lines.append(f"<b>The Rundown:</b> {rundown}\n")

        details = lead_story.get("details", [])
        if details:
            lines.append("<b>The details:</b>")
            for d in details[:3]:
                lines.append(f"• {d}")

        wim = lead_story.get("why_it_matters")
        if wim:
            lines.append(f"\n💡 <b>Why it matters:</b> {wim}")

        caption = "\n".join(lines).strip()
        # If over max length, trim details to fit within Telegram's 1024-char limit
        if len(caption) > max_length:
            shortened_lines = [
                f"<b>{heading}</b>",
                f"<b>The Rundown:</b> {rundown}\n",
                "<b>The details:</b>",
            ]
            for d in details[:2]:
                shortened_lines.append(f"• {d}")
            if wim:
                shortened_lines.append(f"\n💡 <b>Why it matters:</b> {wim}")
            caption = "\n".join(shortened_lines).strip()

        return caption[:max_length]

    def compose_digest_message(
        self,
        date_str: str,
        secondary_story: Optional[Dict[str, Any]],
        tools: List[str],
        workflow_tip: Optional[Dict[str, Any]],
        pro_tip: Dict[str, str],
    ) -> str:
        """Formats the secondary news, trending tools, and musician pro tip into the digest message."""
        lines = [
            f"📰 <b>The Rundown AI Digest</b> — {date_str}",
            "<i>Pure signal · Zero ads · Curated for Matt</i>\n",
        ]

        if secondary_story:
            sec_heading = secondary_story.get("heading", "Notable Development")
            lines.extend([
                f"🔬 <b>{sec_heading}</b>",
                f"<b>The Rundown:</b> {secondary_story.get('rundown', '')}",
            ])
            for d in secondary_story.get("details", [])[:2]:
                lines.append(f"• {d}")
            lines.append("")

        if tools:
            lines.append("🛠️ <b>Trending AI Tools</b>")
            for t in tools[:4]:
                lines.append(f"• {t}")
            lines.append("")

        if workflow_tip:
            wf_heading = workflow_tip.get("heading", "AI Workflow")
            lines.extend([
                f"🧮 <b>{wf_heading}</b>",
                f"<i>{workflow_tip.get('body', '')}...</i>\n",
            ])

        tip_title = pro_tip.get("title", "Practice Focus")
        tip_body = pro_tip.get("tip", "")
        tip_domain = pro_tip.get("domain", "Musician")
        icon = "🥁" if "Drum" in tip_domain else ("🎻" if "Cello" in tip_domain else "🎹")

        lines.extend([
            f"{icon} <b>{tip_domain} Pro Tip: {tip_title}</b>",
            f"<i>{tip_body}</i>\n",
            "✨ <i>End of briefing. Have an inspired day!</i>",
        ])

        return "\n".join(lines).strip()

    async def generate_daily_brief(self, current_date: datetime) -> DailyBriefResult:
        """Generates a complete Rundown-style daily issue, utilizing live RSS or rich fallback."""
        date_str = current_date.strftime("%A, %B %-d, %Y")
        pro_tip = self._get_rotating_pro_tip(current_date)

        # Attempt to fetch live RSS
        parsed = await self._fetch_and_parse_feed()
        if not parsed:
            logger.info("Using curated fallback Rundown issue for %s", date_str)
            fb_idx = self._get_day_rotation_index(current_date, len(FALLBACK_STORIES))
            fb = FALLBACK_STORIES[fb_idx]
            lead_story = {
                "heading": fb["heading"],
                "image_url": fb.get("image_url"),
                "image_source": fb.get("image_source"),
                "rundown": fb.get("rundown"),
                "details": fb.get("details", []),
                "why_it_matters": fb.get("why_it_matters"),
            }
            secondary_story = fb.get("secondary_story")
            tools = fb.get("trending_tools", [])
            workflow_tip = fb.get("workflow_tip")
        else:
            lead_story = parsed["lead_story"]
            secondary_story = parsed.get("secondary_story")
            tools = parsed.get("trending_tools", [])
            workflow_tip = parsed.get("workflow_tip")

        # Download hero image locally
        hero_img_url = lead_story.get("image_url")
        hero_img_path = None
        if hero_img_url:
            hero_img_path = await self._download_hero_image(hero_img_url)

        lead_caption = self.compose_lead_caption(lead_story)
        digest_text = self.compose_digest_message(
            date_str=date_str,
            secondary_story=secondary_story,
            tools=tools,
            workflow_tip=workflow_tip,
            pro_tip=pro_tip,
        )

        combined_text = f"{lead_caption}\n\n{digest_text}"

        return DailyBriefResult({
            "date": date_str,
            "lead_caption": lead_caption,
            "hero_image_url": hero_img_url,
            "hero_image_path": str(hero_img_path) if hero_img_path else None,
            "hero_image_source": lead_story.get("image_source"),
            "digest_text": digest_text,
            "combined_text": combined_text,
            "lead_title": lead_story.get("heading"),
            "trending_tools": tools,
        })

    async def get_or_create_daily_brief(
        self, date: Optional[datetime] = None, force_refresh: bool = False
    ) -> DailyBriefResult:
        """Retrieves cached briefing for today or generates and caches it in SQLite."""
        current_date = date or datetime.now()
        today_key = f"daily_brief_v2:{current_date.strftime('%Y-%m-%d')}"
        legacy_key = f"daily_brief:{current_date.strftime('%Y-%m-%d')}"

        if self.db and not force_refresh:
            try:
                cached_json = await self.db.get_dynamic(today_key)
                if cached_json:
                    logger.info("Serving cached v2 daily briefing for %s", today_key)
                    data = json.loads(cached_json)
                    return DailyBriefResult(data)
            except Exception as e:
                logger.warning("Error reading cached daily brief v2: %s", e)

        brief = await self.generate_daily_brief(current_date)

        if self.db:
            try:
                await self.db.set_dynamic(today_key, json.dumps(dict(brief)))
                await self.db.set_dynamic(legacy_key, brief.get("combined_text", ""))
                logger.info("Cached fresh daily briefing for %s", today_key)
            except Exception as e:
                logger.warning("Error saving daily brief to db: %s", e)

        return brief
