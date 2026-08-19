---
title: "Check Google Cloud Credits Balance"
date: "2026-07-26"
conversation_id: "84fa577ff72f1b90"
source: "antigravity"
---

# Check Google Cloud Credits Balance

## User

how do I see how much money I have in credits?

---

## Assistant

To view your exact promotional credit balance or remaining pre-paid API credits, you'll need to check the **Google Cloud Console**, as the AI Studio dashboard only displays your current month's API spend and tier caps.  
Google

Step 1: Open the Google Cloud Console Credits Page

Go directly to the **Google Cloud Billing Credits Page**.  
Google

If prompted, select your billing account (e.g., **My Billing Account 1**).  
Google

Step 2: View Your Active Balances

On the **Credits** tab, you will see a table listing all active credits tied to your account, including:  
Google

**Remaining value** vs. **Original value**  
Google

**Expiration / End dates**  
Google

**Status** (*Available*, *Used*, or *Expired*)  
Google

Alternative: View Account Balance & Invoices

If you have a pre-paid balance or want to see current statement debits/credits:

Open the **Google Cloud Billing Overview**.

Look at the **Billing account overview** card on the right side to check your current account balance, pending payments, or available pre-paid funds.  
Google

---

## User

why am I seeing this with Hermes?

`Out of credits: HTTP 429: Gemini HTTP 429 (RESOURCE_EXHAUSTED): You exceeded your current quota, please check your plan and billing details. For more information on this error, head to: https://ai.google.dev/gemini-api/docs/rate-limits. To monitor your current usage, head to: https://ai.dev/rate-limit.




Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_paid_tier_input_token_count, limit: 2000000, model: gemini-3.6-flash`

---

## Assistant

The error message shows that Hermes is using the **Gemini API via Google Cloud Vertex AI (or Pay-as-you-go Gemini API key)**, which bills against your Google Cloud project's quotas rather than using standard promotional Developer Program credits.

Here is why this error is happening and where the disconnect is:

1. Daily / Monthly Token Quotas

The error specifies that you hit a hard limit on input tokens:

`Quota exceeded for metric: [generativelanguage.googleapis.com/generate_content_paid_tier_input_token_count](https://generativelanguage.googleapis.com/generate_content_paid_tier_input_token_count), limit: 2000000, model: gemini-3.6-flash`

Even though you have **$13.31** remaining in your Google Developer Program promotional credits, Google Cloud imposes separate **Rate Limits & Quotas** (such as a 2,000,000 input tokens/day limit for `gemini-3.6-flash` on that project/tier). Once you hit that 2M token mark in a single window, API calls return `HTTP 429 RESOURCE_EXHAUSTED` until the quota window resets, regardless of how much dollar balance or credit you have remaining.

2. Pay-as-You-Go vs. Pre-paid Balances

If Hermes is routing requests through a third-party gateway, proxy, or standard Gemini API key, the error `Out of credits` is a generic message returned by the client when it receives a 429 status code from Google.

How to Fix / Bypass This

**Wait for the Quota Window to Reset:**
Token-count quotas for Google Cloud Gemini metrics reset periodically (usually daily). You can view your current real-time quota usage on the **Google Cloud Quotas Page** by filtering for `generativelanguage.googleapis.com`.

**Request a Quota Increase:**

Go to **IAM & Admin** > **Quotas** in Google Cloud Console.

Search for `[generativelanguage.googleapis.com/generate_content_paid_tier_input_token_count](https://generativelanguage.googleapis.com/generate_content_paid_tier_input_token_count)`.

Select the metric for `gemini-3.6-flash` and click **Edit Quotas** to request a higher daily token limit.

**Switch Models Temporarily:**
If you need immediate access in Hermes, switch your model target to `gemini-1.5-flash` or `gemini-1.5-pro`, as they maintain independent token count buckets.

---

## User

look

---

## Assistant

Looking at your current Google Cloud Quotas page for the **ai-os** project, the exact bottleneck is clear:

You hit the **GenerateContent input token count limit per model per minute** for `gemini-3.6-flash`.

What's Happening

**The Quota:** Your project is capped at **2,000,000 input tokens per minute (TPM)** for `gemini-3.6-flash`.

**The Surge:** When Hermes threw that 429 error, your input token throughput spiked past 2,000,000 tokens within a rolling 60-second window.

**Current Status:** As seen on your screen, usage has already cooled back down to **54.05%** (~1.08M tokens/min). Because it's a per-minute limit rather than a daily cap, the HTTP 429 clears as soon as the rolling 60-second window drops back below 2M tokens.

How to Prevent Hermes From Triggering This

**Increase the Quota:**

On your current screen, click the three vertical dots `⋮` on the far right of the **GenerateContent input token count limit** row for `gemini-3.6-flash`.

Select **Edit Quota** and submit a request to bump the limit above 2,000,000 TPM.

**Adjust Hermes Context / History:**

If Hermes sends large file contexts, system prompts, or extensive chat histories on every turn, it quickly inflates input token counts per request. Trimming the active context window or enabling prompt caching (if supported by your setup) will significantly reduce TPM spikes.

---

## User

I can't increase it.

---

## Assistant

The error **"The new quota value must be between 0 and 2,000,000"** occurs because of how Google Cloud structures self-service quota editing versus formal quota increase requests:

**Self-Service Decreases Only:** The **Edit Quota** box on that specific side panel is designed to let you *cap* your quota below your project tier's hard limit (e.g., down to 1,000,000 to manage costs), not raise it above the maximum allowed threshold for your current project tier.

**Tier-Based Ceilings:** Your Google Cloud project (`ai-os`) is currently at the default **Paid Tier 1** ceiling for `gemini-3.6-flash`, which caps input throughput at **2,000,000 tokens per minute (TPM)**.

How to Raise the Limit

To go above 2,000,000 TPM, you need to upgrade your project's billing tier or submit a formal quota increase request:

Option 1: Automatic Tier Upgrades (Billing Activity)

Google Cloud automatically moves your project into **Tier 2** or **Tier 3** once your account reaches specific cumulative spending thresholds on Google Cloud services. Upgrading tiers automatically bumps your default TPM limits across Flash and Pro models without requiring manual form approval.

Option 2: Request a Quota Exception via Form / Support

If you need immediate headroom above 2M TPM:

Close the **Edit quota** slide-out panel on the right.

At the top of the **Quotas** page, look for the **Increase Requests** tab or click **Configurations** to enable **Quota Adjuster** (which automatically requests increases as usage grows).

If self-service requesting is grayed out for your tier, submit a request via **Cloud Customer Care Support** or through the **Google Cloud Quota Increase Request Form**.

Alternative Immediate Fixes for Hermes

Because 2,000,000 TPM is a **per-minute rolling window** rather than a daily cap:

**Add a Delay Between Tool Calls in Hermes:** Setting a short pause (e.g., 2–3 seconds) between agentic tool steps stops rapid multi-file reads from stacking 175k+ token contexts into a single 60-second burst.

**Truncate Context / Start a Fresh Session:** Compacting or resetting your Hermes thread drops your baseline context size, giving you drastically more request headroom within that 2M TPM window.

---
