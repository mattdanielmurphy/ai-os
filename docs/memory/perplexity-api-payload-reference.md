# Perplexity API Request Payload Reference & Schema Analysis

> **Captured Timestamp:** `2026-08-15T20:11:19-06:00`  
> **Source Endpoint:** `POST https://www.perplexity.ai/rest/sse/perplexity_ask`  
> **Protocol Version:** `2.18`

---

## 1. Raw Payload Snapshot

```json
{
    "attachments": [],
    "language": "en-US",
    "timezone": "America/Edmonton",
    "search_focus": "internet",
    "sources": [
        "web"
    ],
    "frontend_uuid": "f857d009-de60-4bcd-be5b-dfaafde76258",
    "mode": "copilot",
    "model_preference": "grok46medium",
    "is_related_query": false,
    "is_sponsored": false,
    "frontend_context_uuid": "ef13536c-91b2-4615-84fe-1fdce8c7dfe0",
    "prompt_source": "user",
    "query_source": "home",
    "is_incognito": false,
    "time_from_first_type": 841.8999999910593,
    "local_search_enabled": false,
    "use_schematized_api": true,
    "send_back_text_in_streaming_api": false,
    "supported_block_use_cases": [
        "answer_modes",
        "media_items",
        "knowledge_cards",
        "inline_entity_cards",
        "place_widgets",
        "finance_widgets",
        "sports_widgets",
        "news_widgets",
        "shopping_widgets",
        "jobs_widgets",
        "search_result_widgets",
        "inline_images",
        "inline_assets",
        "placeholder_cards",
        "diff_blocks",
        "inline_knowledge_cards",
        "entity_group_v2",
        "refinement_filters",
        "canvas_mode",
        "maps_preview",
        "answer_tabs",
        "price_comparison_widgets",
        "preserve_latex",
        "generic_onboarding_widgets",
        "in_context_suggestions",
        "pending_followups",
        "inline_claims",
        "unified_assets",
        "workflow_steps",
        "workflow_widgets",
        "navigation_results",
        "background_agents"
    ],
    "client_coordinates": null,
    "mentions": [],
    "dsl_query": "say hi",
    "skip_search_enabled": true,
    "is_nav_suggestions_disabled": false,
    "source": "default",
    "always_search_override": false,
    "override_no_search": false,
    "client_search_results_cache_key": "f857d009-de60-4bcd-be5b-dfaafde76258",
    "should_ask_for_mcp_tool_confirmation": true,
    "supports_tool_approval_modal": true,
    "browser_agent_allow_once_from_toggle": false,
    "force_enable_browser_agent": false,
    "supported_features": [
        "browser_agent_permission_banner_v1.1"
    ],
    "extended_context": false,
    "version": "2.18",
    "rum_session_id": "9816f967-7633-4c0e-968b-8af37c8f9bd1"
}
```

---

## 2. Key Learnings & Parameter Breakdown

### A. Verified Model Identifiers (as of 2026-08-15)
- **OpenAI GPT (Thinking / Terra)**: `"gpt56_terra_thinking"` *(OpenAI Next-Gen / Terra codename)*
- **Google Gemini 3.7 Flash (Thinking)**: `"gemini37flashthinking"`
- **Claude 3.7 Sonnet (Thinking)**: `"claude50sonnetthinking"`
- **xAI Grok (Thinking)**: `"grok46medium"` *(Preset to Medium thinking)*
- **Moonshot AI Kimi K3 (Thinking)**: `"kimik3thinking"`
- **Zhipu AI GLM-5.2**: `"glm_5_2"`
- **Sonar (Perplexity Default)**: `"turbo"`

### B. Follow-up Thread State Management
Captured from follow-up interaction (`2026-08-15T20:15:24-06:00`):
- `"query_source": "followup"`
- `"last_backend_uuid": "ca19773d-977f-4863-8f9c-3b58309a02e9"` (maintains backend conversational context)
- `"read_write_token": "a6560c57-9c5a-4bfa-aef4-e37c540626f7"` (session authorization token)
- `"followup_source": "link"`

### C. Local Browser Execution Flags
- `"is_local_browser_available": false`
- `"is_local_browser_allowed": false`
- `"browser_agent_allow_once_from_toggle": false`
- `"force_enable_browser_agent": false`

---

## 3. Verified Payloads Changelog

### Snapshot 2: Followup Query with Kimi K3 Thinking (`2026-08-15T20:15:24-06:00`)
```json
{
    "last_backend_uuid": "ca19773d-977f-4863-8f9c-3b58309a02e9",
    "read_write_token": "a6560c57-9c5a-4bfa-aef4-e37c540626f7",
    "attachments": [],
    "language": "en-US",
    "timezone": "America/Edmonton",
    "search_focus": "internet",
    "sources": [
        "web"
    ],
    "frontend_uuid": "776798f7-ea18-4df3-a1ca-f50ecb60048b",
    "mode": "copilot",
    "model_preference": "kimik3thinking",
    "is_related_query": false,
    "is_sponsored": false,
    "prompt_source": "user",
    "query_source": "followup",
    "is_incognito": false,
    "time_from_first_type": 3026.199999988079,
    "local_search_enabled": false,
    "use_schematized_api": true,
    "send_back_text_in_streaming_api": false,
    "supported_block_use_cases": [
        "answer_modes",
        "media_items",
        "knowledge_cards",
        "inline_entity_cards",
        "place_widgets",
        "finance_widgets",
        "sports_widgets",
        "news_widgets",
        "shopping_widgets",
        "jobs_widgets",
        "search_result_widgets",
        "inline_images",
        "inline_assets",
        "placeholder_cards",
        "diff_blocks",
        "inline_knowledge_cards",
        "entity_group_v2",
        "refinement_filters",
        "canvas_mode",
        "maps_preview",
        "answer_tabs",
        "price_comparison_widgets",
        "preserve_latex",
        "generic_onboarding_widgets",
        "in_context_suggestions",
        "pending_followups",
        "inline_claims",
        "unified_assets",
        "workflow_steps",
        "workflow_widgets",
        "navigation_results",
        "background_agents"
    ],
    "client_coordinates": null,
    "mentions": [],
    "skip_search_enabled": true,
    "is_nav_suggestions_disabled": false,
    "followup_source": "link",
    "source": "default",
    "always_search_override": false,
    "override_no_search": false,
    "should_ask_for_mcp_tool_confirmation": true,
    "supports_tool_approval_modal": true,
    "force_enable_browser_agent": false,
    "supported_features": [
        "browser_agent_permission_banner_v1.1"
    ],
    "extended_context": false,
    "is_local_browser_available": false,
    "is_local_browser_allowed": false,
    "version": "2.18",
    "rum_session_id": "9816f967-7633-4c0e-968b-8af37c8f9bd1"
}
```
