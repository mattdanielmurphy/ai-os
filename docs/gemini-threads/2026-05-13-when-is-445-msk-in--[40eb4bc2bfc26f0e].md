---
title: "when is 445 msk in est"
date: "2026-08-13"
source: "gemini.google.com"
conversation_id: "52e8a39c-600a-50da-82b8-9e6ea6947f9a"
url: ""
---

# when is 445 msk in est

> [!NOTE]
> Archived Gemini Thread: [when is 445 msk in est]() | Date: 2026-08-13

## User

when is 445 msk in est

---

## Gemini

from datetime import datetime, timedelta
import pytz

# Define timezones
msk_tz = pytz.timezone('Europe/Moscow')
est_tz = pytz.timezone('US/Eastern') # This handles EST/EDT automatically

# Target time in MSK on May 12, 2026 (as per system prompt date)
# The user sees the message on a website now, so it refers to the upcoming 04:45.
target_msk = msk_tz.localize(datetime(2026, 5, 12, 4, 45))

# Convert to Eastern Time
target_et = target_msk.astimezone(est_tz)

print(f"MSK Time: {target_msk.strftime('%Y-%m-%d %H:%M %Z')}")
print(f"ET Time: {target_et.strftime('%Y-%m-%d %H:%M %Z')}")



MSK Time: 2026-05-12 04:45 MSK
ET Time: 2026-05-11 21:45 EDT


04:45 MSK is 9:45 PM in Eastern Daylight Time (EDT), which is the current local time for the Eastern US and Canada.


Because Moscow is 7 hours ahead of the Eastern Time zone during the summer, this time falls on the previous evening.

---

## User

mdt rather. whatever edmonton is now

---

## Gemini

04:45 MSK is 7:45 PM in Mountain Daylight Time (MDT).


Since Edmonton is currently on MDT (UTC-6), the forum should be back online right about now, as it is currently 7:44 PM in your local time.

---

## User

kind of funny I only have to wait ONE minute. hope it's accurate

---

## Gemini

Perfect timing. Since it is currently 7:44 PM MDT, that 04:45 MSK mark should be hitting exactly now.


Give the page a refresh—if their maintenance schedule is tight, RuTracker should be loading the tracker results for you any second.

---

