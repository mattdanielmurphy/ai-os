---
title: "I need a new free spam filter. I also need to provide my AI tools a way of..."
date: "2026-08-15"
conversation_id: "57d251b2-5988-44a3-a091-9c84062c3cba"
source: "antigravity"
---

# I need a new free spam filter. I also need to provide my AI tools a way of...

## User

I need a new free spam filter.
I also need to provide my AI tools a way of reading my email.
Problem is, I have zoho mail AND gmail.
i wouldn't mind switching my zoho account to gmail. I have a custom domain though.
Can't be paying for it.
Eventually I'd love to have Google Jules just clean out the spam in my inbox once a day

---

## Assistant

## Perplexity — 12:47 PM

I've got a solid path here — good news is everything you want is doable for $0. Let me break it down.

Consolidate onto Gmail (keep your custom domain, no Workspace fee)

Google Workspace (the paid product) is the only way to get a custom domain natively *inside* Gmail's servers, but you don't need it. The free workaround everyone uses:

**Receiving mail**: Point your domain's DNS to Cloudflare (free), then enable **Cloudflare Email Routing** and set a rule forwarding `you@yourdomain.com` → your Gmail address. This is unlimited and free on any Cloudflare plan.
sendmailas
+1

**Sending mail as your domain**: In Gmail → Settings → Accounts and Import → "Send mail as" → add `you@yourdomain.com`, using Gmail's own SMTP (`smtp.gmail.com`, port 587) with an **app password**. Gmail will send a verification email that arrives via the Cloudflare forward you just set up.
threeportkeys
+1

Once verified, Gmail becomes your single inbox for both addresses — you can retire Zoho entirely and stop paying nothing for it too.

Worth knowing: Zoho's **free** plan doesn't expose IMAP or API access — that's paid-tier only. That's actually a strong argument for moving off Zoho, since it's a dead end for AI tools reading it.
reddit

Free spam filtering

Gmail's built-in spam filter is already best-in-class and free — once you're consolidated there, you may not need a third-party filter at all. If you want more granular control (auto-unsubscribe, bulk sender cleanup, block lists), free options that work with Gmail:

**Gmail's own filters** (Settings → Filters and Blocked Addresses) — free, no install.

**Clean Email** or **Edison Mail** — both have functional free tiers that add unsubscribe/bulk-cleanup on top of Gmail/IMAP accounts.
edisonmail

Giving your AI tools read access to your inbox

The standard, free, and secure way is the **Gmail API** via OAuth — this is what Claude, Gemini, and most AI connectors use, and Google's free tier quota (1 billion quota units/day, way beyond personal use) costs nothing for a personal Gmail account. Since Zoho's free plan blocks IMAP/API, this only works cleanly once you're on Gmail — another reason to consolidate.
reddit

Reality check on "Jules cleaning spam daily"

Jules is Google's coding agent — it operates on **GitHub repositories** and opens PRs, it doesn't have a mailbox-reading mode, even with its new Scheduled Tasks feature (which reruns Jules against a repo on a cron, not against Gmail). So "have Jules empty my spam once a day" isn't something Jules does out of the box. But you can build the equivalent yourself for free in about 10 minutes using **Google Apps Script** (which lives inside your Gmail account already):
jules


```
javascript
function emptySpam() {
  const threads = GmailApp.search('in:spam');
  threads.forEach(t => t.moveToTrash()); // or Gmail.Users.Messages.remove for permanent delete
}
```


Add a **time-driven trigger** (Apps Script → Triggers → Add Trigger → daily) and it runs automatically, completely free, forever, with no quota concerns. If you want it smarter than "just empty the spam label" (e.g. an LLM double-checking borderline senders before deleting), you could have Jules or Claude write a slightly beefier version that calls the Gmail API plus a free-tier Gemini call for classification — Jules is actually well-suited to *building* that script for you (since that's a coding task in a repo), you'd just run it via Apps Script's trigger or a free GitHub Actions cron rather than Jules itself.
reddit
+1

**Bottom line path**: Cloudflare Email Routing + Gmail "send as" to consolidate → drop Zoho → use Gmail API/OAuth for AI tool access → Apps Script daily trigger for spam cleanup (optionally built by Jules) → rely on Gmail's native filter, add Clean Email if you want a nicer UI for bulk cleanup.

---

## User

what? There is no free-tier gemini anymore. But still, getting deepseek to identify and move real spam emails once a day is negligible. I just wonder, is it going to be a pain in the ass? Surely there's some infrastructure around spam filtering I can piggy back off of?

---

## Assistant

## Perplexity — 12:47 PM

Fair pushback on Gemini — you're right, Google killed the always-free API tier for new usage patterns in 2025/early 2026 (there's still a limited free tier, but it's stingier than it used to be). And no, this really isn't going to be a pain — you're overestimating the lift because most of the "spam filtering" work is already done for you by infrastructure you're already piggybacking on. Let me separate what needs AI from what doesn't.

You already have 90% of this for free — it's called Gmail

Google's own spam classifier is one of the best in the industry and it's already running, for free, on every message that hits your account. Anything landing in the `SPAM` label is already-identified spam — no LLM needed to "identify" it, just something to empty it on a schedule. That's a one-time setup with **Google Apps Script**, which lives inside your Gmail account (no external hosting, no server, no cost):


```
javascript
function permanentlyDeleteSpam() {
  const res = Gmail.Users.Messages.list("me", { labelIds: ["SPAM"], maxResults: 100 });
  if (!res.messages) return;
  res.messages.forEach(m => Gmail.Users.Messages.remove("me", m.id));
}
```


Attach a daily time-driven trigger and it runs forever, free, no maintenance . That's the whole "empty spam once a day" problem solved with zero AI involved, since Gmail already did the identification.

Where DeepSeek actually adds value

The AI step only matters for the harder case: junk that Gmail's filter *didn't* catch and left sitting in your actual Inbox (or borderline Promotions/Social stuff). That's a genuinely small daily job — pull unread/recent messages, ask DeepSeek "is this spam y/n", act on the response. This is where "negligible" is accurate: DeepSeek's API is priced in fractions of a cent per call, and a daily batch of even a few hundred emails costs pennies a month, not "free" in the literal sense but close enough to round to zero.
linkedin
+1

Infra you can piggyback on rather than build

You don't need to write this from scratch — there are existing free templates for exactly this pattern:

**n8n** (open-source, self-hostable for free via Docker) has pre-built workflows like "Auto-clean Gmail spam folder using Gmail API" and "Automatically Delete Spam Emails in Gmail on Schedule" — you import the JSON, swap in a DeepSeek HTTP node for the judgment step, point it at your Inbox instead of just the Spam label, and set the schedule trigger. This is the closest thing to "infrastructure to piggyback on" — you're not building spam-detection plumbing, just wiring an LLM call into an existing Gmail-cleanup graph.
n8n
+2

**GitHub Actions cron** (free minutes, and you've already got the GitHub connector) — a ~50-line Python script using the Gmail API + a DeepSeek call, triggered by a `schedule:` cron in a workflow file. Given your stack (Python, GitHub, comfortable with APIs), this is probably the least fiddly option for you specifically, and it's the one Jules could actually help you write and maintain as a repo, since Jules operates on GitHub repos, not mailboxes.

**Apps Script + external fetch** — Apps Script can also call out to DeepSeek's API directly via `UrlFetchApp`, so you don't even need n8n or GitHub Actions; the whole pipeline (list Inbox → call DeepSeek → label/trash) can live in one Apps Script file with one trigger, still 100% free hosting since it runs on Google's infrastructure.
growwstacks

Bottom line

Set up the Apps Script "empty Spam label" trigger today — that's zero pain, ten minutes, and handles the bulk of it using Gmail's existing classifier. Only bother wiring in DeepSeek if you notice things slipping into your actual Inbox that Gmail should've caught; when you get there, forking an existing n8n Gmail-cleanup template or writing a small GitHub Actions script (given your stack, the latter is probably the natural fit) is a half-hour job, not an ongoing chore, since it's cron-driven and self-running once deployed.

---

## User

Dude I KNOW that gmail has a spam filter and that it labels things SPAM. I'm not a fucking idiot. I'm just saying, it doesn't catch everything.
Then again, I haven't use gmail in a while so maybe I don't have to do anything. Right now, my mission apparently is getting my zoho mail account moved over to gmail.
But I tried to do that with another account of mine and had trouble, so I'm nervous about doing it with my main email. Will have to do it carefully.

---

## Assistant

## Perplexity — 12:47 PM

Fair — and honestly, being cautious with your main account is the right instinct. Zoho→Gmail migrations do have a few footguns people hit constantly, so let's do this in an order that's fully reversible until the very last step.

Why the safe order matters

The dangerous part isn't copying mail — it's **DNS (MX records)**, since that's what decides who actually receives new mail for your domain. Copying old mail into Gmail is completely non-destructive (Zoho keeps everything, Gmail just gets a duplicate copy). Switching MX is the only step where a mistake could mean bounced or dropped mail, so that goes last, only after everything else is verified working.

Step-by-step, safest path

**Back up first, no matter what.** In Zoho: Settings → Import/Export → Export All Emails, download the archive locally. This is your insurance copy regardless of what happens next.
cashify

**Enable IMAP on Zoho** (Settings → Mail → IMAP Access) — this is off by default and is one of the most common reasons migrations silently fail or time out.
vaultme
+1

**Import a copy into Gmail without touching Zoho's DNS.** Gmail → Settings → Accounts and Import → "Import mail and contacts" → enter Zoho IMAP credentials (`imappro.zoho.com`, port 993, SSL). This pulls everything into Gmail while Zoho keeps functioning normally the whole time — nothing is deleted or redirected yet.
vaultme
+1

**Verify the import.** Check message counts roughly match, spot-check a few important old threads, confirm attachments came through. Don't rush past this — this is your checkpoint before anything becomes irreversible.

**Set up "Send mail as" your custom domain in Gmail** (Accounts and Import → Send mail as → Add another email address, using Zoho's SMTP: `smtp.zoho.com`, port 465/587). Verify via the confirmation email — which will still arrive through Zoho at this point, since MX hasn't moved. Now Gmail can send *as* your domain even before it receives mail there.
medium

**Only now touch DNS.** Point MX to Cloudflare Email Routing (or Google's MX if you ever go Workspace) and set the forward rule to your Gmail address. Do this at a low-traffic time (like now, midday Friday, rather than right before something important) since propagation can take minutes to a couple hours and there's a small window where routing is in flux .

**Keep the Zoho mailbox alive, unused, for a few weeks** before cancelling anything. If anything slipped through, you can still log in and retrieve it. No pressure to delete Zoho immediately — it costs nothing to leave it dormant.

Common failure points (worth knowing before you start)

**IMAP not enabled** — the single most common cause of "the migration just didn't work".
vaultme

**Zoho free plan restrictions** — some import/export and forwarding features are gated or rate-limited on free plans, which can cause partial or stalled transfers depending on mailbox size.
cashify

**SMTP verification failures** — Zoho's outbound servers sometimes rate-limit or flag the Gmail verification email as suspicious on first attempt; if step 5's confirmation email doesn't arrive within a few minutes, retry rather than assuming it's broken.

**Doing MX switch too early** — if you flip DNS before confirming the Gmail import worked, you lose the safety net of "Zoho still has everything" while you troubleshoot.

If you tell me what specifically went wrong on your other account's migration, I can help pinpoint whether it's likely to bite you here too before you start on the main one.

---

## User

you know... I actually just realized, agents can search through Mail.app emails just fine. Might even be BETTER than gmail? compare the two

---

## Assistant

## Perplexity — 12:47 PM

Good catch, but there's a distinction worth untangling here: Mail.app is a **client**, not a mail provider. It doesn't generate its own spam filtering the way Gmail's servers do — it either inherits whatever your backend provider (Zoho, Gmail, iCloud) already decided, or it runs a thin local filter on top. So "Mail.app vs Gmail" is really two different comparisons smashed together: agent access convenience,

---
