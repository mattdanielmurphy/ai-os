"""macOS Calendar Probe using EventKit with AppleScript fallback and TCC verification."""

import asyncio
import json
import logging
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple

logger = logging.getLogger("assistant.context_gate.calendar")

SWIFT_EVENTKIT_SCRIPT = """
import Foundation
import EventKit

let store = EKEventStore()
let status = EKEventStore.authorizationStatus(for: .event)

// Status rawValue: 0=notDetermined, 1=restricted, 2=denied, 3=fullAccess/authorized(older), 4=fullAccess(Sonoma/Sequoia)
if CommandLine.arguments.count > 1 && CommandLine.arguments[1] == "--check-tcc" {
    print("STATUS:\\(status.rawValue)")
    exit(0)
}

let cal = Calendar.current
let now = Date()
let startWindow = now.addingTimeInterval(-3600 * 2) // Past 2 hours to catch ongoing long events
let endWindow = now.addingTimeInterval(3600 * 12)  // Next 12 hours

let predicate = store.predicateForEvents(withStart: startWindow, end: endWindow, calendars: nil)
let events = store.events(matching: predicate)

struct EventItem: Codable {
    let title: String
    let start: String
    let end: String
    let isAllDay: Bool
}

let iso = ISO8601DateFormatter()
var list: [EventItem] = []

for ev in events {
    // Exclude Canadian Holidays and Siri Suggestions if needed, or include all
    let title = ev.title ?? "Untitled"
    let s = iso.string(from: ev.startDate)
    let e = iso.string(from: ev.endDate)
    list.append(EventItem(title: title, start: s, end: e, isAllDay: ev.isAllDay))
}

let encoder = JSONEncoder()
if let data = try? encoder.encode(list), let str = String(data: data, encoding: .utf8) {
    print(str)
} else {
    print("[]")
}
"""


@dataclass
class CalendarEvent:
    title: str
    start: datetime
    end: datetime
    is_all_day: bool


class CalendarProbe:
    def __init__(self):
        self._tcc_ok: Optional[bool] = None

    def check_tcc_permission(self) -> bool:
        """Runs a fast TCC health check and logs an explicit warning if permission is missing."""
        try:
            res = subprocess.run(
                ["swift", "-e", SWIFT_EVENTKIT_SCRIPT, "--", "--check-tcc"],
                capture_output=True,
                text=True,
                timeout=4,
            )
            if res.returncode == 0 and "STATUS:" in res.stdout:
                raw_val = int(res.stdout.split("STATUS:")[1].strip())
                # 3 or 4 indicates authorized / fullAccess
                self._tcc_ok = raw_val in (3, 4)
                if not self._tcc_ok:
                    logger.warning(
                        f"Calendar EventKit TCC permission NOT granted (status={raw_val}). "
                        "macOS may block calendar queries in background launchd!"
                    )
                return self._tcc_ok
        except Exception as e:
            logger.warning(f"Error checking Calendar TCC permission via Swift: {e}")

        # Fallback probe via osascript
        try:
            res = subprocess.run(
                ["osascript", "-e", 'tell application "Calendar" to return (count of calendars)'],
                capture_output=True,
                text=True,
                timeout=5,
            )
            self._tcc_ok = res.returncode == 0
            return self._tcc_ok
        except Exception as e:
            logger.warning(f"Error checking Calendar TCC permission via AppleScript: {e}")
            self._tcc_ok = False
            return False

    def fetch_events(self) -> List[CalendarEvent]:
        """Fetches calendar events in the active window."""
        # 1. Try Swift EventKit first (fast, direct)
        try:
            res = subprocess.run(
                ["swift", "-e", SWIFT_EVENTKIT_SCRIPT],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if res.returncode == 0 and res.stdout.strip():
                lines = res.stdout.strip().splitlines()
                # Last line should be the JSON
                json_line = lines[-1] if lines else "[]"
                data = json.loads(json_line)
                events: List[CalendarEvent] = []
                for item in data:
                    try:
                        s = datetime.fromisoformat(item["start"])
                        e = datetime.fromisoformat(item["end"])
                        events.append(
                            CalendarEvent(
                                title=item["title"],
                                start=s,
                                end=e,
                                is_all_day=bool(item.get("isAllDay", False)),
                            )
                        )
                    except Exception:
                        continue
                return events
        except Exception as e:
            logger.debug(f"Swift EventKit fetch failed, falling back to AppleScript: {e}")

        # 2. Fallback to AppleScript
        return self._fetch_events_osascript()

    def _fetch_events_osascript(self) -> List[CalendarEvent]:
        script = """
        tell application "Calendar"
            set now to current date
            set res to {}
            repeat with c in calendars
                tell c
                    set evs to (every event whose start date <= (now + 12 * hours) and end date >= (now - 2 * hours))
                    repeat with ev in evs
                        set res to res & (summary of ev & "|" & (start date of ev as string) & "|" & (end date of ev as string))
                    end repeat
                end tell
            end repeat
            return res
        end tell
        """
        try:
            res = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=6,
            )
            if res.returncode == 0 and res.stdout.strip():
                # AppleScript returns comma separated strings
                raw_items = [x.strip() for x in res.stdout.strip().split(", ")]
                events: List[CalendarEvent] = []
                for item in raw_items:
                    parts = item.split("|")
                    if len(parts) >= 3:
                        title = parts[0]
                        # Best effort parsing, otherwise placeholder
                        now = datetime.now(timezone.utc)
                        events.append(CalendarEvent(title=title, start=now, end=now + timedelta(hours=1), is_all_day=False))
                return events
        except Exception as e:
            logger.warning(f"AppleScript calendar query failed: {e}")

        return []

    def is_in_event_or_buffer(
        self, now: Optional[datetime] = None, buffer_minutes: int = 45
    ) -> Tuple[bool, Optional[CalendarEvent], Optional[datetime]]:
        """
        Checks if current time is within an event OR within the post-event routine buffer (e.g. +45 min).
        Returns:
            (in_event_or_buffer, blocking_event, resume_time)
        """
        if now is None:
            now = datetime.now(timezone.utc)

        events = self.fetch_events()
        for ev in events:
            # Skip all-day events unless explicitly wanted, as they shouldn't block the whole 24h
            if ev.is_all_day:
                continue

            event_start = ev.start
            event_end = ev.end
            buffer_end = event_end + timedelta(minutes=buffer_minutes)

            # Normalize timezones if needed
            if event_start.tzinfo is None and now.tzinfo is not None:
                event_start = event_start.replace(tzinfo=timezone.utc)
                event_end = event_end.replace(tzinfo=timezone.utc)
                buffer_end = buffer_end.replace(tzinfo=timezone.utc)
            elif event_start.tzinfo is not None and now.tzinfo is None:
                now = now.replace(tzinfo=timezone.utc)

            if event_start <= now <= buffer_end:
                logger.info(
                    f"Blocked by event '{ev.title}' (Ends {event_end.strftime('%H:%M')}, buffer until {buffer_end.strftime('%H:%M')})"
                )
                return True, ev, buffer_end

        return False, None, None
