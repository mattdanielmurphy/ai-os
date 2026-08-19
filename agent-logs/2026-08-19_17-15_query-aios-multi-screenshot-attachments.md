# Multi-Attachment Fix & End-to-End Image Upload Verification in `query_aios` and AI-OS Companion

**Date:** 2026-08-19  
**Category:** Bug Fix / Subsystem Enhancement  

---

## 1. Problem Statement & Root Cause
In conversation `0d53eed7-c272-4176-9f64-5e16e89c0850`, when an agent attempted to attach two screenshots to Perplexity via `query_aios.js`, only one screenshot was retained and dispatched. Furthermore, the single-file pipeline lacked multi-attachment support at multiple architectural layers:

1. **CLI Argument Parser (`query_aios.js`)**: Held only a single scalar `filePath` variable, causing subsequent `--screenshot`, `--image`, or `-f` arguments to overwrite previous ones.
2. **Prompt Auto-Detection (`extractAndInlineReferencedFiles`)**: Stopped scanning after encountering the first image path in the prompt text.
3. **AI-OS Server Data Model (`src-tauri/src/server.rs`)**: `PromptDispatchPayload` only contained a single `attachment: Option<AttachmentPayload>` and `file_path: Option<String>`, discarding additional attachments.
4. **Perplexity Engine (`src-tauri/engines/perplexity-engine.js`)**: `send(message, engine, attachments, sessionId)` only packed a single `imageToken` (`attachments: (attachments && attachments.imageToken) ? [attachments.imageToken] : []`).
5. **Gemini Engine (`src-tauri/engines/gemini-engine.js`)**: `sendRaw` assumed a single `attachments` dictionary rather than accepting an array of uploaded Scotty tokens.

---

## 2. Changes Made

### A. CLI & Prompt Parser (`scripts/query_aios.js`)
- Replaced `filePath` with an array `filePaths: string[]` in the CLI argument parsing loop. Multiple `--screenshot`, `--image`, `--file`, `--files`, or `-f` flags now accumulate into `filePaths`.
- Updated `extractAndInlineReferencedFiles` to return `attachedImagePaths: string[]`, auto-detecting all referenced images in the prompt and appending them to `filePaths`.
- Updated payload dispatch to send both `file_path` (for backwards compatibility) and `file_paths: string[]` to the AI-OS companion server.

### B. Companion App Server (`apps/gemini-companion/src-tauri/src/server.rs`)
- Added `attachments: Option<Vec<AttachmentPayload>>` and `file_paths: Option<Vec<String>>` to `PromptDispatchPayload`.
- Implemented `prepare_attachments_list` returning a `Vec<PreparedAttachment>`, reading and base64-encoding all files provided across single and plural payload fields.
- Updated `handle_perplexity_query` and `handle_gemini_query` to serialize the entire attachments array into webview JavaScript, upload each file concurrently/sequentially via `uploadFileToPerplexity` / `uploadFileToGoogle`, and pass the array of uploaded tokens to the respective engines.

### C. Webview Engines (`perplexity-engine.js` & `gemini-engine.js`)
- Updated `perplexity-engine.js` `send()` to unpack `attachmentsArray` from an array of tokens and populate `params.attachments = [...]`.
- Updated `gemini-engine.js` `sendRaw()` to iterate through `attachments` and construct multi-part `attachmentsArray` payload frames.

### D. Workflow Documentation (`_plan-with-ai-os.md`)
- Documented multi-screenshot attachment support in `_plan-with-ai-os.md`.

---

## 3. Verification & Testing
1. **Live Dual-Image E2E Query Test**:
   - Dispatched two distinct image attachments (`media_1787104046219.png` [Cover Letter] and `media_1787180410933.png` [Instagram iOS Header]) using:
     ```bash
     node scripts/query_aios.js "Please inspect both attached images and describe image 1 and image 2 in detail." \
       --screenshot /Users/matt/.gemini/antigravity/brain/f90fe323-312b-494e-88c2-b5b1a4d8d39d/.user_uploaded/media_1787104046219.png \
       --screenshot /Users/matt/.gemini/antigravity/brain/0d53eed7-c272-4176-9f64-5e16e89c0850/.user_uploaded/media_1787180410933.png \
       --model gemini \
       --thread test_real_multi_screenshots \
       --new-thread
     ```
   - **Result**: Perplexity correctly received both images, uploaded each to S3, and returned a comprehensive analysis detailing both the Cover Letter (Image 1) and the Instagram iOS Header (Image 2).
2. **Compilation**: `cargo check --manifest-path apps/gemini-companion/src-tauri/Cargo.toml` passed cleanly with 0 errors.
