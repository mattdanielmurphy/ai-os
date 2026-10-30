"""Deploy to the VPS: copy bot.py, write its .env (no values printed), install deps, unit and Caddy route."""
import base64, json, secrets, subprocess, urllib.request
from pathlib import Path
from dotenv import dotenv_values

HERE = Path(__file__).parent
v = dotenv_values(Path.home()/"projects/ai-os/.env")
sid, tok = v["TWILIO_ACCOUNT_SID"], v["TWILIO_AUTH_TOKEN"]
auth = base64.b64encode(f"{sid}:{tok}".encode()).decode()
ids = json.load(urllib.request.urlopen(urllib.request.Request(
    f"https://api.twilio.com/2010-04-01/Accounts/{sid}/OutgoingCallerIds.json", headers={"Authorization": "Basic "+auth}), timeout=15))
ids = ids["outgoing_caller_ids"]
print("verified numbers:", len(ids))
nums = json.load(urllib.request.urlopen(urllib.request.Request(
    f"https://api.twilio.com/2010-04-01/Accounts/{sid}/IncomingPhoneNumbers.json", headers={"Authorization": "Basic "+auth}), timeout=15))
frm = nums["incoming_phone_numbers"][0]["phone_number"]
token = secrets.token_urlsafe(24)
env = {k: v[k] for k in ("TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "DEEPGRAM_API_KEY", "SPEECHIFY_API_KEY", "ANTHROPIC_API_KEY")}
env |= {"TWILIO_PHONE_NUMBER": frm, "MATT_PHONE": ids[0]["phone_number"], "CALL_TOKEN": token}
(HERE/".call-token").write_text(token)

REMOTE = r'''set -e
mkdir -p ~/apps/morning-call; cd ~/apps/morning-call
cat > .env; chmod 600 .env
command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH=$HOME/.local/bin:$PATH
uv venv -q --python 3.12 --allow-existing .venv
uv pip install -q --python .venv/bin/python "pipecat-ai[deepgram,anthropic,silero,websocket]" fastapi uvicorn python-dotenv aiohttp
sudo tee /etc/systemd/system/morning-call.service >/dev/null <<E
[Unit]
Description=Morning call bot
After=network-online.target
[Service]
User=$USER
WorkingDirectory=$HOME/apps/morning-call
ExecStart=$HOME/apps/morning-call/.venv/bin/uvicorn bot:app --host 127.0.0.1 --port 8797
Restart=always
MemoryMax=2G
CPUQuota=200%
[Install]
WantedBy=multi-user.target
E
grep -q morning-call /etc/caddy/Caddyfile || sudo sed -i '0,/^vps.mattmurphy.ca {/s//vps.mattmurphy.ca {\n\thandle_path \/morning-call\/* {\n\t\treverse_proxy 127.0.0.1:8797\n\t}/' /etc/caddy/Caddyfile
sudo caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile >/dev/null 2>&1
sudo systemctl daemon-reload; sudo systemctl enable -q morning-call; sudo systemctl restart morning-call; sudo systemctl reload caddy
sleep 12; curl -s https://vps.mattmurphy.ca/morning-call/health; echo; systemctl is-active morning-call
'''
subprocess.run(["scp", "-q", str(HERE/"bot.py"), "oracle-vps:apps-morning-call-bot.py"], check=True)
body = "\n".join(f"{k}={val}" for k, val in env.items())+"\n"
subprocess.run(["ssh", "oracle-vps", "mkdir -p ~/apps/morning-call && mv ~/apps-morning-call-bot.py ~/apps/morning-call/bot.py && "+REMOTE], input=body.encode(), check=True)
