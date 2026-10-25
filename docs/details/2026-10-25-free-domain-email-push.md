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
