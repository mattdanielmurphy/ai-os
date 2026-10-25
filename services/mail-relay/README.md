# Mail relay

Lets Claude and other agents read, draft and send Matt's email from anywhere (cloud threads,
claude.ai, the Mac) over HTTPS. It logs into the mailbox (iCloud Mail) with IMAP/SMTP, so cloud
sessions that can only make web requests still get mail access.

Just for Matt (one mailbox, one token), but self-contained: any IMAP/SMTP mailbox works via env vars.

- **Where:** VPS `oracle-vps`, `~/apps/mail-relay/`, systemd `mail-relay`, `127.0.0.1:8790`,
  published by Caddy at `https://vps.mattmurphy.ca/mail/` (`handle_path /mail/*` in `/etc/caddy/Caddyfile`;
  backup of the old file: `Caddyfile.bak-mail-relay`).
- **Auth:** `MAIL_RELAY_TOKEN` (in the VPS `env` file and ai-os `.env`). REST takes
  `Authorization: Bearer <token>`; MCP takes it in the path. Wrong token: 401 (REST) / 404 (MCP).
- **Python stdlib only.** No packages to install.

## Tools

| Tool | What |
|---|---|
| `list_folders` | mail folders |
| `list_messages` | newest in a folder (`folder`, `limit`, `unread_only`) |
| `search` | `query`, `field` TEXT/FROM/SUBJECT/TO/BODY |
| `read_message` | one message by `uid`; never marks it read |
| `find_codes` | sign-in / verification codes from the last `minutes` (default 15) |
| `create_draft` | saves to Drafts; `in_reply_to_uid` threads a reply |
| `send` | sends as `MAIL_FROM`, copies to Sent, logs to `sent.jsonl`. Agents send only after Matt OKs that exact message. `ALLOW_SEND=0` turns sending off. |

REST: `GET|POST https://vps.mattmurphy.ca/mail/api/<tool>` (query string or JSON body).
MCP: `https://vps.mattmurphy.ca/mail/mcp/<token>` (add as a custom connector in claude.ai, no OAuth).

```bash
tok=$(grep ^MAIL_RELAY_TOKEN= ~/projects/ai-os/.env | cut -d= -f2-)
curl -s -H "Authorization: Bearer $tok" "https://vps.mattmurphy.ca/mail/api/find_codes?minutes=10"
```

## Files

- `relay.py`: the server. `test_relay.py`: end-to-end test against a throwaway GreenMail server (21 checks; command in its docstring).
- `configure.py`: copies `MAIL_USER`, `MAIL_PASSWORD`, `MAIL_FROM`, `MAIL_FROM_NAME`, `SMTP_USER` from ai-os `.env` to the VPS and restarts. `--check` shows which are set. Never prints values.
- `import_eml.py`: copies a Zoho export (.zip or folder of .eml) into the mailbox under `Zoho/…`; keeps dates, skips duplicates, re-runnable, `--dry-run`.
- Deploy: `scp relay.py oracle-vps:apps/mail-relay/ && ssh oracle-vps sudo systemctl restart mail-relay`.

## Zoho → iCloud migration runbook

Mail must never break. Everything before step 5 changes nothing live.

1. **App password (Matt).** account.apple.com → Sign-In and Security → App-Specific Passwords → "mail-relay".
   Add to ai-os `.env` (`code ~/projects/ai-os/.env`): `MAIL_USER` (Apple Account email), `MAIL_PASSWORD`,
   `MAIL_FROM` (the mattmurphy.ca address), `MAIL_FROM_NAME`. Then `python3 services/mail-relay/configure.py`.
   Relay now reads the iCloud inbox (tests work before the domain moves).
2. **Add the domain in iCloud (Matt).** iPhone Settings → [name] → iCloud → iCloud Mail → Custom Email Domain →
   Add Domain → mattmurphy.ca → add the existing address. Stop at the DNS step and note the records Apple shows
   (the verification TXT is unique to him).
3. **Export Zoho mail (Matt).** mail.zoho.com → Settings → Import/Export → Export, each folder. Unverified that
   free plans can export; if not, forward/print the few that matter.
4. **Lower TTLs.** Cloudflare: set the MX/TXT records' TTL to 2 min a day ahead.
5. **Cutover (together, quiet time).** In Cloudflare DNS:
   - add Apple's verification TXT (`apple-domain=…`)
   - SPF: `v=spf1 include:icloud.com include:zoho.com ~all` (both while switching)
   - DKIM: CNAME `sig1._domainkey` → `sig1.dkim.mattmurphy.ca.at.icloudmailadmin.com` (DNS only, not proxied;
     an explicit record overrides the current `*` → Vercel wildcard)
   - replace MX with `mx01.mail.icloud.com` and `mx02.mail.icloud.com` (priority 10, per Apple's page)
   - in iCloud settings tap Finish / Done once Apple verifies.
6. **Test hard:** mail from Gmail and the ualberta address arrives on the iPhone instantly; a reply from the
   iPhone shows SPF/DKIM pass (Gmail → Show original); a sign-in code arrives and `find_codes` sees it;
   relay `send` to himself works.
7. **Keep Zoho for 2 weeks.** Mail sent during propagation still lands there; check it, then import with
   `import_eml.py`. After that, SPF drops `include:zoho.com` and the Zoho TXT goes.

**Rollback:** put back MX `10 mx.zoho.com`, `20 mx2.zoho.com` and SPF `v=spf1 include:zoho.com ~all`.

### DNS snapshot before migration (2026-10-25, Cloudflare `yew`/`zita`)

```
MX     10 mx.zoho.com. / 20 mx2.zoho.com.
TXT    v=spf1 include:zoho.com ~all
TXT    zoho-verification=zb60615773.zmverify.zoho.com
TXT    google-site-verification=RYpG8McYiX9dsSwkvr4tkF4gZ_Fz7CVLWDQ_2GwKP7g
_dmarc TXT v=DMARC1; p=none;
*      CNAME cname.vercel-dns.com (wildcard: also catches *._domainkey, so Zoho DKIM is not set up today)
```
