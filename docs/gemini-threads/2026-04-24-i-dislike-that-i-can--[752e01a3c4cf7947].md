---
title: "I dislike that I can only change SwitchBot config in the app"
date: "2026-08-13"
source: "gemini.google.com"
conversation_id: "821d0aa0-75f8-5fcf-bb4c-513eef49cd2c"
url: ""
---

# I dislike that I can only change SwitchBot config in the app

> [!NOTE]
> Archived Gemini Thread: [I dislike that I can only change SwitchBot config in the app]() | Date: 2026-08-13

## User

I dislike that I can only change SwitchBot config in the app and can’t automate it much. (Eg open 10 mins earlier per day until it reaches sunrise).
What’s the cheapest way of enabling that?

---

## Gemini

The cheapest way to achieve dynamic, time-shifting automation for SwitchBot is to move the logic away from their app and onto a local controller. Since you’re a macOS power user and web developer, you can do this for $0 (assuming you have a Mac or an old PC/Raspberry Pi running 24/7).


1. The $0 Solution: Homebridge + Scripting
You can run Homebridge on your Mac. It has a robust SwitchBot plugin that can communicate via Bluetooth (if your Mac is close enough) or via the SwitchBot OpenAPI (requires a Hub, but gives you more flexibility).



* The Logic: Instead of setting a static schedule, you use a script to calculate the time.

* The Tool: Homebridge-SwitchBot plugin.

* Implementation: You can write a small Node.js script or use a Cron job that updates a "Virtual Switch" or triggers the Curtain/Bot directly. Since you’re already building Columnar with TypeScript, writing a small script to calculate $CurrentSunrise - (10 \times Days)$ and firing a webhook would be trivial for you.


2. The "Set it and Forget it" Solution: Home Assistant (Free Software)
If you want something more professional that doesn't rely on your primary Mac staying awake, Home Assistant is the gold standard.



* Cost: $0 if run on an existing machine; ~$35 if you buy a Raspberry Pi.

* Why it works: It has a native SwitchBot (Bluetooth) integration. You don't even need a SwitchBot Hub if your server has Bluetooth.

* The Automation: You can create a "Template Sensor" that calculates your desired opening time daily.

* Example logic: set opening_time = state_attr('sun.sun', 'next_rising') - timedelta(minutes=10 * days_since_start)





3. The "Low-Code" Middle Ground: IFTTT + Webhooks
If you have a SwitchBot Hub, you can use IFTTT, but it's increasingly restrictive with its "Pro" tiers. I wouldn't recommend this for a developer—it's slower and more expensive in the long run.



Comparison Table

































MethodHardware NeededCostEffortReliabilityHomebridge (Mac)None (uses existing Mac)$0LowMedium (Mac must stay on)Home AssistantPC/Mac/Raspberry Pi$0 - $35HighHigh (Local control)Python/Node ScriptMac + Hub (for API)$0MediumHigh (Total control)
My Recommendation
Since you’re comfortable with automation tools like Hammerspoon and Keyboard Maestro, I'd suggest starting with Homebridge on your Mac.



* Enable Developer Options in the SwitchBot App (tap App Version 10 times) to get your OpenAPI Token/Secret.

* Install homebridge-switchbot.

* Write a simple script to trigger the OpenAPI at your calculated time.


This bypasses the app's scheduling limitations entirely without requiring you to buy a Hub 2 or extra hardware.


How many SwitchBot devices are you looking to sync up with this "earlier every day" routine?

---

## User

Ooh I’ve got an old rpi. Does it have Bluetooth tho? Might need an adapter

---

## Gemini

Whether you need an adapter depends on the specific model. Raspberry Pis started including built-in Bluetooth with the Pi 3 Model B.


Does yours have it?
You can verify the hardware by running this in the terminal:


hciconfig


* If you see hci0: You’re good to go. The hardware is present.

* If it returns nothing: You’ll need a USB adapter.


Raspberry Pi Bluetooth Compatibility

























ModelBluetooth StatusPi 4, 5, 400Built-in (BT 5.0)Pi 3 (B, B+, A+)Built-in (BT 4.1 / 4.2)Pi Zero W / Zero 2 WBuilt-in (BT 4.1)Pi 1, Pi 2, Zero (non-W)None (Needs USB adapter)
If you need an adapter
Don't break the bank. You just need a Bluetooth 4.0 or 5.0 USB Dongle that is "plug-and-play" with Linux.



* Top Pick: The TP-Link UB400 or UB500 are usually around $15 CAD and work out of the box with Raspberry Pi OS and Home Assistant.

* The "Developer" Pick: If you have any old CSR 4.0 dongles lying in a drawer from years ago, those almost always work too.


Why the Pi is better than the Mac for this
Since SwitchBot uses Bluetooth Low Energy (BLE), range is the biggest hurdle. If your Mac is in an office and the SwitchBot is in a bedroom, it won't work. The Pi is small enough that you can tuck it behind a curtain or near the device and just leave it powered on 24/7.


Quick Check: Do you happen to know if it's a Pi 2 or 3? (The Pi 3 has "FCC" markings on the board and a small white ceramic antenna near the GPIO pins).

---

## User

When did pi3 come out?

---

## Gemini

The Raspberry Pi 3 Model B was released on February 29, 2016.


It was a significant milestone because it was the first "flagship" Pi to include integrated Wi-Fi and Bluetooth (4.1). If your board has "Raspberry Pi 3" silk-screened on it, you’re set—no adapter required.


How to be 100% sure
If you can't find the text on the board, look for the small white ceramic rectangle near the display connector or the GPIO pins—that's the internal antenna. The Pi 1 and Pi 2 are missing that component and have a much larger, silver metal "can" (the crystal oscillator) in different spots.


Your Game Plan for SwitchBot
Since you're comfortable with TypeScript and web dev:



* OS: Flash a fresh copy of Raspberry Pi OS Lite (no need for a desktop GUI).

* Controller: Install Home Assistant (via Docker is easiest for devs) or Homebridge.

* The "10-minute" Logic: * In Home Assistant, you’d use a Template Sensor to track the "Target Open Time."

* Every night at midnight, have a script increment a daily_offset variable by 10.

* Set the automation to trigger at sunrise - daily_offset.





Because the Pi 3's Bluetooth is on-board, it’s surprisingly reliable for BLE (Bluetooth Low Energy) commands, which is exactly what SwitchBot uses.


Do you remember if your Pi was part of an old project, or has it just been sitting in a "parts bin" waiting for its moment?

---

## User

So then how would I update the config?

---

## Gemini

To update the configuration without using the SwitchBot app, you effectively turn your Raspberry Pi into the "brain" that sends the commands. Since you have the skills to handle a terminal, here is the most efficient path:


1. The Home Assistant Path (Recommended)
This is the most "set it and forget it" method. Home Assistant has a native SwitchBot integration that uses the Pi’s Bluetooth to talk directly to your devices.



* Setup: Once installed, it will likely auto-discover your SwitchBot.

* The Logic: You’ll use the YAML editor (or the UI) to create an "Input Number" helper to track your offset.

* The Automation:
trigger:
  - platform: sun
    event: sunrise
    offset: "-00:10:00" # This is where your dynamic logic goes
action:
  - service: switchbot.device_open
    target:
      device_id: your_curtain_id




2. The Web Dev Path (Custom Script)
If you want total control, you can write a simple Node.js script using a library like node-switchbot. This allows you to skip the heavy UI of Home Assistant.



* Logic: Write a script that calculates the time: $TargetTime = Sunrise - (10 \times Days)$.

* Scheduling: Use a Cron job on the Pi to run this script daily at midnight. The script calculates the "Today's Open Time" and schedules a one-time at command or remains active as a light background process.


3. Communicating with the Device
Regardless of the software, the "update" happens over BLE (Bluetooth Low Energy).



* Direct Control: Your Pi sends a specific HEX command (a "handle") to the SwitchBot.

* No Hub Needed: Because your Pi is the controller, you don't need the SwitchBot Cloud or the official Hub. You are talking directly to the hardware.


How to get started on the Pi:

* Check Bluetooth: Ensure bluez is installed (sudo apt install bluez).

* Scan for Devices: Run bluetoothctl then scan on to find the MAC address of your SwitchBot.

* Pick your "Brain":

* Easy/GUI: Install Home Assistant (use the "Supervised" or "Docker" method).

* Pro/Scripted: Use Homebridge with the homebridge-switchbot plugin. It has a "Schedule" feature that is much more flexible than the official app.





Since you're already doing web dev, does the idea of managing a small Docker container on the Pi sound like the right level of effort, or are you looking for something even more "bare metal"?

---

## User

I’d want to be able to make modifications quickly and easily with my phone like: delay opening of curtain tomorrow morning only until X time.
I could probably set up a server on the pi or whatever and be able to update the config using even iOS shortcuts with http requests

---

## Gemini

Since you're a web developer, building a "Remote Controller" for your curtains via iOS Shortcuts is actually the most efficient way to get that high-precision control you want.


You can bypass the SwitchBot app entirely by using your Raspberry Pi as a local API server. Here is the cleanest architecture to get that "Delay until X" functionality:


1. The Architecture: Pi as a Webhook Listener
The most lightweight way (without a heavy UI) is to run a simple Node.js/Express server or Python/Flask app on your Pi.



* Endpoint: POST /curtain/override

* Payload: { "time": "08:30" }

* Logic: The script saves this time to a local config.json. Every morning, your main automation script checks if an override exists for "today" before falling back to its default "sunrise minus offset" calculation.


2. The iOS Shortcut Setup
In iOS Shortcuts, you don't need a custom app. You can use the native "Get Contents of URL" action.



* Action 1: "Ask for Input" (Type: Time).

* Action 2: "Get Contents of [Your-Pi-IP]:3000/override"

* Method: POST

* JSON Body: {"open_at": "Provided Input"}





3. The "Developer" Way: Home Assistant + Helpers
If you don't want to maintain your own API code, Home Assistant (running on your Pi) has this built-in via "Helpers."



* Create a Helper: In HA, go to Settings > Helpers and create a Date and/or Time helper called input_datetime.curtain_override.

* The Automation: Set your curtain automation to trigger at the value of that helper.

* iOS Integration: Download the Home Assistant Companion App. It exposes your "Helpers" directly to iOS Shortcuts.

* Your Shortcut would simply be: "Call Service: input_datetime.set_datetime" with the data from your manual time picker.





Why this beats the App

* Granularity: You can calculate $Sunrise + \text{Coffee Brew Time}$ or any other variable.

* Speed: You can place this Shortcut as a Widget on your iPhone home screen or map it to the Action Button (if you have an iPhone 15/16 Pro).

* Zero Cloud: By using the Pi's Bluetooth, you aren't relying on SwitchBot's servers. If your internet goes down, your curtains still open.


Pro-Tip for the "10 mins earlier" logic:
Since you're doing this on a Pi, you can store a startDate in a text file. Your script can then calculate:
$$CurrentOpenTime = Sunrise - ( (Today - StartDate) \times 10 )$$
If you trigger your "Override" shortcut, it simply writes a "True" flag to a isOverridden variable to skip the math for one day.


Does your Pi currently have a clean OS install, or would you be starting the setup from scratch?

---

