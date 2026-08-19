---
title: "DeepSeek Flash Image Capabilities"
date: "2026-08-11"
conversation_id: "e7c5f948e30cf4c5"
source: "antigravity"
---

# DeepSeek Flash Image Capabilities

## User

[SYSTEM CONTEXT & DIRECTIVES:

1. Primary User Vault: /Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/

2. Strict Media & Story Spoilers Directive: STRICT NO SPOILERS POLICY. You MUST NOT under any circumstances reveal plot twists, endings, key character fates, deaths, betrayals, secret identities, major narrative developments, or unreleased details for movies, TV shows, books, anime, games, or story-driven media. If asked about media, err heavily on the side of caution. Give zero hints or foreshadowing of major events unless the user explicitly requests spoilers with confirmation.

3. Tone, Sycophancy & Banned Buzzwords: No sycophantic praise or routine filler ("that's very insightful", "great question", "I understand..."). NEVER use banned buzzwords: "glitch in the matrix", "nuclear option", "final boss", "game changer", "level up", "cheat code", "you've hit on", "unlocking the potential".

4. Tool Call Directive: You can output JSON tool calls inside a ```tool_call codeblock. Schema: {"tool":"save_note","run_automatically":true,"args":{"title":"...","content":"..."}}. Set "run_automatically": true ONLY if the tool should execute immediately without user confirmation (e.g. proactive note-taking). Set to false if it's a suggested action for the user to trigger manually.

5. Fact-Checking Directive: When asked to verify/fact-check claims, perform Information Sufficiency Check, Source & Context Audit, and define Explicit Assumptions & Boundaries.

6. Local Environment & Tooling Rules: Default JS package manager is Bun (never npm/pnpm). Use ./tmp for local script files. Safe file removal via mv ~/.Trash/ (never rm).

7. No YouTube links in responses.]




[2026-08-11 00:22 MDT-6] [context to this point is 0]  does DeepSeek Flash really not have image capabilities?

---

## Assistant

**Yes, standard/base DeepSeek Flash is purely a text-only model**. Its native architecture (such as DeepSeek-V4-Flash) is a text-focused Mixture-of-Experts (MoE) model optimized for fast, low-cost text inference, long context windows, and code/reasoning performance.  
Hugging Face
+ 1

However, there are a few important nuances depending on how you are accessing the DeepSeek ecosystem:

**Base Model (Text-Only):** If you are calling the vanilla `deepseek-v4-flash` or `deepseek-v3` API endpoint directly from DeepSeek or standard inference providers (like DeepInfra, Fireworks, or OpenRouter), it only accepts text prompts. It cannot natively process, parse, or generate images.

**Dedicated Vision Models (`DeepSeek Vision` / `Janus`):** For multimodal tasks (documents, screenshots, diagrams, photos), DeepSeek provides dedicated vision variants (e.g., *DeepSeek V4 Vision* or the open-source *Janus* series) designed specifically to handle image inputs alongside text.  
Scale Xpert

**Community / Fine-Tuned Vision Adapters:** Third-party developers and platforms frequently attach vision encoders (like MoonViT) onto the DeepSeek Flash text backbone (e.g., `DeepSeek-V4-Flash-Vision`) to give the Flash model visual capabilities.  
Hugging Face

If your current pipeline or API call returns an error when sending image payloads to DeepSeek Flash, you need to route those queries to a dedicated multimodal model or a Flash-Vision adapter variant.

---

## User

[2026-08-11 00:25 MDT-6] [context to this point is 478]  is there any chance there's a local model vision adapter that I can use? On a macbook pro m2, 16gb ram. I've got gemini nano with chrome already installed... would that work? I mean it's dumb af so probably not?

---

## Assistant

There isn't a direct "vision adapter" you can drop onto a text model like DeepSeek Flash on Apple Silicon. Multimodal architectures tie the visual encoder (like ViT) directly into the model's projection layer during pre-training or instruction tuning, so you generally have to run a dedicated vision-capable model.

Regarding **Gemini Nano via Chrome**, it is **strictly text-in / text-out** via the `window.ai` Prompt API (designed for low-latency tasks like summarization, rewrite, and translation). It has no exposed vision/multimodal hooks.  
Google Gemini

Running a dedicated local vision model on a **MacBook Pro M2 with 16GB RAM** is completely feasible within unified memory constraints.

What Will Fit on Your 16GB M2

On a 16GB M2 Mac, macOS and system overhead leave roughly **9–11 GB of Unified Memory free** for inference. You need a vision model under 8B parameters quantized to 4-bit (Q4).

Top Picks for M2 / 16GB RAM
Model	Size (4-bit)	VRAM Footprint	Best For
**Qwen2.5-VL-7B**	~4.7 GB	~6.5 GB	**Best Overall:** OCR, dense document reading, code UI interpretation, and diagram parsing.
**Llama-3.2-Vision-11B**	~7.2 GB	~9.0 GB	**Best General Reasoning:** High visual understanding, but leaves little RAM headroom for other apps.
**Moondream2**	~1.8 GB	~2.5 GB	**Ultra-Fast & Lightweight:** Exceptional for quick image tagging and basic visual QA at high tokens/sec.
**MiniCPM-V 2.6**	~5.2 GB	~7.0 GB	**Strong Multimodal:** Excellent OCR and multi-image context capabilities.
Setup Options
Option 1: Ollama (Easiest API / CLI setup)

If you want an OpenAI-compatible local API endpoint (e.g., to hook into local tools or scripts):

Bash

```
# Best overall option for 16GB RAM:
ollama run qwen2.5-vl:7b

# Lightweight option if you want near-zero memory footprint:
ollama run moondream

```

Option 2: MLX (Best Performance on macOS)

Apple’s `mlx-vlm` library leverages Apple Silicon’s Unified Memory and Metal API much more efficiently than standard llama.cpp bindings, yielding significantly faster token output and visual processing times.

**Install MLX VLM:**

Bash

```
pip install mlx-vlm

```


**Run Inference via Python or CLI:**

Bash

```
mlx_vlm.generate \
  --model mlx-community/Qwen2.5-VL-7B-Instruct-4bit \
  --image /path/to/image.png \
  --prompt "Describe this image in detail and extract any text."

```

Option 3: Local GUI Apps

If you want a native UI for dragging-and-dropping images:

**LM Studio:** Offers MLX and Metal acceleration natively, allowing local execution of `Qwen2.5-VL` or `Llama-3.2-Vision` with image attachments.

**Jan:** A lightweight native desktop client with local API support.

Memory Management Strategy

When running a ~7B vision model (like `Qwen2.5-VL-7B`) on a 16GB Mac, keep heavy apps (like Docker containers or major browser tab collections) closed to prevent memory swapping to SSD. The M2 will give around **15–25 tokens/second** at Q4_K_M quantization.

---

## User

[2026-08-11 00:26 MDT-6] [context to this point is 1453]  yeah, that's gonna be, I think, too heavy to quickly spin up and down. I don't think it's too expensive to pay for a cheap vision adapter, right?

---

## Assistant

It is **virtually free** for typical usage. Paying for a cloud API vision route is vastly more practical than constantly loading a 5GB–7GB model into Unified Memory on an M2 Mac just to parse an occasional image.

What Cloud Vision Actually Costs

For small-to-medium multimodal tasks (extracting text from a screenshot, describing an image, or analyzing a diagram), image inputs are converted into visual "tiles" (tokens). A high-res image usually consumes between **200 and 1,000 tokens**.

Model	Input Cost / 1M Tokens	Output Cost / 1M Tokens	Approximate Cost Per Image
**Gemini 1.5 Flash**	$0.075	$0.30	**~$0.00005** (200 images per cent)
**GPT-4o-mini**	$0.15	$0.60	**~$0.0001** (100 images per cent)
**Claude 3.5 Haiku**	$0.80	$4.00	**~$0.001** (10 images per cent)

**Bottom Line:** You could process 1,000 screenshots through Gemini 1.5 Flash or GPT-4o-mini and spend less than **5 to 10 cents**.

How to Set Up a "Vision Adapter" for DeepSeek

Since DeepSeek Flash lacks built-in vision support, the standard pattern in application building or workflow automation is **fallback routing**:

**Text-only queries** → Sent directly to DeepSeek Flash (fast, hyper-cheap text processing).

**Queries with images** → Intercepted and routed to **Gemini 1.5 Flash** or **GPT-4o-mini**.  
OpenAI

Unified API Gateway

If you are using tools like Cursor, VS Code extensions, or custom CLI scripts, use an aggregator like **OpenRouter**:

Unified API key.

Automatically sends image payloads to a vision model (like `google/gemini-flash-1.5` or `openai/gpt-4o-mini`) while sending standard text to `deepseek/deepseek-chat`.

Zero setup overhead on your Mac, leaving your 16GB RAM completely free for your dev environment.

---

## User

[2026-08-11 00:39 MDT-6] [context to this point is 2037] what are you talkin gabout with OR unified API key?

---

## Assistant

**An API proxy or aggregator** (like OpenRouter) gives you **one API key and one base URL** to access hundreds of different models across every major AI provider.  
OpenRouter

Instead of managing separate accounts and API keys for OpenAI, Google, Anthropic, DeepSeek, and Qwen, you maintain a single balance and single key.

How It Solves Your Vision Problem

OpenRouter's API endpoint is 100% **OpenAI-compatible**. This means if an application, CLI tool, or VS Code extension expects an OpenAI API format, you just point its `baseURL` to OpenRouter and use your OpenRouter key.  
OpenRouter

1. Zero Extra Setup

You send the request to the exact same endpoint (`[https://openrouter.ai/api/v1/chat/completions](https://openrouter.ai/api/v1/chat/completions)`) regardless of which model processes it.

2. Simple Model Switching via String

To handle text-only tasks with DeepSeek, you set the model string to:
`deepseek/deepseek-chat`

When you need vision capabilities (OCR, screenshots, diagrams), you keep your code identical and simply change the model string to a vision-capable endpoint:  
OpenRouter

`google/gemini-flash-1.5`

`openai/gpt-4o-mini`

`qwen/qwen-2.5-vl-7b-instruct`

3. Automatic Auto-Routing

OpenRouter also offers dynamic router endpoints (like `openrouter/auto` or `openrouter/free`). If you send an image payload in your request payload (e.g. an `image_url` block), the system automatically detects the image and routes the prompt to a vision-capable model behind the scenes so the call doesn't fail.  
OpenRouter

Example Request Body
JSON

```
{
  "model": "google/gemini-flash-1.5",
  "messages": [
    {
      "role": "user",
      "content": [
        { "type": "text", "text": "What does this diagram show?" },
        { "type": "image_url", "image_url": { "url": "data:image/png;base64,..." } }
      ]
    }
  ]
}

```


It avoids keeping local models in memory or juggling half a dozen different subscriptions—you just pay pennies as you go across whatever model fits the specific prompt.

---

## User

[2026-08-11 00:40 MDT-6] [context to this point is 2718] what's the pareto frontier cheap vision capabilites model to use?

---

## Assistant

To define the **Pareto frontier** (the optimal trade-off curve between low cost, high visual capabilities, and fast response times), vision-capable models can be categorized based on their primary use cases:

The Pareto Frontier Summary
Tier / Role	Model	Input / Output (per 1M tokens)	Average Cost per Image	Pareto Strength
**#1 Overall Pareto Champion**	**Gemini 1.5 / 2.0 / 3 Flash**	~$0.075 - $0.30 / $0.30 - $1.50	**~$0.00005 - $0.0001**	**Best general capability per dollar.** Native multimodal context, unmatched OCR/diagram/document reading, massive context window.
**#2 Dense Structured / UI Data**	**Qwen2.5-VL-7B / 72B**	~$0.10 - $0.20 / $0.40 - $0.80	**~$0.00008**	**Best for OCR, UI code generation, & chart extraction.** Open-weight heritage with top-tier spatial/visual accuracy.
**#3 Easiest API / Dev Integration**	**GPT-4o-mini / GPT-5 Mini**	~$0.15 - $0.25 / $0.60 - $2.00	**~$0.0001**	**Best for strict JSON schema output from images.** Highly consistent instruction-following for basic image tasks.
1. The Overall Winner: **Google Gemini Flash Series**

For almost any generic vision task (reading text from a screenshot, interpreting complex architecture diagrams, analyzing photos, or reading multi-page PDFs), **Gemini Flash is the benchmark for value**.  
ClawRouters

**Why it dominates the curve:** Google pre-trains Gemini as natively multimodal rather than stitching a vision adapter onto a text LLM. This gives it spatial reasoning on par with flagship models while costing less than a penny per 50–100 images.

**Best used for:** Diagrams, PDF/document parsing, multi-image comparisons, and video frames.

2. The OCR & Code Winner: **Qwen2.5-VL**

If your visual tasks involve **extracting dense text, reading code off screens, or parsing UI layouts into HTML/React**, Alibaba’s **Qwen2.5-VL** hits an extremely efficient spot on the frontier.

**Why it dominates the curve:** It handles dynamic visual resolution natively (doesn't warp or overly compress wide/tall images) and rivals much larger models on visual document benchmarks. Hosted API prices on OpenRouter/Together/DeepInfra are near floor-level.

**Best used for:** Screenshot-to-code, technical blueprint reading, complex chart/graph data extraction.  
ClawRouters

3. The Instruction-Following Winner: **GPT-4o-mini**

If your visual prompt needs to enforce strict output formatting (e.g., "Extract product names from this photo and return valid JSON with specific key fields"), **GPT-4o-mini** is hard to beat.

**Why it dominates the curve:** While slightly more expensive per output token than Gemini Flash, its zero-shot reliability for structured outputs and function calls reduces prompt-retry waste.

**Best used for:** Categorization, visual data extraction into JSON, and structured tool calling.  
ClawRouters

Recommendation

**Default to Gemini Flash** via OpenRouter or Google's API as your primary vision workhorse. It provides ~90% of frontier model visual quality at ~1% of the cost.

If your workload is **purely OCR / code screenshots**, switch to **Qwen2.5-VL**.

Where to go from here:
Get a Bun/TypeScript helper for image fallback routing
Compare OCR accuracy on dense code screenshots

---

## User

[2026-08-11 00:44 MDT-6] [context to this point is 3793]  so my use case is screenshots in general of software. If it's OCR, I can use an OCR tool that I have on my Mac. So it's not just text. I'm thinking I use screenshots so rarely that I might as well just use 3Flash. But I still don't understand how to do the routing. Like on OpenRouter, AutoRouter looks like it just has a slider with quality on one side and cost on the other side. And then there's an allowed models text area that I can type in. And I can enable prevent overrides. And that's all I can do.

---

## Assistant

The UI on OpenRouter can make routing seem tricky, but the mechanism behind it is straightforward once broken down.

You actually have **two completely different ways** to route requests depending on whether you want OpenRouter to handle decisions automatically or handle them explicitly yourself in code/configuration.  
OpenRouter

Method 1: Let OpenRouter Do It Automatically (`openrouter/auto`)

OpenRouter's **Auto Router** acts as a smart classifier.  
OpenRouter

How it detects images

When `openrouter/auto` receives an API call, an internal meta-model analyzes the payload.

If the payload contains **only text**, it routes to a fast/cheap text model (like DeepSeek V4 Flash).

If the payload contains an **image array** (`"type": "image_url"`), OpenRouter's feature-filtering automatically discards text-only models and routes exclusively to vision-capable models (like Gemini 3 Flash, GPT-5.6 Luna, or Qwen2.5-VL).  
OpenRouter

How to configure the OpenRouter UI for this:

**Model ID:** Pass `openrouter/auto` as the `model` in your API requests.  
OpenRouter

**Quality vs. Cost Slider:** Leave this near the middle or slightly toward Cost. Since image models are inherently filtered, it won't pick a $0.00 text model for an image—it will pick the cheapest/best *vision* model available within that slider setting.

**Allowed Models (Optional):** If you *only* want it to ever touch DeepSeek Flash (for text) and Gemini Flash (for vision), type those two exact model slugs into the **Allowed Models** box:

`deepseek/deepseek-chat`

`google/gemini-3-flash-preview`

**Prevent Overrides:** Check this box so that if your code/client requests a model outside your allowed list, OpenRouter forces it back into your allowed pair.

Method 2: Client-Side Fallback Arrays (The "Explicit" Way)

If you don't trust `openrouter/auto` and want **100% control**, you don't use the Web UI sliders at all. Instead, you send a `models` array directly in your JSON API request payload:

JSON

```
{
  "models": [
    "deepseek/deepseek-chat",
    "google/gemini-3-flash-preview"
  ],
  "messages": [ ... ]
}

```

How OpenRouter executes this array:

It tries **Model #1** (`deepseek/deepseek-chat`).

If your message **has an image**, DeepSeek's server immediately rejects the request (because it's text-only).

OpenRouter intercepts that rejection instantly and **fails over to Model #2** (`google/gemini-3-flash-preview`).

If your message is **text-only**, Model #1 succeeds and Model #2 is never called.

Recommendation for Your Use Case

Since you're working with software screenshots occasionally, **Gemini 3 Flash** is ideal.

**If using an app like Cursor, TypingMind, or a local script:** Set the model name to `openrouter/auto`. In the OpenRouter web settings, restrict **Allowed Models** to `deepseek/deepseek-chat` and `google/gemini-3-flash-preview`. Text prompts will hit DeepSeek for near-zero cost, and screenshot prompts will seamlessly route to Gemini.  
OpenRouter

---

## User

[2026-08-11 00:45 MDT-6] [context to this point is 4754]  really, I just have to do this in light LLM because I think that's what I'm using for most things Running Hermes

---

## Assistant

If you're using **LiteLLM** (whether directly via its Python SDK, as a proxy server, or backed into your Hermes configuration), you don’t need to handle fallback logic manually in your code. LiteLLM handles model routing and fallbacks natively.  
LiteLLM

How to set this up depends on how you run LiteLLM:

1. LiteLLM Proxy / Hermes (`config.yaml`)

If you run LiteLLM as a local proxy server or feed a YAML configuration to Hermes, configure a **model fallback chain**.  
LiteLLM Docs

Define `deepseek/deepseek-chat` as your primary model, and list Gemini Flash (via OpenRouter or Google) as its fallback.

YAML

```
model_list:
  - model_name: deepseek-flash
    litellm_params:
      model: openrouter/deepseek/deepseek-chat
      api_key: os.environ/OPENROUTER_API_KEY

  - model_name: gemini-flash
    litellm_params:
      model: openrouter/google/gemini-flash-1.5
      api_key: os.environ/OPENROUTER_API_KEY

# Fallback Routing Rule
router_settings:
  fallbacks:
    - deepseek-flash: ["gemini-flash"]

```

What happens when you send a prompt:

LiteLLM sends the request to **DeepSeek Flash**.

If your prompt includes an image, DeepSeek’s API rejects it with an unhandled image/payload error.

LiteLLM catches that error instantly and reroutes the entire payload to **Gemini Flash**.

If it's pure text, DeepSeek handles it normally.

2. LiteLLM Python SDK (`fallbacks` parameter)

If Hermes or your custom scripts invoke LiteLLM programmatically via Python, pass the `fallbacks` list directly into `completion()` or `Router()`:

Python

```
from litellm import completion

response = completion(
    model="openrouter/deepseek/deepseek-chat",
    messages=[
        {
            "role": "user", 
            "content": [
                {"type": "text", "text": "What is in this screenshot?"},
                {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}}
            ]
        }
    ],
    fallbacks=["openrouter/google/gemini-flash-1.5"]
)

```

3. Dynamic Vision Check in LiteLLM

LiteLLM also exposes a built-in helper method, `litellm.supports_vision(model)`.  
LiteLLM

If your Hermes agent checks capabilities before dispatching:

`litellm.supports_vision("openrouter/deepseek/deepseek-chat")` → Returns `False`.

`litellm.supports_vision("openrouter/google/gemini-flash-1.5")` → Returns `True`.

Setting up the fallback array in LiteLLM keeps your environment lightweight while giving Hermes vision capabilities whenever a screenshot is attached.

---

## User

[2026-08-11 00:48 MDT-6] [context to this point is 5564]  wait, how does this work exactly? Is it, if it detects an image in the payload, then it sends the image and the whole prompt to Gemini?

---

## Assistant

**Yes, exactly.** LiteLLM uses **reactive error failover**.

Here is step-by-step how the data flows when an image is attached:

**LiteLLM receives the full payload:** It gets your prompt text alongside the base64/URL image block.

**First Attempt (Primary Model):** LiteLLM sends the **entire payload** to DeepSeek Flash.

**The API Rejection:** DeepSeek's API immediately throws an error (typically an HTTP 400 `BadRequestError` because it doesn't accept multimodal image inputs).

**The Fallback Intercept:** LiteLLM catches that 400 error before your code or Hermes sees a failure.  
LiteLLM

**Second Attempt (Fallback Model):** LiteLLM immediately re-packages the **exact same full payload** (the image + your text prompt) and forwards it to Gemini Flash.

**Execution:** Gemini Flash processes both the screenshot and the prompt, returning the response back to your application as if nothing went wrong.

The Key Takeaway

You **never need to write pre-parsing logic** in your scripts to inspect whether an image is attached.

You just craft your prompt naturally. If it's pure text, DeepSeek succeeds on Step 2. If a screenshot is included, DeepSeek fails fast on Step 3, and Gemini transparently takes over on Step 5.

---

## User

[2026-08-11 00:50 MDT-6] [context to this point is 5949]  I don't want that because Gemini is not going to have the same calf. So if we're deep in a thread and I take a screenshot and say something or give an instruction, Gemini Flash isn't going to have the context to be able to answer that question. What I would like is for Gemini Flash to just describe the image in great detail and give that textual description to Deep Seek.

---

## Assistant

That makes total sense. If you just bounce the whole thread over to Gemini when an image appears, you lose the primary conversation context and the prompt caching benefits of your main thread with DeepSeek.

What you're describing is a **Vision Preprocessing Pipeline** (a "describe-and-swap" interceptor).

Instead of routing the whole prompt away from DeepSeek, you intercept the incoming request payload right before dispatching, pull out the raw screenshot, send *just* the screenshot to Gemini Flash to generate a detailed textual description, and then **swap the raw image bytes in your payload for that text description**. Then the original thread proceeds straight to DeepSeek without breaking context.

The Preprocessing Flow

**Incoming Hermes/LiteLLM Payload:** Contains previous chat history + user prompt + `<raw screenshot base64>`.

**Interceptor Logic:**

Detects if any message in the payload contains an `image_url` or image object.

If **No Image:** Sends the payload straight to DeepSeek Flash as normal.

If **Image Found:**

Extracts the image.

Fires a quick isolated single-turn call to **Gemini Flash**: *"Provide a precise, highly detailed visual description of this software UI screenshot, including all visible text, UI elements, active focus, line numbers, and terminal output."*

Replaces the `image_url` object in the user's message with a formatted text block: `[Image Description from Gemini Flash: <description>]`.

**Dispatch:** Sends the mutated, 100% text payload (with full thread history intact) to **DeepSeek Flash**.

Implementation Options

Depending on how your system is set up, here are two simple ways to implement this:

Option A: TypeScript / Python Middleware (If wrapping Hermes or calling via script)

If you have a hook or wrapper around your LLM completion function:

TypeScript

```
import { completion } from "litellm";

async function processChatRequest(messages: any[]) {
  // 1. Inspect the last user message for image attachments
  const lastMsg = messages[messages.length - 1];
  
  if (Array.isArray(lastMsg.content)) {
    const imageBlock = lastMsg.content.find((item: any) => item.type === "image_url");
    
    if (imageBlock) {
      // 2. Send JUST the image to Gemini Flash for a quick textual description
      const visionResponse = await completion({
        model: "openrouter/google/gemini-flash-1.5",
        messages: [
          {
            role: "user",
            content: [
              { 
                type: "text", 
                text: "Describe this software screenshot in detail for a developer text model. Focus on code, terminal text, active UI components, and layout." 
              },
              imageBlock
            ]
          }
        ]
      });

      const imageDescription = visionResponse.choices[0].message.content;

      // 3. Mutate the message content: replace image with the textual description
      lastMsg.content = lastMsg.content.map((item: any) => {
        if (item.type === "image_url") {
          return {
            type: "text",
            text: `\n\n[Attached Screenshot Visual Context:\n${imageDescription}\n]`
          };
        }
        return item;
      });
    }
  }

  // 4. Send the fully textual payload (with history) to DeepSeek Flash
  return await completion({
    model: "openrouter/deepseek/deepseek-chat",
    messages: messages
  });
}

```

Option B: LiteLLM Custom Guardrail / Hook (If running LiteLLM Proxy)

If you're running LiteLLM as a proxy server in front of Hermes, you can write a short custom pre-call hook (`litellm_pre_call_hook`) in Python:

Python

```
from litellm.integrations.custom_logger import CustomLogger
import litellm

class VisionPreprocessor(CustomLogger):
    async def async_pre_call_hook(self, user_api_key_dict, cache, data, call_type):
        messages = data.get("messages", [])
        for msg in messages:
            if isinstance(msg.get("content"), list):
                new_content = []
                for part in msg["content"]:
                    if part.get("type") == "image_url":
                        # Get text description from Gemini Flash
                        vision_res = await litellm.acompletion(
                            model="openrouter/google/gemini-flash-1.5",
                            messages=[{
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": "Describe this software screenshot in precise technical detail."},
                                    part
                                ]
                            }]
                        )
                        desc = vision_res.choices[0].message.content
                        new_content.append({
                            "type": "text", 
                            "text": f"\n[Screenshot Description: {desc}]\n"
                        })
                    else:
                        new_content.append(part)
                msg["content"] = new_content
        return data

# Register the hook in LiteLLM
litellm.callbacks = [VisionPreprocessor()]

```

Why this works so much better:

**Preserves Thread Context:** DeepSeek retains 100% of the past conversation history.

**Low Cost:** The call to Gemini Flash uses virtually no input/output tokens because it's a isolated single-turn image request (costs less than $0.00005 per screenshot).

**Zero Image Failures:** DeepSeek Flash never receives a multimodal object, so it will never throw a `400 Bad Payload` or missing vision capabilities error.

---

## User

[2026-08-11 00:50 MDT-6] [context to this point is 7791]  i'm actually using Hermes web UI. Can you just check if maybe there's a plugin or even a native feature for this?

---

## Assistant

Hermes Agent handles images in this manner **natively out of the box**.  
Hermes Agent - nous research

The feature is built into the core agent pipeline via an auxiliary tool called **`vision_analyze`**.  
Hermes Agent - nous research

How Hermes Handles Non-Vision Models Automatically

When you paste or attach an image into the Hermes Web UI (or CLI) while using a text-only model like DeepSeek Flash:

**Capability Detection:** Hermes checks the provider metadata for your active model and detects that DeepSeek Flash cannot process raw multimodal image blocks.  
Hermes Agent - nous research

**Auxiliary Intercept:** Instead of sending raw image bytes to DeepSeek (which would trigger a payload error) or bouncing your entire chat thread to another model, Hermes automatically routes *only the image* to its built-in **`vision_analyze`** tool.  
Hermes Agent - nous research

**Text Description Injection:** The auxiliary vision model inspects the screenshot, generates a textual description, and injects that description directly into your conversation context as text.  
Hermes Agent - nous research

**Primary Model Dispatch:** DeepSeek Flash receives your complete conversation history along with the textual description of the screenshot.

Configuration

If you're using a multi-provider setup or OpenRouter through Hermes, ensure your Hermes configuration (`~/.hermes/config.yaml` or your `.env`) has access to at least one vision-capable model in its provider catalog (such as Gemini Flash or GPT-4o-mini).  
nous research

Hermes automatically selects an available vision-capable endpoint from your configured providers to run `vision_analyze` whenever a text-only model receives an image attachment.  
Hermes Agent - nous research

---
