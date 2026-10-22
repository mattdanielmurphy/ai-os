#!/usr/bin/env python3
"""Control Matt's Philips Hue lights through the local Hue Bridge (CLIP v2 API).

The app key lives in the macOS Keychain (service "ai-os-hue"), never in files.

  hue.py link                           pair with the bridge (press its button within 10 min)
  hue.py status                         rooms, lights, on/brightness/colour temp
  hue.py set <room|light|all> [--on|--off] [--bri 0-100] [--kelvin 2000-6500] [--fade SECONDS]
  hue.py automations                    list bridge automations (behaviors)
  hue.py automation <name> --on|--off   enable/disable an automation
  hue.py schedule apply                 push config/hue_schedule.json to the bridge and activate it
  hue.py schedule show                  print tonight's times, the curve and any shift plan
  hue.py schedule daily                 (launchd, noon) re-apply only if tonight's times changed
  hue.py shift --up-by "YYYY-MM-DD HH:MM" --title X [--dry-run]   gradual sleep shift for an early event
  hue.py shift --cancel                 back to the normal schedule
  hue.py retime --bed HH:MM --wake HH:MM [--from-bed HH:MM --from-wake HH:MM] [--nights N] [--reminders]
                                        new normal times, eased in over N nights
  hue.py raw GET|PUT|POST|DELETE <resource path> [json]   escape hatch for anything else
"""
import argparse
import datetime
import json
import socket
import ssl
import subprocess
import sys
import urllib.request
from pathlib import Path

BRIDGE_ID = "001788fffe6b2ad2"
KEYCHAIN_SERVICE = "ai-os-hue"
CONFIG = Path(__file__).resolve().parent.parent / "config" / "hue_schedule.json"

# The bridge uses a self-signed cert issued by Philips/Signify; we only ever talk to the LAN IP.
_CTX = ssl.create_default_context()
_CTX.check_hostname = False
_CTX.verify_mode = ssl.CERT_NONE


def bridge_ip():
    cache = Path.home() / ".cache" / "ai-os-hue-ip"
    if cache.exists():
        ip = cache.read_text().strip()
        try:
            socket.create_connection((ip, 443), timeout=2).close()
            return ip
        except OSError:
            pass
    with urllib.request.urlopen("https://discovery.meethue.com/", timeout=8) as r:
        bridges = json.load(r)
    ip = next(b["internalipaddress"] for b in bridges if b["id"].lower() == BRIDGE_ID)
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(ip)
    return ip


def app_key():
    try:
        return subprocess.run(
            ["security", "find-generic-password", "-s", KEYCHAIN_SERVICE, "-w"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
    except subprocess.CalledProcessError:
        sys.exit("No Hue key in Keychain (service ai-os-hue). Run: hue.py link, then press the bridge button.")


def cmd_link(_):
    """Wait up to 10 min for the bridge's link button, then store the new app key in Keychain."""
    import time
    body = json.dumps({"devicetype": "ai-os#matt-mac", "generateclientkey": True}).encode()
    for _ in range(300):
        with urllib.request.urlopen(urllib.request.Request(f"https://{bridge_ip()}/api", data=body), context=_CTX, timeout=5) as r:
            res = json.load(r)[0]
        if "success" in res:
            subprocess.run(["security", "add-generic-password", "-U", "-a", "hue-bridge", "-s", KEYCHAIN_SERVICE,
                            "-w", res["success"]["username"]], check=True)
            print("Linked; key saved to Keychain.")
            return
        time.sleep(2)
    sys.exit("Link button wasn't pressed in time.")


def api(method, path, body=None):
    """CLIP v2 call. path like 'light' or 'light/<id>'."""
    req = urllib.request.Request(
        f"https://{bridge_ip()}/clip/v2/resource/{path}",
        method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"hue-application-key": app_key(), "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, context=_CTX, timeout=10) as r:
            out = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"{method} {path} failed ({e.code}): {e.read().decode()}")
    if out.get("errors"):
        sys.exit(f"{method} {path} errors: {out['errors']}")
    return out["data"]


def name_of(res):
    return res.get("metadata", {}).get("name", res["id"])


def kelvin_to_mirek(k):
    return max(153, min(500, round(1_000_000 / k)))


def find_target(target):
    """Return (rtype, id) for a room/zone/light name, or the bridge-wide group for 'all'."""
    t = target.lower()
    if t == "all":
        home = api("GET", "bridge_home")[0]
        gl = next(s for s in home["services"] if s["rtype"] == "grouped_light")
        return "grouped_light", gl["rid"]
    for rtype in ("room", "zone"):
        for g in api("GET", rtype):
            if name_of(g).lower() == t:
                gl = next(s for s in g["services"] if s["rtype"] == "grouped_light")
                return "grouped_light", gl["rid"]
    for light in api("GET", "light"):
        if name_of(light).lower() == t:
            return "light", light["id"]
    sys.exit(f"No room, zone or light named {target!r}. Try: hue.py status")


def cmd_status(_):
    lights = {l["id"]: l for l in api("GET", "light")}
    devices = {d["id"]: d for d in api("GET", "device")}
    light_of_device = {
        s["rid"]: d for d in devices.values() for s in d["services"] if s["rtype"] == "light"
    }
    shown = set()
    for room in api("GET", "room") + api("GET", "zone"):
        print(f"[{name_of(room)}]")
        for child in room["children"]:
            ids = [child["rid"]] if child["rtype"] == "light" else [
                s["rid"] for s in devices.get(child["rid"], {}).get("services", []) if s["rtype"] == "light"
            ]
            for lid in ids:
                if lid in lights:
                    print("  " + fmt_light(lights[lid], light_of_device))
                    shown.add(lid)
    rest = [l for lid, l in lights.items() if lid not in shown]
    if rest:
        print("[no room]")
        for l in rest:
            print("  " + fmt_light(l, light_of_device))


def fmt_light(l, light_of_device):
    on = l["on"]["on"]
    bri = l.get("dimming", {}).get("brightness")
    mirek = l.get("color_temperature", {}).get("mirek")
    temp = f"{round(1_000_000 / mirek)}K" if mirek else ("colour" if "color" in l else "white")
    state = f"on {bri:.0f}% {temp}" if on else "off"
    return f"{name_of(light_of_device.get(l['id'], l)):<24} {state}"


def cmd_set(a):
    rtype, rid = find_target(a.target)
    body = {}
    if a.on or a.bri is not None:
        body["on"] = {"on": True}
    if a.off:
        body["on"] = {"on": False}
    if a.bri is not None:
        body["dimming"] = {"brightness": a.bri}
    if a.kelvin:
        body["color_temperature"] = {"mirek": kelvin_to_mirek(a.kelvin)}
    if a.fade is not None:
        body["dynamics"] = {"duration": int(a.fade * 1000)}
    api("PUT", f"{rtype}/{rid}", body)
    print(f"Set {a.target}: {body}")


def cmd_automations(_):
    scripts = {s["id"]: s.get("metadata", {}).get("name", "?") for s in api("GET", "behavior_script")}
    for b in api("GET", "behavior_instance"):
        print(f"{'ON ' if b['enabled'] else 'off'}  {b['metadata']['name']:<32} ({scripts.get(b['script_id'], b['script_id'])})")


def cmd_automation(a):
    matches = [b for b in api("GET", "behavior_instance") if b["metadata"]["name"].lower() == a.name.lower()]
    if not matches:
        sys.exit(f"No automation named {a.name!r}. Try: hue.py automations")
    for b in matches:
        api("PUT", f"behavior_instance/{b['id']}", {"enabled": bool(a.on)})
        print(f"{'Enabled' if a.on else 'Disabled'} {b['metadata']['name']}")


SCHEDULE_SCRIPT = "7238c707-8693-4f19-9095-ccdc1444d228"  # bridge's built-in "Schedule" behavior
EVERY_DAY = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
SCENE_PREFIX = "ai-os "
APPLIED = Path.home() / ".cache" / "ai-os-hue-applied.json"
BED_AUTOMATION = "Night Time"  # Matt's own "lights off" schedule; moved with bedtime
WAKE_AUTOMATION = "Wake up"  # Matt's sunrise routine; moved with wake time


def mins(s):
    h, m = s.split(":")
    return int(h) * 60 + int(m)


def clock(m):
    m = round(m) % 1440
    return f"{m // 60:02d}:{m % 60:02d}"


def hhmm(m):
    m = round(m) % 1440
    return {"hour": m // 60, "minute": m % 60}


def night_of(now=None):
    """The night a run belongs to: before noon still counts as last night."""
    now = now or datetime.datetime.now()
    return (now - datetime.timedelta(hours=12)).date()


def anchors(cfg, night):
    """(bedtime tonight, wake next morning) in minutes, plus a note, for the night starting on `night`.

    Bedtimes live in 12:00-36:00 so that after-midnight bedtimes interpolate correctly.
    """
    bed = mins(cfg["bedtime"])
    bed += 1440 if bed < 720 else 0
    wake = mins(cfg["wake"])
    note = "normal"
    ramp = cfg.get("ramp")
    if ramp:  # easing from old times to new normal ones, the same step each night
        k = (night - datetime.date.fromisoformat(ramp["start"])).days
        if 0 <= k < ramp["nights"]:
            r_bed = mins(ramp["from_bed"])
            r_bed += 1440 if r_bed < 720 else 0
            frac = k / ramp["nights"]
            bed = round((r_bed + (bed - r_bed) * frac) / 5) * 5
            wake = round((mins(ramp["from_wake"]) + (wake - mins(ramp["from_wake"])) * frac) / 5) * 5
            note = f"easing to {cfg['bedtime']}/{cfg['wake']}, night {k + 1}/{ramp['nights']}"
    shift = cfg.get("shift")
    if not shift:
        return bed, wake, note
    start = datetime.date.fromisoformat(shift["start"])
    event = datetime.date.fromisoformat(shift["event_date"])
    nights = (event - start).days
    k = (night - start).days + 1  # 1 = first shifted night, nights = the night before the event
    if not 1 <= k <= nights:
        return bed, wake, note
    t_wake = mins(shift["wake"])
    t_bed = t_wake - cfg["shift_sleep_hours"] * 60
    t_bed += 1440 if t_bed < 720 else 0
    frac = k / nights
    step = lambda a, b: round((a + (b - a) * frac) / 5) * 5
    return step(bed, t_bed), step(wake, t_wake), f"shift night {k}/{nights} for {shift['title']}"


def shift_plan(cfg):
    shift = cfg["shift"]
    start = datetime.date.fromisoformat(shift["start"])
    nights = (datetime.date.fromisoformat(shift["event_date"]) - start).days
    for k in range(nights):
        night = start + datetime.timedelta(days=k)
        bed, wake, _ = anchors(cfg, night)
        yield night, bed, wake


def slot_actions(lights, slot):
    actions = []
    for l in lights:
        action = {"on": {"on": True}, "dimming": {"brightness": float(slot["bri"])}}
        ct = l.get("color_temperature", {}).get("mirek_schema")
        if ct and slot.get("kelvin"):
            mirek = round(1_000_000 / slot["kelvin"])
            action["color_temperature"] = {"mirek": max(ct["mirek_minimum"], min(ct["mirek_maximum"], mirek))}
        actions.append({"target": {"rid": l["id"], "rtype": "light"}, "action": action})
    return actions


def build_slots(cfg, bed, wake):
    slots = [{"at": wake - cfg["day_starts_before_wake"], **cfg["day"]}]
    slots += [{"at": bed - e["before_bed"], "bri": e["bri"], "kelvin": e.get("kelvin")} for e in cfg["evening"]]
    return sorted(slots, key=lambda s: round(s["at"]) % 1440)


def move_automation(name, when, mutate):
    for b in api("GET", "behavior_instance"):
        if b["metadata"]["name"] == name:
            conf = b["configuration"]
            mutate(conf, hhmm(when))
            api("PUT", f"behavior_instance/{b['id']}", {"configuration": conf})
            return True
    print(f"(no automation named {name!r}; skipped)")
    return False


def set_start_at(conf, t):
    conf["when_extended"]["start_at"]["time_point"]["time"] = t


def set_wake_time(conf, t):
    conf["when"]["time_point"]["time"] = t


def apply_schedule(cfg, night, activate):
    home = api("GET", "bridge_home")[0]
    group = {"rid": home["id"], "rtype": "bridge_home"}
    name = cfg["name"]
    bed, wake, note = anchors(cfg, night)

    # Re-applying replaces everything this command made before, so the config file stays the source of truth.
    was_active = False
    for b in api("GET", "behavior_instance"):
        if b["metadata"]["name"] == f"{SCENE_PREFIX}{name}":
            api("DELETE", f"behavior_instance/{b['id']}")
    for s in api("GET", "smart_scene"):
        if name_of(s) == name:
            was_active |= s["state"] == "active"
            api("DELETE", f"smart_scene/{s['id']}")
    for s in api("GET", "scene"):
        if name_of(s).startswith(SCENE_PREFIX):
            api("DELETE", f"scene/{s['id']}")

    lights = api("GET", "light")
    timeslots = []
    for slot in build_slots(cfg, bed, wake):
        scene = api("POST", "scene", {
            "metadata": {"name": f"{SCENE_PREFIX}{clock(slot['at'])}"},
            "group": group,
            "actions": slot_actions(lights, slot),
        })[0]
        timeslots.append({
            "start_time": {"kind": "time", "time": {**hhmm(slot["at"]), "second": 0}},
            "target": {"rid": scene["rid"], "rtype": "scene"},
        })
    smart = api("POST", "smart_scene", {
        "metadata": {"name": name},
        "group": group,
        "week_timeslots": [{"timeslots": timeslots, "recurrence": EVERY_DAY}],
        "transition_duration": cfg["fade_minutes"] * 60_000,
    })[0]
    # Any manual change or other scene (e.g. the Wake up routine) deactivates a smart scene, so re-arm it daily.
    api("POST", "behavior_instance", {
        "script_id": SCHEDULE_SCRIPT,
        "enabled": True,
        "metadata": {"name": f"{SCENE_PREFIX}{name}"},
        "configuration": {
            "what": [{"group": group, "recall": {"rid": smart["rid"], "rtype": "smart_scene"}}],
            "when_extended": {"recurrence_days": EVERY_DAY, "start_at": {"time_point": {"type": "time", "time": hhmm(wake + 1)}}},
            "where": [{"group": group}],
        },
    })
    move_automation(BED_AUTOMATION, bed, set_start_at)
    move_automation(WAKE_AUTOMATION, wake - cfg["wake_fade_minutes"], set_wake_time)
    for b in api("GET", "behavior_instance"):
        if b["metadata"]["name"] in cfg.get("disable", []) and b["enabled"]:
            api("PUT", f"behavior_instance/{b['id']}", {"enabled": False})
            print(f"Disabled {b['metadata']['name']}")
    if activate or was_active:
        api("PUT", f"smart_scene/{smart['rid']}", {"recall": {"action": "activate"}})
    APPLIED.parent.mkdir(parents=True, exist_ok=True)
    APPLIED.write_text(json.dumps({"night": night.isoformat(), "bed": bed, "wake": wake, "config": cfg}))
    print(f"Applied {name!r} for the night of {night} ({note}): bright from {clock(wake - cfg['day_starts_before_wake'])}, "
          f"fade from {clock(bed - cfg['evening'][0]['before_bed'])}, lights off {clock(bed)}, "
          f"sunrise {clock(wake - cfg['wake_fade_minutes'])}-{clock(wake)}"
          f"{'' if activate or was_active else ' (left inactive; re-arms at wake)'}")


def cmd_schedule(a):
    cfg = json.loads(CONFIG.read_text())
    night = night_of()
    if a.action == "show":
        for s in api("GET", "smart_scene"):
            if name_of(s) == cfg["name"]:
                print(f"{cfg['name']}: {s['state']}, fade {s['transition_duration'] // 60000} min")
        bed, wake, note = anchors(cfg, night)
        print(f"Tonight ({night}, {note}): bed {clock(bed)}, wake {clock(wake)}")
        for slot in build_slots(cfg, bed, wake):
            print(f"  {clock(slot['at'])}  {slot['bri']}%  {slot.get('kelvin') or '-'}K")
        if cfg.get("shift"):
            print(f"Shift plan for {cfg['shift']['title']}:")
            for n, bed, wake in shift_plan(cfg):
                print(f"  night of {n:%a %b %d}: bed {clock(bed)}, up {clock(wake)}")
        return
    if a.action == "daily":
        # Run by launchd at noon: only touch the bridge when tonight's times differ from what's there.
        bed, wake, _ = anchors(cfg, night)
        try:
            last = json.loads(APPLIED.read_text())
            if (last["bed"], last["wake"], last["config"]) == (bed, wake, cfg):
                print(f"Unchanged for the night of {night}; nothing to do.")
                return
        except (OSError, ValueError, KeyError):
            pass
        apply_schedule(cfg, night, activate=False)
        return
    apply_schedule(cfg, night, activate=True)


def add_reminder(title, due, notes):
    """Apple Reminders via AppleScript (the apple-reminders CLI lacks Reminders access under launchd/Claude)."""
    script = (
        'on run argv\n'
        'tell application "Reminders" to make new reminder at end of list "Reminders" with properties '
        '{name:item 1 of argv, body:item 3 of argv, due date:date (item 2 of argv), remind me date:date (item 2 of argv)}\n'
        'end run'
    )
    subprocess.run(["osascript", "-e", script, title, due.strftime("%A, %B %-d, %Y at %-I:%M:%S %p"), notes],
                   check=True, capture_output=True)


def cmd_retime(a):
    """Set new normal bed/wake times, easing there from tonight's (or --from-*) times over --nights nights."""
    cfg = json.loads(CONFIG.read_text())
    night = night_of()
    bed, wake, _ = anchors(cfg, night)
    from_bed, from_wake = a.from_bed or clock(bed), a.from_wake or clock(wake)
    cfg["bedtime"], cfg["wake"] = a.bed, a.wake
    cfg["ramp"] = {"start": night.isoformat(), "nights": a.nights, "from_bed": from_bed, "from_wake": from_wake} if a.nights else None
    print(f"New normal: bed {a.bed}, up {a.wake}" + (f", easing from bed {from_bed}/up {from_wake} over {a.nights} nights:" if a.nights else ""))
    plan = []
    for k in range(a.nights + 1 if a.nights else 0):
        n = night + datetime.timedelta(days=k)
        b, w, _ = anchors(cfg, n)
        plan.append((n, b, w))
        print(f"  night of {n:%a %b %d}: bed {clock(b)}, up {clock(w)}")
    if a.dry_run:
        return
    CONFIG.write_text(json.dumps(cfg, indent=2) + "\n")
    if a.reminders:
        for n, b, w in plan[:-1]:
            bed_at = datetime.datetime.combine(n, datetime.time()) + datetime.timedelta(minutes=b)
            wake_at = datetime.datetime.combine(n + datetime.timedelta(days=1), datetime.time()) + datetime.timedelta(minutes=w)
            add_reminder(f"Bed by {clock(b)} (easing to {a.bed})", bed_at - datetime.timedelta(minutes=30),
                         "Lights start fading now; set by hue.py retime.")
            add_reminder(f"Wake up {clock(w)} (easing to {a.wake})", wake_at, "Set by hue.py retime.")
        print(f"Added {2 * (len(plan) - 1)} reminders (bedtime -30 min, and wake-up alarms).")
    apply_schedule(cfg, night, activate=False)


def cmd_shift(a):
    cfg = json.loads(CONFIG.read_text())
    if a.cancel:
        cfg["shift"] = None
        CONFIG.write_text(json.dumps(cfg, indent=2) + "\n")
        print("Shift cancelled; back to the normal schedule.")
        apply_schedule(cfg, night_of(), activate=False)
        return
    up = datetime.datetime.fromisoformat(a.up_by)
    event_date = up.date()
    start = datetime.date.fromisoformat(a.start) if a.start else night_of()
    if (event_date - start).days < 1:
        sys.exit("The event needs to be at least one night away.")
    cfg["shift"] = {"title": a.title, "wake": up.strftime("%H:%M"), "event_date": event_date.isoformat(), "start": start.isoformat()}
    plan = list(shift_plan(cfg))
    base_wake = mins(cfg["wake"])
    worst = max(abs(w2 - w1) for (_, _, w1), (_, _, w2) in zip([(None, None, base_wake)] + plan, plan))
    print(f"Shift for {a.title} (up by {up:%a %b %d %H:%M}), about {worst} min earlier per day:")
    for night, bed, wake in plan:
        print(f"  night of {night:%a %b %d}: bed {clock(bed)}, up {clock(wake)}")
    if worst > 60:
        print("  Warning: more than an hour a day is hard to keep up; start earlier with --start if you can.")
    if a.dry_run:
        return
    CONFIG.write_text(json.dumps(cfg, indent=2) + "\n")
    if a.reminders:  # off by default: Matt doesn't want bed/wake reminders (2026-10-22)
        for night, bed, wake in plan:
            bed_at = datetime.datetime.combine(night, datetime.time()) + datetime.timedelta(minutes=bed)
            wake_at = datetime.datetime.combine(night + datetime.timedelta(days=1), datetime.time()) + datetime.timedelta(minutes=wake)
            add_reminder(f"Bed by {clock(bed)} (shifting for {a.title})", bed_at - datetime.timedelta(minutes=30),
                         "Lights start fading now; set by hue.py shift.")
            add_reminder(f"Wake up {clock(wake)} (shifting for {a.title})", wake_at,
                         "Alarm for the gradual sleep shift; set by hue.py shift.")
        print(f"Added {2 * len(plan)} reminders (bedtime -30 min, and wake-up alarms).")
    apply_schedule(cfg, night_of(), activate=False)


def cmd_raw(a):
    print(json.dumps(api(a.method.upper(), a.path, json.loads(a.body) if a.body else None), indent=2))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("link").set_defaults(fn=cmd_link)
    sub.add_parser("status").set_defaults(fn=cmd_status)
    s = sub.add_parser("set")
    s.add_argument("target")
    s.add_argument("--on", action="store_true")
    s.add_argument("--off", action="store_true")
    s.add_argument("--bri", type=float)
    s.add_argument("--kelvin", type=int)
    s.add_argument("--fade", type=float, help="seconds")
    s.set_defaults(fn=cmd_set)
    sub.add_parser("automations").set_defaults(fn=cmd_automations)
    au = sub.add_parser("automation")
    au.add_argument("name")
    au.add_argument("--on", action="store_true")
    au.add_argument("--off", action="store_true")
    au.set_defaults(fn=cmd_automation)
    sc = sub.add_parser("schedule")
    sc.add_argument("action", choices=["apply", "show", "daily"])
    sc.set_defaults(fn=cmd_schedule)
    rt = sub.add_parser("retime", help="change normal bed/wake times, easing there over a few nights")
    rt.add_argument("--bed", required=True, help="new normal bedtime, HH:MM")
    rt.add_argument("--wake", required=True, help="new normal wake time (sunrise full), HH:MM")
    rt.add_argument("--from-bed", help="tonight's bedtime (default: whatever tonight is now)")
    rt.add_argument("--from-wake", help="tomorrow's wake time (default: whatever it is now)")
    rt.add_argument("--nights", type=int, default=0, help="nights to ease over (0 = switch tonight)")
    rt.add_argument("--reminders", action="store_true", help="also add bed/wake reminders (Matt doesn't want them)")
    rt.add_argument("--dry-run", action="store_true")
    rt.set_defaults(fn=cmd_retime)
    sh = sub.add_parser("shift", help="gradually move bed and wake times earlier for an early event")
    sh.add_argument("--up-by", help='when you need to be up, e.g. "2026-10-27 04:00"')
    sh.add_argument("--title", default="early event")
    sh.add_argument("--start", help="first night to shift (default: tonight)")
    sh.add_argument("--dry-run", action="store_true")
    sh.add_argument("--reminders", action="store_true", help="also add bed/wake reminders (Matt doesn't want them)")
    sh.add_argument("--cancel", action="store_true")
    sh.set_defaults(fn=cmd_shift)
    r = sub.add_parser("raw")
    r.add_argument("method")
    r.add_argument("path")
    r.add_argument("body", nargs="?")
    r.set_defaults(fn=cmd_raw)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
