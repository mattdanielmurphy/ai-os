# Free custom-domain email with instant push (2026-10-25)

## 15:20 Options researched

Asked (via coordinator): find free (no monthly fee) custom-domain email with instant phone push; check whether the current Zoho free plan can just be fixed. Research only: no email or DNS changes made.

What I checked: mattmurphy.ca MX points at Zoho (mx.zoho.com / mx2.zoho.com). His iCloud account has ~133 GB of quota left, so he already pays for iCloud+ (free tier is 5 GB). No Zoho app is installed on the Mac.

---

### iCloud custom domain

iCloud+ includes "Custom Email Domain": up to 5 domains, 10 addresses each, send and receive in Apple Mail on iPhone/Mac and icloud.com. iCloud Mail is true push on iPhone (Apple's own servers), so notifications are instant. Because he already pays for iCloud+, this costs nothing extra. Setup: Settings > Apple Account > iCloud > Custom Email Domain, then swap Zoho's MX/SPF/DKIM DNS records for Apple's. Risk: old mail stays in Zoho unless exported; do it once and keep Zoho as a fallback until it's verified. Source: https://support.apple.com/en-us/102540

---

### Zoho fix

Zoho's own pricing page says Mail Free has "IMAP/POP/ActiveSync not included", but does include the mobile app. So Apple Mail can't fetch it (no push, no fetch). The only fix on free is the Zoho Mail app (iOS/Android) with its notifications turned on. Forum reports on how instant that is are mixed; I found no official word on free-plan push timing. Cheapest paid step is Mail Lite (~US$1/user/month billed yearly), which adds IMAP but users report no true "Push" option in Apple Mail even then. Sources: https://www.zoho.com/mail/zohomail-pricing.html, https://help.zoho.com/portal/en/community/topic/mail-app-on-ios-and-push-notifications

---

### Cloudflare forward to Gmail

Cloudflare Email Routing (free) forwards mail for the domain into an existing inbox; Gmail push is instant. Needs DNS moved to Cloudflare, and sending as the custom address uses Gmail's "Send mail as" with Gmail SMTP plus an SPF tweak, or replies come from the gmail address / show warnings. More moving parts. Rejected as first choice since Matt avoids routing things through Gmail. Sources: https://dev.to/jaygooby/use-a-basic-gmail-account-to-send-mail-as-with-a-domain-that-uses-cloudflare-email-routing-89b

---

### Rejected

Google Workspace (no free tier; old free legacy being phased out), Neo (15-day trial only), Outlook.com (no custom domains on free).

Untested: iCloud setup itself and Zoho app push speed were not tried on his phone.

## 15:25 Agent access changes the pick

Matt wants Claude and other agents to read, draft and send his email. That flips the recommendation to Cloudflare forwarding into his existing Gmail.

---

### Gmail connector works everywhere

His Claude setup already has a Gmail connector (search, read, draft, send, labels). It works from cloud threads and the Code tab, no Mac needed. With Cloudflare Email Routing, all mail for his domain lands in that Gmail, so every agent can see it, and Gmail push on his phone is instant.

---

### iCloud is Mac-only for agents

iCloud has no Claude connector. Agents could only reach it through Mail.app AppleScript on his Mac (already used for emailing Matt) or IMAP with an app-specific password (himalaya CLI). Cloud threads couldn't touch it without a stored secret.

---

### Sending as the domain is unverified

Gmail "Send mail as" lets him (and Gmail itself) send from the custom address. I have not checked whether the Claude Gmail connector can pick that From address on drafts/sends; it may default to the gmail.com address. Needs a test after setup.

Note: the existing memory rule "send to Matt via Mail.app, never the Gmail connector" is about agents emailing Matt himself; it would need revisiting if Gmail becomes his main inbox.

## 15:30 Gmail send-as is going away, back to iCloud

The coordinator passed on Matt's earlier "Stop sending through gmail": Gmail is dropping third-party "Send mail as". I checked: Gmailify and POP fetching ended January 2026, and Android Authority (Aug 5, 2026) reports third-party "Send as" (custom domains included) ends January 2027. One source only; Google's own page not found.

---

### Cloudflare-to-Gmail breaks on sending

Receiving via Cloudflare forwarding would keep working, but from January 2027 neither Matt nor agents could send as his own domain from Gmail. So it's a dead end for a setup he wants to keep.

---

### iCloud with agent access

Back to iCloud custom domain (already paid for). Agents get in through IMAP/SMTP with an Apple app-specific password: the himalaya CLI skill can read, draft (save to Drafts) and send as the custom address. On his Mac that's a local secret in ai-os .env; cloud threads would need the same secret on the cloud environment. Mail.app AppleScript also works on the Mac. No Claude connector, so it's CLI/script access rather than a one-click connector. Untested.

---

### Rejected combo

Cloudflare receive + a sending API (Resend etc.): agents could send, but Matt's own phone replies would still come from Gmail. Too many pieces.

## 15:31 Does iCloud agent access need the Mac?

No in principle: IMAP/SMTP (imap.mail.me.com:993, smtp.mail.me.com:587) are internet services, so any machine with the app password can read, draft and send. Cloud threads would need the password saved as a secret on the cloud environment.

---

### Cloud ports might be blocked

Cloud sessions go through a network proxy that may only allow web (HTTPS) traffic. If ports 993/587 are blocked there, cloud threads can't reach iCloud mail directly. Untested. Fallbacks: hand it to the Mac (as with Amazon.ca), or a tiny mail relay on his VPS that cloud agents call over HTTPS.

## 15:55 Migration prep done, relay live

Matt asked to begin migrating to iCloud Mail, build the VPS relay, and leave the DNS cutover until he's ready to oversee it. Nothing about his live mail changed: MX, SPF and every DNS record are untouched; Zoho still gets all mail.

---

### Relay is live on the VPS

`services/mail-relay/relay.py` runs on oracle-vps (systemd `mail-relay`, 127.0.0.1:8790), published at https://vps.mattmurphy.ca/mail/ through Caddy (`handle_path /mail/*`; the existing app on 8000 still answers everything else, checked /docs = 200 before and after; Caddyfile backup `Caddyfile.bak-mail-relay`). Tools: list_folders, list_messages, search, read_message, find_codes (pulls sign-in codes from the last N minutes, aimed at his refresh pain), create_draft, send. REST with a bearer token and MCP (custom-connector style, token in path). Python stdlib only, so nothing to install. Why VPS + Python stdlib: the VPS already runs Caddy with HTTPS and reaches iCloud's IMAP/SMTP ports (checked with nc); stdlib means no dependency drift. Why MCP too: cloud threads and claude.ai can add it as a connector, closest to the Gmail-connector experience he liked. Rejected: Bun + imapflow (extra deps for no gain), a new subdomain (would need a DNS change, which he wants to hold).

---

### Tests and what's untested

`test_relay.py` runs 21 end-to-end checks on the VPS against a throwaway GreenMail server: auth rejects, list, search, read without marking seen, find_codes, threaded drafts, send + Sent copy, MCP initialize/list/call, ALLOW_SEND=0. All pass (found and fixed one bug: Python 3.10's getaddresses returns nothing when fed an empty field). `import_eml.py` tested twice against GreenMail: imports, keeps dates, skips duplicates on re-run. Live over HTTPS: health OK, bad token 401, good token reaches the tool and says "mailbox not configured yet". Untested: real iCloud login, real iCloud folder names (assumed "Sent Messages"/"Drafts"), Zoho's export format, whether Zoho free allows export.

---

### Token handling

Fresh token generated on the VPS (`~/apps/mail-relay/env`, mode 600), copied into ai-os `.env` as `MAIL_RELAY_TOKEN` via a pipe, never printed. Cloud threads need the same value added to the cloud environment's secrets (Matt does that). `configure.py` pushes the iCloud login from `.env` to the VPS the same way.

---

### Matt's steps before cutover

1) Apple app-specific password, then add MAIL_USER, MAIL_PASSWORD, MAIL_FROM, MAIL_FROM_NAME to ai-os .env and run configure.py. 2) iCloud Settings → Custom Email Domain → add mattmurphy.ca and his address, stop at the DNS screen. 3) Export Zoho mail. Then the cutover itself is a session together: TXT verify, SPF with both includes, DKIM CNAME, MX swap, tests, Zoho kept two weeks as a safety net. Full runbook and the DNS snapshot for rollback: services/mail-relay/README.md.

Side finding: a `*` wildcard CNAME to Vercel means Zoho DKIM was never set up, so his current outgoing mail isn't DKIM-signed. iCloud's explicit sig1 record fixes that at cutover.
