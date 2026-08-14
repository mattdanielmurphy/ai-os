---
title: "How can I set up a marketplace bot to periodically scrape ma"
date: "2026-08-13"
source: "gemini.google.com"
conversation_id: "fe65f056-396f-5365-968c-61f19f89e03e"
url: ""
---

# How can I set up a marketplace bot to periodically scrape ma

> [!NOTE]
> Archived Gemini Thread: [How can I set up a marketplace bot to periodically scrape ma]() | Date: 2026-08-13

## User

How can I set up a marketplace bot to periodically scrape marketplace for listings and give that to an LLM to identify great deals?

---

## Gemini

Setting up an automated system to scrape Facebook Marketplace and analyze deals using a Large Language Model (LLM) involves three primary phases: scraping, processing/filtering, and LLM evaluation.


Because Facebook aggressively blocks standard automated scrapers, your architectural choices are critical.



1. The Scraping Layer
Standard request libraries (requests, BeautifulSoup) generally fail on Facebook Marketplace due to dynamic JavaScript rendering and strict anti-bot measures. You will need a browser automation tool.


Option A: Playwright or Puppeteer (Self-Hosted)

* How it works: Runs a headless Chromium instance to mimic a real user.

* Setup:

* Use Playwright (Python/Node.js) to navigate to the specific Marketplace search URL with your filters pre-applied (e.g., radius, price cap).

* Implement human-like behavior: randomize wait times, simulate mouse scrolls to trigger lazy loading, and use a realistic User-Agent.

* Extract the raw HTML or target specific CSS selectors (like item titles, prices, locations, and links).





Option B: Scraping APIs (Low Maintenance)

* How it works: If you want to bypass proxy management, CAPTCHAs, and constant selector updates, you can use structured data scraping APIs (like Crawlbase, ScrapingBee, or ZenRows). They handle proxy rotation and return the rendered HTML or structured JSON.



2. Data Parsing & Filtering
Before sending data to an LLM, you must clean it to minimize token costs and noise.



* Extract Key Fields: Parse the scraped HTML into a structured format (JSON or a Pandas DataFrame) containing only essential data:
{
  "title": "Art Lutherie Cherry Folk Guitar",
  "price": "CA$150",
  "location": "Fort Saskatchewan, AB",
  "description": "Needs strings, comes with case and stand."
}



* Pre-Filter: Do not send obviously irrelevant listings to the LLM. Filter out listings that don't match basic numerical criteria (e.g., if you are only looking for cars under $5,000, drop everything else via code first).



3. The LLM Evaluation Pipeline
Once you have a clean list of items, you pass them to the LLM to assess market value and detect anomalies (underpriced gems).


The Prompt Design
To get consistent results, instruct the LLM to act as an expert appraiser and force a structured JSON output.



System Prompt Example:
"You are an expert market analyst specializing in secondhand goods. Analyze the provided marketplace listings. Estimate the typical fair market value based on your knowledge. If the listed price is significantly lower than fair market value (a great deal), flag it as 'TRUE' and provide a brief rationale."



Automation Workflow

* Batching: Send 5–10 listings at a time to the LLM (e.g., gpt-4o-mini or Claude 3.5 Haiku to keep costs low) to analyze simultaneously.

* Parsing Output: Have your script read the LLM's JSON response. If is_great_deal equals true, trigger a notification.



4. Automation & Notifications
To make it a true periodic "bot," wrap your script in a scheduler and a notification engine.



* Scheduling: Use a simple Cron job (Linux/Mac) or Task Scheduler (Windows) to run the script every 30 or 60 minutes. Running it too frequently increases the risk of your IP being flagged by Facebook.

* State Management: Keep a local database or a simple text file tracking previously seen listing IDs so you only process and alert on new listings.

* Alerts: Use webhooks to send great deals instantly to your personal Discord server, Telegram bot, or Slack workspace.



⚠️ A Note on Anti-Bot Safeguards
Facebook uses advanced behavioral analysis. To prevent your scraper from getting blocked immediately:



* Avoid Logging In: If possible, scrape public Marketplace URLs without logging into a personal Facebook account. Scraping while logged in risks getting your account banned.

* Use Residential Proxies: If running frequently, route your Playwright/Puppeteer traffic through a rotating residential proxy network.

---

## User

I'm thinking I'd run the scraper on my Oracle VPS

---

## Gemini

Running this on a cloud VPS like Oracle Cloud Infrastructure (OCI) is a great choice because it gives you a dedicated static IP and allows for continuous 24/7 background operation. However, there are a few important technical configurations and constraints to keep in mind when deploying a headless browser scraper on a VPS.



1. Environment Headless Dependencies
Oracle Linux or Ubuntu Server images do not come with the graphical libraries required to run Chromium or Firefox.


If you use Playwright, you can easily install all the required system dependencies and browser binaries with a single command once your project is initialized:


# Install playwright dependencies (Run this on your VPS)
playwright install-deps
playwright install chromium

If you are using Docker to deploy your bot, it is highly recommended to use the official Playwright Docker image (mcr.microsoft.com/playwright) as your base. This completely eliminates "missing .so library" errors on headless servers.



2. IP Reputation and Proxy Needs
This is your primary bottleneck on a free or cheap VPS tier:



* The Problem: Oracle Cloud IP ranges (like AWS, DigitalOcean, and GCP) are publicly documented and heavily flagged by Facebook's anti-bot systems (like Akamai or Cloudflare). If you try to fetch Facebook Marketplace directly from an Oracle data center IP, you will likely hit immediate CAPTCHAs, blank pages, or login walls.

* The Solution: You must route your script's browser traffic through residential proxies.

* In Playwright, you pass the proxy server directly into your browser launch context:
browser = await playwright.chromium.launch(
    proxy={
        "server": "http://your-proxy-provider.com:8000",
        "username": "your_username",
        "password": "your_password"
    }
)








3. Resource Allocation (OCI Compute Shapes)
If you are utilizing Oracle's "Always Free" Ampere (ARM64) or AMD shapes, monitor your memory usage:



* Headless browsers are notoriously memory-hungry. A single Chromium instance can easily eat up 500MB to 1GB of RAM while rendering heavy, image-laden infinite-scroll timelines like Marketplace.

* Ensure you explicitely close the browser context (await browser.close()) at the end of every execution loop to prevent memory leaks from crashing your VPS.

* If you use an ARM64 Ampere shape, ensure your proxy provider and any third-party node packages fully support aarch64 architecture.



4. Keeping it Alive
To ensure your script runs indefinitely without needing your terminal window open, do not run it with a simple python script.py. Instead, use a process manager like PM2 or a system service:


Option A: PM2 (Recommended for Node/Python)
npm install pm2 -g
pm2 start script.py --cron "*/30 * * * *" --no-autorestart

(This tells PM2 to run your scraping script exactly every 30 minutes, keeping track of logs and failures without keeping your SSH session active).


Option B: Systemd Service
Create a standard systemd service profile (/etc/systemd/system/marketplace-bot.service) paired with a systemd timer to handle execution intervals cleanly.

---

## User

I've been thinking about this. I'd rather not have to pay for the AI API calls. I wonder if I could run my scraper on my VPS, commit all the scraped data to my github, and then have Google Jules analyze the data and identify good buys.

---

## Gemini

Using GitHub as a bridge to pull data into a Google workspace or AI tool is a creative way to try and keep everything free, but you are going to run into a major bottleneck with Google Jules.


Jules is a developer-focused assistant integrated directly into Google Cloud and its development environments (like Project IDX or Gemini Code Assist). It isn't designed to act as an automated, background data-processing pipeline or an autonomous bot that watches a repository to generate consumer alerts.


That said, you can absolutely still achieve a 100% free workflow using your Oracle VPS and GitHub. Instead of Jules, you can leverage free-tier production AI models that are actually built for automation.


Here is how you can restructure the pipeline to keep it completely free.



The Free Alternative Pipeline
[Oracle VPS Scraper] 
       │
       ▼ (Filters & Formats)
[GitHub Repository] 
       │
       ▼ (Triggers)
[GitHub Actions (Free)] ───> [Free-Tier AI API] ───> [Discord/Telegram Alert]

1. The GitHub Repo (Your Data Store)
Your script on the Oracle VPS runs, scrapes Marketplace, and handles the initial filtering.



* It formats the new listings into a clean JSON file (e.g., listings.json).

* It commits and pushes this file to a private GitHub repository.


2. GitHub Actions (The Free Compute Engine)
Instead of relying on an interactive chat tool to read your repo, you can use GitHub Actions, which gives you up to 2,000 free automation minutes per month on standard accounts.



* You can configure a GitHub Action workflow that triggers automatically every time you push new data to the repository.

* The Action runner spins up, reads the new JSON data, and sends a single payload to a free-tier AI model.


3. The Free AI Tier (Replacing Jules)
Several highly capable LLM providers offer completely free API tiers that easily handle a project of this scale:



* Google AI Studio (Gemini 2.5 Flash / 1.5 Flash): Google’s official developer platform offers a generous free tier (typically 15 RPM / 1,500 RPD). Gemini 1.5/2.5 Flash is incredibly fast, features a massive context window, and is perfect for parsing structured JSON data to find deals.

* Groq Cloud: Offers free access to open models like Llama 3 with incredibly high speeds and a generous free rate limit layer.


Because your script pre-filters the data, you will only be making a few calls an hour, staying well within the free limits.



How the Free Script Looks (GitHub Action)
Instead of manually asking an assistant to read your repo, a simple Python script inside your GitHub Action can handle the evaluation and send the deal directly to your phone:


import os
import json
import google.generativeai as genai
from discord_webhook import DiscordWebhook

# Configure Free Gemini API
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# Load the data pushed by your VPS
with open("listings.json", "r") as f:
    listings = json.load(f)

prompt = f"Analyze these marketplace listings and return a JSON list of items that are priced significantly below market value: {json.dumps(listings)}"

response = model.generate_content(prompt)
deals = json.loads(response.text)

# If a great deal is found, ping your personal Discord/Telegram
for deal in deals:
    if deal.get("is_great_deal"):
        webhook = DiscordWebhook(url=os.environ["DISCORD_WEBHOOK_URL"], content=f"🚨 DEAL FOUND: {deal['title']} for {deal['price']}!")
        webhook.execute()

Why this beats trying to use Jules

* True Automation: You don't have to open a browser window, paste data, or prompt an AI manually. The system runs silently in the background 24/7.

* Immediate Alerts: The moment your VPS finds a listing, GitHub Actions processes it via the Gemini API, and a notification hits your phone within a couple of minutes.

* Zero Cost: By combining the Oracle Free Tier, GitHub Actions' free compute minutes, and Google AI Studio's free API limits, your monthly operating cost remains exactly $0.

---

## User

[2026-06-30 21:47 MDT-6] best ai API free tiers for various tasks

---

## Gemini

If you are looking for permanent or highly usable free tiers rather than brief trial credits that expire in a couple of weeks, the API ecosystem offers several excellent choices tailored to specific tasks.


Here are the best free-tier AI APIs categorized by their strengths:


1. Best for Aggregation & Multi-Model Flexibility: OpenRouter
If you want to build or experiment without managing dozens of API keys, OpenRouter is the cleanest starting point.



* The Deal: Access to over 20+ free, open-weight models through a single, unified OpenAI-compatible API.

* Key Restrictions: 20 Requests Per Minute (RPM); 50 Requests Per Day (RPD) by default, though this scales up significantly (to 1,000/day) if you ever choose to add a small credit top-up. No credit card is required to use the base free tier.

* Best For: Prototyping, evaluating different models side-by-side, and rapid experimentation without vendor lock-in.


2. Best for Long-Context & Native Multimodality: Google AI Studio (Gemini)
Google’s free tier via AI Studio remains incredibly generous for developer exploration, specifically when handling massive amounts of data.



* The Deal: Free access to models like Gemini 3.5 Flash and Gemini 3.1 Flash-Lite. These models natively support massive context windows (up to 1 million tokens or more) and excel at multimodal tasks (text, audio, video, and images).

* Key Restrictions: 5 to 15 RPM and up to 1,500 RPD depending on the specific model and project configuration. Note that outside the EU/UK/EEA, data sent through the free tier may be used for model training.

* Best For: Multi-minute video analysis, processing entire codebases or massive PDF textbooks, and building complex multimodal pipelines.


3. Best for Extreme Speed & Voice Agents: Groq
Groq serves open-weight models using their proprietary Language Processing Unit (LPU) hardware, which clocks in at blistering speeds (often 400 to 500+ tokens per second).



* The Deal: Permanent free access to frontier open models like Llama 3.3 70B (for complex reasoning) and Llama 3.1 8B (for lightweight tasks). No credit card required.

* Key Restrictions: 30 RPM. The 8B model offers a generous 14,400 RPD, while the 70B model caps out at 1,000 RPD.

* Best For: Applications where ultra-low latency is required, such as real-time conversational bots, interactive CLI utilities, or instant-response user interfaces.


4. Best for Evaluation of Proprietary Frontier Models: GitHub Models
If you want free access to top-tier commercial models that normally require a paid subscription from the start, GitHub provides a stellar developer playground.



* The Deal: Free API endpoints for models like GPT-4o and Claude 3.5 Sonnet, alongside leading open weights.

* Key Restrictions: Roughly 15 RPM and a cap of 150 to 1,000 RPD depending on the model tier. It is strictly designed for playground testing and prototyping, not production deployment.

* Best For: Testing how an application behaves against industrial gold-standard reasoning models before committing to a paid architecture.


5. Best for High-Volume Text & Code Processing: Mistral AI
Mistral offers an "Experiment" tier via their La Plateforme console that is incredibly permissive on sheer token volume.



* The Deal: Free access to Codestral (excellent for coding tasks) and their core Mistral model family.

* Key Restrictions: Delivers roughly 1 billion tokens per month, making it one of the largest pure token allocations available on a free tier, though rate limits can vary dynamically.

* Best For: Heavy coding assistant backend scripting, local developer workflow automation, and processing large volumes of text asynchronously.


6. Best for Specialized Tasks (Audio & Image Media)

* Speech-to-Text: Groq provides free access to Whisper v3 Turbo. You get 2,000 requests per day and a massive 7,200 audio seconds per hour—meaning you can process roughly two hours of audio for every hour of real-time clock speed.

* Open-Source Model Exploration: Hugging Face Serverless Inference API gives you rate-limited community access to test out hundreds of thousands of niche, specialized open-source models (including tokenizers, embeddings, and classification models) without spinning up infrastructure.


Key Tips for Navigating Free Tiers:

* Watch the Project Quotas: For providers like Google and Groq, rate limits apply at the organization/project level, not per API key. Generating five separate keys inside the same account won't bypass the limits.

* Implement Backoff: Always wrap free tier integrations in basic retry logic with exponential backoff, as free tiers are more prone to temporary 429 Too Many Requests or resource exhaustion errors during high global traffic.

---

## User

[2026-06-30 22:13 MDT-6] Just had an idea. I'm a developer. But I've gotten so used to agentic coding that I'm really rusty and I barely ever do ANYTHING by hand. Even stuff that's easy to do. When I do try and dig in, I find it takes me SO long to find the relevant code and change it properly to accomplish what I want.
But I just realized something: I can just ask the AIs coding on the project to add a really robust system to I can edit all the relevant parameters for a project. Basically I'd have a simple interface (a JSON file say) with tons of parameters used in a project, like UI spacing, colors, etc, and I can edit them trivially and instantly see the results, rather than changing some variable somewhere in the code and hoping for the best.

---

## Gemini

That is a highly practical shift in perspective. Moving the levers of your application out of the codebase and into a structured configuration file—especially when working alongside agentic tools—is an excellent way to reclaim immediate, predictable control without getting bogged down in file navigation.


When you offload the heavy lifting to an AI agent, having a centralized data structure becomes incredibly powerful for a few reasons:


1. It Establishes a "Source of Truth"
Instead of letting an agent scatter hardcoded values across multiple files, components, or styles, you force the AI to build the architecture around a single, highly readable configuration file. This keeps the codebase incredibly clean and predictable.


2. Trivial Context Verification
When you want to tweak something yourself, you don't have to grep through a dozen files or remember the exact syntax of a framework's layout system. You open one file, change a numeric value or a string, and let your hot-reloading environment handle the rest.


3. Clear Boundaries for the AI
It creates a perfect division of labor. The AI agent handles the structural logic, the data parsing, and the underlying plumbing. You maintain absolute veto power over the behavioral and visual nuance by owning the configuration data.



Implementing the Strategy Effectively
To make this work seamlessly with an agentic workflow, you might want to consider a few design choices:



* Use a Schema for Guardrails: If you use JSON, pairing it with a JSON Schema (or using a TypeScript as const definition if your project allows) ensures that both you and the AI know exactly what parameters are allowed, their types, and their valid ranges.

* Leverage Hot-Reloading: Ensure your app's state management or styling solution reads this file reactively. If you are tweaking UI spacing or behavioral constants, you want that instant feedback loop without full rebuilds.

* Categorize Early: Structure the file logically from the start so it doesn't turn into a massive, flat list of hundreds of keys.


{
  "theme": {
    "spacing": {
      "paddingSmall": 8,
      "paddingMedium": 16,
      "layoutGap": 24
    },
    "colors": {
      "accent": "#007acc"
    }
  },
  "behavioralDefaults": {
    "animationDurationMs": 300,
    "maxRetryAttempts": 3
  }
}

By having the agent build the parsing logic into the application up front, you transform your role from a developer hunting down lines of code into a high-level systems director.


What specific project or parameters are you thinking of targeting with this approach first?

---

