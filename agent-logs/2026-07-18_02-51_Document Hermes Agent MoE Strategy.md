## Goal
Document the strategy and architecture decisions for Hermes Agent integration, including forking vs. not forking and a Mixture of Experts (MoE) triage system.

## User Feedback & Decisions
- Resolved conflation with Claude Code: the discussion is about Nous Research's open-source Hermes Agent.
- Decided not to fork the Hermes Agent project to preserve upstream update capabilities.
- Sticking with a Model Context Protocol (MCP) boundary to manage context size and routing.
- Conceptualized a quota-aware Mixture of Experts (MoE) triage engine behind the MCP boundary.

## Changes Made
- Created [hermes-agent-integration.md](file:///Users/matt/Library/Mobile%20Documents/iCloud~md~obsidian/Documents/Personal/Development/Project%20Notes/hermes-agent-integration.md) in the Obsidian vault documenting the forking rationale and MoE routing.
- Updated [Project Index.md](file:///Users/matt/Library/Mobile%20Documents/iCloud~md~obsidian/Documents/Personal/Development/Project%20Notes/Project%20Index.md) to index the new note.

## What Worked
- Formulated MoE diagram and strategy.
- Cleanly cataloged choices in Obsidian.

## What Didn't Work / Known Issues
- N/A

## Architecture Notes
- The MCP server acts as an isolation barrier, protecting the parent agent's context from raw execution logs.
- Forking is not required to implement a complex model-routing strategy; the logic can live inside the custom MCP server.

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity/brain/24839105-f9dc-4547-9e5e-97d32600358d/.system_generated/logs/transcript.jsonl)