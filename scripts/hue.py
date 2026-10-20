#!/usr/bin/env python3
"""Control Matt's Philips Hue lights through the local Hue Bridge (CLIP v2 API).

The app key lives in the macOS Keychain (service "ai-os-hue"), never in files.

  hue.py link                           pair with the bridge (press its button within 10 min)
  hue.py status                         rooms, lights, on/brightness/colour temp
  hue.py set <room|light|all> [--on|--off] [--bri 0-100] [--kelvin 2000-6500] [--fade SECONDS]
  hue.py automations                    list bridge automations (behaviors)
  hue.py automation <name> --on|--off   enable/disable an automation
  hue.py schedule apply                 push config/hue_schedule.json to the bridge
  hue.py schedule show                  print the active ai-os schedule
  hue.py raw GET|PUT|POST|DELETE <resource path> [json]   escape hatch for anything else
"""
import argparse
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
SCHEDULE_NAME = "ai-os bright-then-fade"

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


def hhmm(s):
    h, m = s.split(":")
    return {"hour": int(h), "minute": int(m)}


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


def cmd_schedule(a):
    cfg = json.loads(CONFIG.read_text())
    home = api("GET", "bridge_home")[0]
    group = {"rid": home["id"], "rtype": "bridge_home"}
    name = cfg["name"]
    if a.action == "show":
        for s in api("GET", "smart_scene"):
            if name_of(s) == name:
                print(f"{name}: {s['state']}, fade {s['transition_duration'] // 60000} min")
        for slot in cfg["slots"]:
            print(f"  {slot['time']}  {slot['bri']}%  {slot.get('kelvin', '-')}K")
        return

    # Re-applying replaces everything this command made before, so the config file stays the source of truth.
    for b in api("GET", "behavior_instance"):
        if b["metadata"]["name"] == f"{SCENE_PREFIX}{name}":
            api("DELETE", f"behavior_instance/{b['id']}")
    for s in api("GET", "smart_scene"):
        if name_of(s) == name:
            api("DELETE", f"smart_scene/{s['id']}")
    for s in api("GET", "scene"):
        if name_of(s).startswith(SCENE_PREFIX):
            api("DELETE", f"scene/{s['id']}")

    lights = api("GET", "light")
    timeslots = []
    for slot in sorted(cfg["slots"], key=lambda s: s["time"]):
        scene = api("POST", "scene", {
            "metadata": {"name": f"{SCENE_PREFIX}{slot['time']}"},
            "group": group,
            "actions": slot_actions(lights, slot),
        })[0]
        timeslots.append({
            "start_time": {"kind": "time", "time": {**hhmm(slot["time"]), "second": 0}},
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
            "when_extended": {"recurrence_days": EVERY_DAY, "start_at": {"time_point": {"type": "time", "time": hhmm(cfg["activate_at"])}}},
            "where": [{"group": group}],
        },
    })
    for b in api("GET", "behavior_instance"):
        if b["metadata"]["name"] in cfg.get("disable", []) and b["enabled"]:
            api("PUT", f"behavior_instance/{b['id']}", {"enabled": False})
            print(f"Disabled {b['metadata']['name']}")
    api("PUT", f"smart_scene/{smart['rid']}", {"recall": {"action": "activate"}})
    print(f"Applied and activated {name!r}: {len(timeslots)} slots, {cfg['fade_minutes']} min fades, re-armed daily at {cfg['activate_at']}")


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
    sc.add_argument("action", choices=["apply", "show"])
    sc.set_defaults(fn=cmd_schedule)
    r = sub.add_parser("raw")
    r.add_argument("method")
    r.add_argument("path")
    r.add_argument("body", nargs="?")
    r.set_defaults(fn=cmd_raw)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
