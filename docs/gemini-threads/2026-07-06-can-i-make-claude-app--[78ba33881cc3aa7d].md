---
title: "can I make Claude.app connect to litellm?"
date: "2026-08-13"
source: "gemini.google.com"
conversation_id: "75700f17-05dc-5aa0-a4ce-028e6bd8fe78"
url: ""
---

# can I make Claude.app connect to litellm?

> [!NOTE]
> Archived Gemini Thread: [can I make Claude.app connect to litellm?]() | Date: 2026-08-13

## User

can I make Claude.app connect to litellm?

---

## Gemini

Yes, you can. Claude Desktop (Claude.app on macOS) recently introduced the ability to connect to custom API endpoints and third-party inference gateways.


Since LiteLLM can act as an Anthropic-compatible proxy (translating requests from the Anthropic Messages format to whatever backend model you want to use), you can route your desktop traffic through it.


You have two main ways to configure this on macOS:


Method 1: Via Developer Mode (GUI)
LiteLLM now natively supports direct integration with Claude Desktop via the UI:



* Open Claude Desktop.

* Go to the top menu bar and select Help → Claude → Help, then click Enable Developer Mode.

* Click the Claude menu bar/status icon, hover over Developer, and select Configure Third-Party Inference.

* In the dialog that opens, configure your settings:

* Gateway URL: Enter your LiteLLM Proxy URL (e.g., http://localhost:4000 or your hosted gateway address).

* API Key: Enter your LiteLLM Virtual Key or Master Key.




* Save and restart Claude Desktop.



Method 2: Via Terminal Environment Variables
If you prefer bypassing the UI settings, you can launch the app from your terminal by overriding the base API URL directly.



* Ensure your LiteLLM proxy instance is running.

* Open your terminal and export the routing variables before launching the application:
export ANTHROPIC_BASE_URL="http://localhost:4000"
export ANTHROPIC_AUTH_TOKEN="your-litellm-virtual-key"
open -a "Claude"





⚠️ A Quick Gotcha with Desktop Proxies: Claude Desktop frequently utilizes hidden sub-agents or background system prompts for complex features like Artifacts or Projects. If LiteLLM doesn't recognize the exact versioned model names Claude Desktop targets (e.g., claude-3-5-sonnet-...), it might return a "model not found" error. To prevent this, ensure your litellm_config.yaml explicitly maps those exact Anthropic model strings to your fallback upstream models.

---

## User

in the Developer page of settings it just says local MCP Servers

---

## Gemini

That happens because you are likely already signed into your Anthropic account in the app. When you are logged in, Claude Desktop hides the third-party gateway settings and only shows MCP options.


To make the Configure Third-Party Inference option appear, you have to access it from the login screen:


The Login Screen Method

* Open Claude Desktop, click your profile icon or the menu, and Log Out.

* Once you are back on the main login/sign-in screen, go to the macOS top menu bar.

* Select Help → Troubleshooting → Enable Developer Mode.

* Now, click the Developer menu item that appears in the top menu bar—you should see Configure Third-Party Inference... right alongside the MCP options.



The Direct Config File Method (If the UI is being stubborn)
If you don't want to log out or the menu still won't play nice, you can force Claude Desktop to look at LiteLLM by manually creating or editing its global configuration file.


On macOS, Claude Desktop's app settings are stored as managed preferences. You can write the LiteLLM gateway details straight into your user preferences via the Terminal:


# 1. Set the provider to use a custom gateway
defaults write com.anthropic.claudefordesktop inferenceProvider "gateway"

# 2. Point it to your local LiteLLM instance
defaults write com.anthropic.claudefordesktop inferenceGatewayBaseUrl "http://localhost:4000"

# 3. Set the auth scheme to bearer token
defaults write com.anthropic.claudefordesktop inferenceGatewayAuthScheme "bearer"

# 4. Add your LiteLLM virtual key
defaults write com.anthropic.claudefordesktop inferenceGatewayApiKey "your-litellm-virtual-key"

(If your LiteLLM setup uses X-API-Key headers instead of a Bearer token, change the auth scheme line to "x-api-key".)


Once you run those commands and restart Claude Desktop, it will completely bypass the standard Anthropic login screen and route all traffic directly through your LiteLLM proxy.

---

