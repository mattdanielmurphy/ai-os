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

### A. Model Identifier
- **Grok Internal Name**: `"model_preference": "grok46medium"`
- Note: Sonnet Thinking is `"claude50sonnetthinking"`, Sonar is `"turbo"`.

### B. Agentic & Tooling Capabilities
- **MCP & Tool Approval**:
  - `"should_ask_for_mcp_tool_confirmation": true`
  - `"supports_tool_approval_modal": true`
  Perplexity natively has parameters for MCP tool approval and confirmation dialogs.
- **Browser Agent Integration**:
  - `"browser_agent_allow_once_from_toggle": false`
  - `"force_enable_browser_agent": false`
  - `"supported_features": ["browser_agent_permission_banner_v1.1"]`

### C. Advanced SSE Block Types (`supported_block_use_cases`)
New blocks exposed in version 2.18:
- `"background_agents"`: Background subagents / asynchronous task runs.
- `"workflow_steps"`, `"workflow_widgets"`: Multi-step execution pipelines.
- `"canvas_mode"`: Interactive canvas / artifact rendering.
- `"price_comparison_widgets"`, `"jobs_widgets"`: Domain-specific interactive widgets.
- `"navigation_results"`, `"maps_preview"`: Geo-spatial and navigation widgets.

### D. Anti-Bot / Timing Telemetry
- `"time_from_first_type"`: Measures user typing latency in milliseconds (`841.89ms`). Automated engines should randomize this value between 500ms–2500ms to avoid synthetic pattern flags.
- `"client_search_results_cache_key"` & `"frontend_uuid"`: Match the client-generated UUID for deduplication.
- `"rum_session_id"`: Real User Monitoring session tracking UUID.
