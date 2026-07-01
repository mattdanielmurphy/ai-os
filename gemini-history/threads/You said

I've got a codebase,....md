[2026-06-30 23:23] User:
I've got a codebase, and I want you to create a summarized version of how it works given all the code. Still give lots of detail as to how it works, but we don't need the actual verbatim code.




Project Path: vector-art-generator




Source Tree:




```txt

vector-art-generator

├── AG_CONTEXT.md

├── FEATURES.md

├── GenerationService.js

├── OpenRouterService.js

├── PLAN.md

├── cleanup.py

├── cleanup2.py

├── cleanup3.py

├── main.js

└── package.json




```




`AG_CONTEXT.md`:




```md

# Context: structural-constraint-art




## Tech Stack

- Frontend application with index.html, main.js, and GenerationService.js.




## API Integration

- Interacts with Google Gemini APIs directly (using v1beta endpoint for responseSchema/responseMimeType).

- Gemini API 503 errors trigger immediate fallback to OpenRouter (no retries). Fallback uses `google/<model>` naming.

- OpenRouter supports all Gemini models plus DeepSeek models as dropdown options.

- Full app state (API keys, provider, model, params, toggles) persists via localStorage under `pixelArtState_v2`.




## Drawing Engine Architecture

- Composite Layout drawing instructions format containing strictly 'rect' (rectangle) shapes with explicit x, y, w, and h coordinates to eliminate property hallucination and ensure deterministic styling.

- Dynamically injected semantic palette data mapping colors to structured indices (Index 0 background, Index 1 shadows, etc.).

- Back-to-front layer compositing renderer for Canvas rasterization and SVG vector generation, featuring strict type and bounds validation checks.







```




`FEATURES.md`:




```md

# Features




## Model Integration

- Supports selection of Gemini models via the user interface:

  - `gemini-3.5-flash` (Recommended)

  - `gemini-3.1-pro-preview`

  - `gemini-3.1-flash-lite`

  - `gemini-3-flash-preview`

  - `gemini-2.5-pro`

  - `gemini-2.5-flash`

  - `gemini-2.5-flash-lite`

  - `gemini-1.5-pro`

  - `gemini-1.5-flash`

- **API Routing**: Targets the `v1beta` API endpoint to support developer features like system instructions, response MIME types, and structured response schemas across all model variants (including preview and experimental models).

## User Feedback & Diagnostics

- **Real-time Pipeline Logging**: Display a live terminal-style progress log panel within the workspace canvas to communicate the exact status of the backend API call steps to the user (e.g. system prompt construction, endpoint selection, API request submission, raw text sanitization, coordinate validation, performance measurement).

- **Accurate Token-Based Cost Calculation**: Computes model-specific pricing (supporting Gemini 3.5 Flash, 3.1 Pro/Flash-Lite, 2.5 Pro/Flash/Flash-Lite, 1.5 Pro/Flash) by parsing the API's actual `usageMetadata` response containing exact input and output token usage. Costs are displayed in cents with 4 significant figures when under $1.00.




## Color Palettes & Optimization

- **Expanded Retro Palettes**: Added curated, high-quality, larger color palettes mimicking classic retro consoles and styles (PICO-8, NES Mario, GameBoy Classic, Sega Genesis Sonic, Sweetie 16, Bubblegum Pastel).

- **Structured JSON Schema Enforcement**: Configured Gemini API `responseSchema` and `responseMimeType` settings to guarantee valid JSON formatting natively, removing parsing failures and speeding up generation time.

- **Client-Side Timeout Protection**: Embedded a 10-minute abort timer (`AbortController`) to guarantee that complex and slow-generating matrices have all the time they need to complete, while still providing an eventual safety fallback in the event of a total network drop.




## Drawing Engine v2: Composite Layout & Semantic Injection

- **Locked-Down Shape Schema**: Configured response schema to strictly accept 'rect' shape instructions with explicit coordinate properties (`x`, `y`, `w`, `h`) to prevent property hallucination.

- **Enhanced System Instructions**: Added explicit coordinates guidelines, canvas boundaries, and back-to-front rendering rules.

- **Safety-First Composite Renderers**: Rebuilt Canvas and SVG renderers to validate rectangle dimensions and safely skip invalid or missing values, avoiding drawing pipeline crashes.

- **Semantic Palette Injection**: Dynamically injects hex values combined with human-readable semantic descriptions into the model prompt, allowing the model to make informed color placements.

- **Standardized Palette Mapping**: Enforces a consistent layout hierarchy (Index 0 for background, Index 1 for shadows, Index 2 for midtones, Index 3 for highlights, Index 4+ for details) in the system prompt.

- **Layered Composition Renderer**: Rebuilt Canvas (raster) and SVG (vector) rendering logic to composite geometric drawing instructions sequentially back-to-front.




## State Persistence

- Full app state (API keys, provider, model, prompt, grid size, palette, vector toggle, fallback toggle, auto-save toggle) is saved to localStorage under `pixelArtState_v2` and restored on restart. All input changes, model selections, and toggle flips trigger automatic save.




## 503 Fallback to OpenRouter

- Gemini API 503 errors throw immediately (no retries) and fall back to the equivalent `google/<model>` on OpenRouter when fallback is enabled.

- OpenRouter dropdown includes all Gemini models (prefixed with `google/`) plus DeepSeek models.




## Auto-Save to Project Folder (Disabled by Default)

- Toggleable via "Auto-save SVGs to project folder" checkbox (default: off).

- When enabled, every generation auto-saves the SVG file and a `.meta.json` (containing prompt, params, palette, model, instructions, timing) to a user-selected folder via the File System Access API.

- First save prompts the user to pick a directory; subsequent saves reuse that directory.

- Auto-saved filenames are structured with: `[timestamp]_[sanitized-prompt-truncated]_[model]_[cost].svg`.




## Vector Mode Layer Selection

- Mouse click selection of individual layer elements is fully supported in both raster (canvas) and vector (SVG) viewing modes. Highlight overlays align precisely over the active view.







```




`GenerationService.js`:




```js

/**

 * GenerationService

 *

 * An isolated API service layer for handling interactions with the Google Gemini API.

 * This class ensures that the "Structural Constraint Harness" system instruction is

 * strictly applied to every request, forcing the model to output a deterministic JSON matrix.

 *

 * To swap out Google Gemini for a custom serverless API base URL (like RunPod, Modal, etc.):

 * 1. Change the `baseUrl` inside `generateVectorArt` to your custom endpoint.

 * 2. Modify the `headers` and `payload` structures to match your custom endpoint's expectations.

 * 3. Update the response parsing logic to extract the returned JSON object correctly.

 */

export class GenerationService {

    /**

     * Calls the Gemini API to generate the drawing instructions.

     *

     * @param {string} apiKey - The Google Gemini API key.

     * @param {string} model - The specific model to use (e.g., 'gemini-3.5-flash').

     * @param {string} prompt - The user's description of the asset.

     * @param {number} gridSize - The dimensions of the grid (e.g., 16, 32, 64).

     * @param {Array<{hex: string, name: string}>} palette - The color palette with hex codes and semantic names.

     * @returns {Promise<{instructions: any[], rawText: string, metadata: any}>} The generated instructions and raw response text.

     */

    static async generateVectorArt(apiKey, model, prompt, gridSize, palette, onProgress = () => {}) {

        onProgress('Initializing Structural Constraint Harness instructions...');

        

        // Format the semantic palette for injection

        const formattedPalette = palette.map((color, index) => {

            return `Index ${index}: ${color.hex} (${color.name})`;

        }).join('\n');




        // Build the system instructions enforcing the Composite Layout System.

        const systemInstruction = `You are a vector art generation engine creating SVG-style graphics within a ${gridSize}x${gridSize} viewBox. 

- Coordinate [0,0] is the top-left corner.

- You must use the provided semantic color palette.

- Output a sequence of vector shapes: 'path', 'circle', 'rect', or 'polygon'.

- Always start with a full-canvas background rect, then layer elements front-to-back or back-to-front as needed for SVG.

- Use smooth Bezier curves (C, S, Q, T) in paths for organic shapes.

- You may optionally use 'opacity' (0.0 to 1.0), 'strokeColorIndex' (integer), and 'strokeWidth' (number) for advanced styling.




Color Palette Configuration:

You MUST ONLY map colors using the following indexes. Each index represents a specific semantic purpose in the composition:

${formattedPalette}




Strict Hierarchy/Structure Guidelines:

- Index 0 represents the background or sky. Always start by filling the canvas.

- Index 1 represents primary shadows, deep contours, or background details.

- Index 2 represents the primary surface, midtones, or base shapes.

- Index 3 represents the primary highlights, light source effects, or details.

- Indices >= 4 represent specific detail accents or specialized colors as labeled above.




Target Canvas Coordinates:

The grid is a 2D coordinate system from 0,0 (top-left) to ${gridSize},${gridSize} (bottom-right). Coordinates can be fractional (e.g., 10.5).




Constraints:

1. Output raw JSON conforming to the schema. Do not output markdown code blocks (e.g. \`\`\`json) or conversational prose.

2. Ensure layers are output in order from back-to-front.`;




        onProgress(`Configuring API endpoint for model: ${model}...`);

        // Configure the API Endpoint

        const baseUrl = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`;

        const url = `${baseUrl}?key=${apiKey}`;




        onProgress('Constructing payload and generation configuration...');

        // Construct the request payload for Gemini

        const payload = {

            system_instruction: {

                parts: [{ text: systemInstruction }]

            },

            contents: [

                {

                    parts: [{ text: prompt }]

                }

            ],

            generationConfig: {

                temperature: 0.2, // Low temperature for deterministic layout

                topK: 1, // Restrict token choices to the absolute most likely

                responseMimeType: "application/json",

                responseSchema: {

                    type: "OBJECT",

                    properties: {

                        instructions: {

                            type: "ARRAY",

                            description: `An ordered array of vector drawing instructions to construct the image in a ${gridSize}x${gridSize} viewBox.`,

                            items: {

                                type: "OBJECT",

                                properties: {

                                    type: {

                                        type: "STRING",

                                        enum: ["rect", "circle", "path", "polygon"]

                                    },

                                    colorIndex: {

                                        type: "INTEGER"

                                    },

                                    x: { "type": "NUMBER" },

                                    y: { "type": "NUMBER" },

                                    w: { "type": "NUMBER" },

                                    h: { "type": "NUMBER" },

                                    cx: { "type": "NUMBER" },

                                    cy: { "type": "NUMBER" },

                                    r: { "type": "NUMBER" },

                                    d: { "type": "STRING", "description": "SVG path data" },

                                    points: { "type": "STRING", "description": "SVG polygon points" },

                                    opacity: { "type": "NUMBER", "description": "Opacity from 0.0 to 1.0" },

                                    strokeColorIndex: { "type": "INTEGER" },

                                    strokeWidth: { "type": "NUMBER" },

                                    description: { "type": "STRING" }

                                },

                                required: ["type", "colorIndex"]

                            }

                        }

                    },

                    required: ["instructions"]

                }

            }

        };




        try {

            const startTime = performance.now();

            let response;

            const maxRetries = 3;

            let retryDelay = 1000;

            const timeoutMs = 600000; // 10-minute client-side timeout to ensure slow generations are never cut off




            for (let attempt = 1; attempt <= maxRetries; attempt++) {

                onProgress(`Sending request to Gemini API (Attempt ${attempt}/${maxRetries})...`);

                const controller = new AbortController();

                const timeoutId = setTimeout(() => controller.abort(), timeoutMs);




                try {

                    response = await fetch(url, {

                        method: 'POST',

                        headers: {

                            'Content-Type': 'application/json'

                        },

                        body: JSON.stringify(payload),

                        signal: controller.signal

                    });

                    clearTimeout(timeoutId);




                    if (response.status === 503) {

                        // 503 = immediate fallback to OpenRouter, no retries

                        throw new Error(`Gemini API 503: Model ${model} is currently unavailable.`);

                    }

                    if (response.status === 429) {

                        if (attempt < maxRetries) {

                            onProgress(`Model is busy (Status ${response.status}). Retrying in ${(retryDelay / 1000).toFixed(1)}s...`);

                            await new Promise(resolve => setTimeout(resolve, retryDelay));

                            retryDelay *= 2;

                            continue;

                        }

                    }

                    break;

                } catch (err) {

                    clearTimeout(timeoutId);

                    const isAbort = err.name === 'AbortError';

                    const msg = isAbort ? `Request timed out after ${(timeoutMs / 1000).toFixed(0)}s.` : `Network/Connection error.`;




                    if (attempt === maxRetries) {

                        throw new Error(isAbort ? `API request timed out after ${maxRetries} attempts.` : err.message);

                    }

                    onProgress(`${msg} Retrying in ${(retryDelay / 1000).toFixed(1)}s...`);

                    await new Promise(resolve => setTimeout(resolve, retryDelay));

                    retryDelay *= 2;

                }

            }




        if (!response) {

            throw new Error("Failed to receive response from the API after retrying.");

        }




        onProgress(`Response received with status ${response.status} (${response.statusText}).`);




        if (!response.ok) {

            const errorData = await response.json().catch(() => ({}));

            throw new Error(`API Error ${response.status}: ${errorData.error?.message || response.statusText}`);

        }




        onProgress('Reading response JSON content...');

        const data = await response.json();

        const endTime = performance.now();

        const durationMs = endTime - startTime;




            // Extract the generated text from Gemini's response structure

            if (!data.candidates || data.candidates.length === 0) {

                throw new Error("No candidates returned from the API.");

            }




            onProgress('Extracting generated text candidate...');

            let rawText = data.candidates[0].content.parts[0].text;




            onProgress('Sanitizing markdown and formatting delimiters...');

            rawText = rawText.replace(/```json/g, '').replace(/```/g, '').trim();




            onProgress('Parsing generated coordinate composition string...');

            let parsedJson;

            try {

                parsedJson = JSON.parse(rawText);

            } catch (e) {

                onProgress('Error: Failed to parse raw string into valid JSON.');

                console.error("Failed to parse JSON string:", rawText);

                throw new Error("Model failed to return valid JSON. Check the console for the raw output.");

            }




            if (!parsedJson.instructions || !Array.isArray(parsedJson.instructions)) {

                throw new Error("JSON returned does not contain a valid 'instructions' array key.");

            }




            onProgress('Calculating pipeline performance metrics...');

            const computeTimeS = (durationMs / 1000).toFixed(2);

            const coldStartMs = Math.floor(Math.random() * (120 - 20 + 1) + 20);




            // Extract token usage metadata from response or use estimations as fallback

            const promptTokens = data.usageMetadata?.promptTokenCount || Math.ceil((systemInstruction.length + prompt.length) / 4);

            const tokensOut = data.usageMetadata?.candidatesTokenCount || Math.ceil(rawText.length / 4);




            // API Pricing Rates per Token (pricing per 1M tokens / 1,000,000)

            const MODEL_RATES = {

                'gemini-3.5-flash': { input: 0.075 / 1000000, output: 0.30 / 1000000 },

                'gemini-3.1-pro-preview': { input: 1.25 / 1000000, output: 5.00 / 1000000 },

                'gemini-3.1-flash-lite': { input: 0.075 / 1000000, output: 0.30 / 1000000 },

                'gemini-3-flash-preview': { input: 0.075 / 1000000, output: 0.30 / 1000000 },

                'gemini-2.5-pro': { input: 1.25 / 1000000, output: 5.00 / 1000000 },

                'gemini-2.5-flash': { input: 0.075 / 1000000, output: 0.30 / 1000000 },

                'gemini-2.5-flash-lite': { input: 0.075 / 1000000, output: 0.30 / 1000000 },

                'gemini-1.5-pro': { input: 1.25 / 1000000, output: 5.00 / 1000000 },

                'gemini-1.5-flash': { input: 0.075 / 1000000, output: 0.30 / 1000000 }

            };




            const rates = MODEL_RATES[model] || MODEL_RATES['gemini-3.5-flash'];

            const activeBilling = (promptTokens * rates.input + tokensOut * rates.output).toFixed(8);




            const metadata = {

                computeTime: computeTimeS,

                coldStart: coldStartMs,

                promptTokens: promptTokens,

                tokensOut: tokensOut,

                activeBilling: `$${activeBilling}`

            };




            onProgress('Pipeline execution complete!');

            return {

                instructions: parsedJson.instructions,

                rawText: rawText,

                metadata: metadata

            };




        } catch (error) {

            onProgress(`Error: ${error.message || 'Generation failed'}`);

            console.error("GenerationService Error:", error);

            throw error;

        }

    }




    /**

     * Refines a single layer instruction via the Gemini API.

     *

     * @param {string} apiKey - The Google Gemini API key.

     * @param {string} model - The specific model to use.

     * @param {string} originalPrompt - The user's original asset description.

     * @param {number} gridSize - The dimensions of the grid.

     * @param {Array<{hex: string, name: string}>} palette - The color palette.

     * @param {object} targetInstruction - The instruction object to refine.

     * @param {number} index - The index of the instruction in the array.

     * @param {string} refinePrompt - The user's refinement request.

     * @param {function} onProgress - Progress callback.

     * @returns {Promise<{replacement: any[]}>} The replacement instructions.

     */

    static async refineLayer(apiKey, model, originalPrompt, gridSize, palette, targetInstruction, index, refinePrompt, onProgress = () => {}, allInstructions = []) {

        onProgress('Preparing layer refinement context...');




        const formattedPalette = palette.map((color, i) => {

            return `Index ${i}: ${color.hex} (${color.name})`;

        }).join('\n');




        // Build surrounding-context snippet when no specific target is selected

        let contextBlock = ''

        if (targetInstruction) {

            // Single-selection refinement — include neighbors for context

            const prev = index > 0 ? allInstructions.slice(Math.max(0, index - 3), index) : []

            const next = index < allInstructions.length - 1 ? allInstructions.slice(index + 1, index + 4) : []

            contextBlock = `The layer to refine is at index ${index}:

${JSON.stringify(targetInstruction)}




Surrounding layers (for context — DO NOT modify these):

${prev.length ? `Layers before (indices ${Math.max(0, index - 3)}–${index - 1}):\n${JSON.stringify(prev)}` : '(none before)'}

${next.length ? `\nLayers after (indices ${index + 1}–${Math.min(allInstructions.length - 1, index + 4)}):\n${JSON.stringify(next)}` : '\n(none after)'}`

        } else {

            // No selection — do a global contextual refinement over the whole image

            contextBlock = `The user wants a refinement applied to the ENTIRE image. Here are ALL current instructions for context:

${JSON.stringify(allInstructions)}

Respond with a complete replacement "instructions" array (same structure as the input).`

        }




        const systemInstruction = `You are a vector art generation engine refining SVG graphics in a ${gridSize}x${gridSize} viewBox.




${targetInstruction ? `The user wants to modify one specific drawing instruction.` : `The user wants to refine the entire composition.`}




${contextBlock}




The user's refinement request: "${refinePrompt}"




Original image description: "${originalPrompt}"




Rules:

${targetInstruction

    ? `- Output a JSON object with a "replacement" array of one or more vector instructions that REPLACE the original at index ${index}.

- If you need to split the original shape into multiple shapes, output them in back-to-front order.

- To delete the layer entirely, output an empty array [].`

    : `- Output a JSON object with an "instructions" array that is a FULL replacement for the entire composition.

- Keep the same overall structure but apply the requested refinement.

- Maintain back-to-front ordering.`

}

- Valid types: "rect", "circle", "path", "polygon". Provide appropriate properties (x, y, w, h for rect; cx, cy, r for circle; d for path; points for polygon).

- Use only colors from the palette below.

- Coordinates can be fractional and should generally fall within [0,0] to [${gridSize},${gridSize}].

- Use colorIndex values that make semantic sense for the refinement.




Color Palette:

${formattedPalette}




Output raw JSON conforming to the schema. No markdown code blocks.`;




        onProgress(`Sending refinement to ${model}...`);




        const baseUrl = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`;

        const url = `${baseUrl}?key=${apiKey}`;




        const payload = {

            system_instruction: {

                parts: [{ text: systemInstruction }]

            },

            contents: [

                {

                    parts: [{ text: refinePrompt }]

                }

            ],

            generationConfig: {

                temperature: 0.3,

                topK: 1,

                responseMimeType: "application/json",

                responseSchema: {

                    type: "OBJECT",

                    properties: {

                        replacement: {

                            type: "ARRAY",

                            description: `Replacement instruction(s) for the layer at index ${index}. Empty array = delete the layer.`,

                            items: {

                                type: "OBJECT",

                                properties: {

                                    type: {

                                        type: "STRING",

                                        enum: ["rect", "circle", "path", "polygon"]

                                    },

                                    colorIndex: { type: "INTEGER" },

                                    x: { type: "NUMBER" },

                                    y: { type: "NUMBER" },

                                    w: { type: "NUMBER" },

                                    h: { type: "NUMBER" },

                                    cx: { type: "NUMBER" },

                                    cy: { type: "NUMBER" },

                                    r: { type: "NUMBER" },

                                    d: { type: "STRING" },

                                    points: { type: "STRING" },

                                    opacity: { type: "NUMBER" },

                                    strokeColorIndex: { type: "INTEGER" },

                                    strokeWidth: { type: "NUMBER" },

                                    description: { type: "STRING" }

                                },

                                required: ["type", "colorIndex"]

                            }

                        }

                    },

                    required: ["replacement"]

                }

            }

        };




        const refineStartTime = performance.now();




        const response = await fetch(url, {

            method: 'POST',

            headers: { 'Content-Type': 'application/json' },

            body: JSON.stringify(payload)

        });




        if (!response.ok) {

            const errorData = await response.json().catch(() => ({}));

            throw new Error(`API Error ${response.status}: ${errorData.error?.message || response.statusText}`);

        }




        onProgress('Parsing refinement response...');

        const data = await response.json();

        const refineEndTime = performance.now();




        if (!data.candidates || data.candidates.length === 0) {

            throw new Error("No candidates returned from the API.");

        }




        let rawText = data.candidates[0].content.parts[0].text;

        rawText = rawText.replace(/```json/g, '').replace(/```/g, '').trim();




        let parsed;

        try {

            parsed = JSON.parse(rawText);

        } catch (e) {

            throw new Error("Failed to parse refinement JSON. Raw: " + rawText.substring(0, 200));

        }




        // Calculate compute time & cost for this refinement

        const refineDuration = refineEndTime - refineStartTime

        const refineTimeS = (refineDuration / 1000).toFixed(2)

        const rPromptTokens = data.usageMetadata?.promptTokenCount || Math.ceil((systemInstruction.length + refinePrompt.length) / 4)

        const rTokensOut = data.usageMetadata?.candidatesTokenCount || Math.ceil(rawText.length / 4)

        const MODEL_RATES = {

            'gemini-3.5-flash': { input: 0.075 / 1000000, output: 0.30 / 1000000 },

            'gemini-3.1-pro-preview': { input: 1.25 / 1000000, output: 5.00 / 1000000 },

            'gemini-3.1-flash-lite': { input: 0.075 / 1000000, output: 0.30 / 1000000 },

            'gemini-3-flash-preview': { input: 0.075 / 1000000, output: 0.30 / 1000000 },

            'gemini-2.5-pro': { input: 1.25 / 1000000, output: 5.00 / 1000000 },

            'gemini-2.5-flash': { input: 0.075 / 1000000, output: 0.30 / 1000000 },

            'gemini-2.5-flash-lite': { input: 0.075 / 1000000, output: 0.30 / 1000000 },

            'gemini-1.5-pro': { input: 1.25 / 1000000, output: 5.00 / 1000000 },

            'gemini-1.5-flash': { input: 0.075 / 1000000, output: 0.30 / 1000000 }

        }

        const rates = MODEL_RATES[model] || MODEL_RATES['gemini-3.5-flash']

        const rBilling = (rPromptTokens * rates.input + rTokensOut * rates.output).toFixed(8)




        if (!parsed.replacement && !targetInstruction && parsed.instructions) {

            // Global refinement — returned full instructions

            onProgress('Global refinement received successfully!');

            return {

                replacement: parsed.instructions,

                meta: {

                    computeTime: refineTimeS,

                    coldStart: 0,

                    promptTokens: rPromptTokens,

                    tokensOut: rTokensOut,

                    activeBilling: `$${rBilling}`

                }

            }

        }




        if (!Array.isArray(parsed.replacement)) {

            throw new Error("Refinement response missing 'replacement' array.");

        }




        onProgress('Refinement received successfully!');

        return {

            replacement: parsed.replacement,

            meta: {

                computeTime: refineTimeS,

                coldStart: 0,

                promptTokens: rPromptTokens,

                tokensOut: rTokensOut,

                activeBilling: `$${rBilling}`

            }

        };

    }

}




```




`OpenRouterService.js`:




```js

/**

 * OpenRouterService

 *

 * Handles API calls to OpenRouter for models like DeepSeek V4 Flash and DeepSeek R1.

 * Uses OpenAI-compatible chat completions format.

 */

export class OpenRouterService {

    /**

     * Generates pixel art instructions via OpenRouter.

     *

     * @param {string} apiKey - OpenRouter API key.

     * @param {string} model - The OpenRouter model ID (e.g. "deepseek/deepseek-v4-flash").

     * @param {string} prompt - User's description.

     * @param {number} gridSize - Canvas size.

     * @param {Array} palette - Color palette array.

     * @param {function} onProgress - Progress callback.

     * @returns {Promise<{instructions: any[], metadata: any}>}

     */

    static async generateVectorArt(

        apiKey,

        model,

        prompt,

        gridSize,

        palette,

        onProgress = () => {}

    ) {

        onProgress(`Initializing OpenRouter request for ${model}...`)




        const formattedPalette = palette

            .map((c, i) => `Index ${i}: ${c.hex} (${c.name})`)

            .join('\n')




        const systemMessage = `You are a vector art generation engine creating SVG-style graphics within a ${gridSize}x${gridSize} viewBox.

- Coordinate [0,0] is the top-left corner.

- You must use the provided semantic color palette.

- Output a sequence of vector shapes: 'path', 'circle', 'rect', or 'polygon'.

- Always start with a full-canvas background rect, then layer elements back-to-front.

- Use smooth Bezier curves (C, S, Q, T) in paths for organic shapes.

- You may optionally use 'opacity' (0.0 to 1.0), 'strokeColorIndex' (integer), and 'strokeWidth' (number) for advanced styling.

- NEVER invent property names. The color field MUST be called "colorIndex" (not "color"). Use strictly: type, colorIndex, x, y, w, h, cx, cy, r, d, points, opacity, strokeColorIndex, strokeWidth, description.




Color Palette Configuration:

${formattedPalette}




Strict Hierarchy/Structure Guidelines:

- Index 0 represents the background or sky. Always start by filling the canvas.

- Index 1 represents primary shadows, deep contours, or background details.

- Index 2 represents the primary surface, midtones, or base shapes.

- Index 3 represents the primary highlights, light source effects, or details.

- Indices >= 4 represent specific detail accents or specialized colors as labeled above.




Target Canvas Coordinates:

The viewBox goes from [0,0] to [${gridSize},${gridSize}]. Coordinates can be fractional.




Constraints:

1. Output ONLY raw JSON matching the provided schema.

2. Layer back-to-front: background, midground, shadows, highlights, details.`




        const userMessage = `Generate vector art: ${prompt}\n\nOutput JSON with an "instructions" array of vector shape objects.`




        const requestBody = {

            model: model,

            messages: [

                { role: 'system', content: systemMessage },

                { role: 'user', content: userMessage },

            ],

            temperature: 0.2,

            top_p: 1,

            response_format: { type: 'json_object' },

        }




        onProgress(`Sending request to OpenRouter...`)




        const startTime = performance.now()

        const response = await fetch(

            'https://openrouter.ai/api/v1/chat/completions',

            {

                method: 'POST',

                headers: {

                    'Content-Type': 'application/json',

                    Authorization: `Bearer ${apiKey}`,

                    'HTTP-Referer': window.location.origin,

                    'X-Title': 'Vector Art Generator',

                },

                body: JSON.stringify(requestBody),

            }

        )




        if (!response.ok) {

            const errBody = await response.json().catch(() => ({}))

            const status = response.status

            const msg = errBody.error?.message || response.statusText

            if (status === 503) {

                throw new Error(`OpenRouter 503: Model ${model} is currently unavailable on OpenRouter.`)

            }

            throw new Error(

                `OpenRouter Error ${status}: ${msg}`

            )

        }




        const endTime = performance.now()

        const durationMs = endTime - startTime

        onProgress('Response received, parsing...')




        const data = await response.json()




        let rawText = data.choices?.[0]?.message?.content

        if (!rawText) throw new Error('OpenRouter returned empty response.')




        // Strip markdown fences if present

        rawText = rawText

            .replace(/```json/g, '')

            .replace(/```/g, '')

            .trim()




        let parsed

        try {

            parsed = JSON.parse(rawText)

        } catch (e) {

            throw new Error(

                'Failed to parse OpenRouter JSON. Raw: ' +

                    rawText.substring(0, 200)

            )

        }




        if (!parsed.instructions || !Array.isArray(parsed.instructions)) {

            // Some models wrap differently — try top-level

            if (Array.isArray(parsed)) {

                parsed = { instructions: parsed }

            } else {

                throw new Error("OpenRouter JSON missing 'instructions' array.")

            }

        }




        // Normalize: DeepSeek sometimes uses "color" instead of "colorIndex"

        for (const inst of parsed.instructions) {

            if (inst.color !== undefined && inst.colorIndex === undefined) {

                inst.colorIndex = inst.color

                delete inst.color

            }

        }




        const tokensIn = data.usage?.prompt_tokens || 0

        const tokensOut = data.usage?.completion_tokens || 0




        // OpenRouter pricing rates

        const MODEL_RATES = {

            'google/gemini-3.5-flash': { input: 0.075 / 1000000, output: 0.30 / 1000000 },

            'google/gemini-3.1-pro-preview': { input: 1.25 / 1000000, output: 5.00 / 1000000 },

            'google/gemini-3.1-flash-lite': { input: 0.075 / 1000000, output: 0.30 / 1000000 },

            'google/gemini-3-flash-preview': { input: 0.075 / 1000000, output: 0.30 / 1000000 },

            'google/gemini-2.5-pro': { input: 1.25 / 1000000, output: 5.00 / 1000000 },

            'google/gemini-2.5-flash': { input: 0.075 / 1000000, output: 0.30 / 1000000 },

            'google/gemini-2.5-flash-lite': { input: 0.075 / 1000000, output: 0.30 / 1000000 },

            'google/gemini-1.5-pro': { input: 1.25 / 1000000, output: 5.00 / 1000000 },

            'google/gemini-1.5-flash': { input: 0.075 / 1000000, output: 0.30 / 1000000 },

            'deepseek/deepseek-v4-flash': { input: 0.14 / 1000000, output: 0.28 / 1000000 },

            'deepseek/deepseek-r1': { input: 0.55 / 1000000, output: 2.19 / 1000000 }

        };

        const rates = MODEL_RATES[model] || { input: 0.075 / 1000000, output: 0.30 / 1000000 };

        const activeBilling = `≈$${(tokensIn * rates.input + tokensOut * rates.output).toFixed(8)}`




        const computeTimeS = (durationMs / 1000).toFixed(2)




        onProgress('Generation complete!')

        return {

            instructions: parsed.instructions,

            metadata: {

                computeTime: computeTimeS,

                coldStart: 0,

                promptTokens: tokensIn,

                tokensOut: tokensOut,

                activeBilling: activeBilling,

            },

        }

    }




    /**

     * Refines a single layer via OpenRouter.

     */

    static async refineLayer(

        apiKey,

        model,

        originalPrompt,

        gridSize,

        palette,

        targetInstruction,

        index,

        refinePrompt,

        onProgress = () => {},

        allInstructions = []

    ) {

        onProgress(`Preparing OpenRouter refinement for ${model}...`)




        const formattedPalette = palette

            .map((c, i) => `Index ${i}: ${c.hex} (${c.name})`)

            .join('\n')




        // Build surrounding-context snippet

        let contextBlock = ''

        if (targetInstruction) {

            const prev = index > 0 ? allInstructions.slice(Math.max(0, index - 3), index) : []

            const next = index < allInstructions.length - 1 ? allInstructions.slice(index + 1, index + 4) : []

            contextBlock = `The layer to refine is at index ${index}:

${JSON.stringify(targetInstruction)}




Surrounding layers (for context — DO NOT modify these):

${prev.length ? `Layers before (indices ${Math.max(0, index - 3)}–${index - 1}):\n${JSON.stringify(prev)}` : '(none before)'}

${next.length ? `\nLayers after (indices ${index + 1}–${Math.min(allInstructions.length - 1, index + 4)}):\n${JSON.stringify(next)}` : '\n(none after)'}`

        } else {

            contextBlock = `The user wants a refinement applied to the ENTIRE image. Here are ALL current instructions for context:

${JSON.stringify(allInstructions)}

Respond with a complete replacement "instructions" array (same structure as the input).`

        }




        const systemMessage = `You are a vector art generation engine refining SVG graphics in a ${gridSize}x${gridSize} viewBox.




${targetInstruction ? `The user wants to modify one specific drawing instruction.` : `The user wants to refine the entire composition.`}




${contextBlock}




The user's refinement request: "${refinePrompt}"




Original description: "${originalPrompt}"




Rules:

${targetInstruction

    ? `- Output a JSON object with a "replacement" array of one or more vector instructions that REPLACE the original at index ${index}.

- Valid types: "rect", "circle", "path", "polygon". Provide appropriate properties.

- Use only colors from the palette below.

- Split into multiple shapes if needed, back-to-front order.

- Empty array = delete the layer.`

    : `- Output a JSON object with an "instructions" array that is a FULL replacement for the entire composition.

- Keep the same overall structure but apply the requested refinement.

- Maintain back-to-front ordering.`

}




Color Palette:

${formattedPalette}




Output ONLY raw JSON.`




        const requestBody = {

            model: model,

            messages: [

                { role: 'system', content: systemMessage },

                { role: 'user', content: refinePrompt },

            ],

            temperature: 0.3,

            top_p: 1,

            response_format: { type: 'json_object' },

        }




        onProgress('Sending refinement to OpenRouter...')




        const response = await fetch(

            'https://openrouter.ai/api/v1/chat/completions',

            {

                method: 'POST',

                headers: {

                    'Content-Type': 'application/json',

                    Authorization: `Bearer ${apiKey}`,

                    'HTTP-Referer': window.location.origin,

                    'X-Title': 'Vector Art Generator',

                },

                body: JSON.stringify(requestBody),

            }

        )




        if (!response.ok) {

            const errBody = await response.json().catch(() => ({}))

            const status = response.status

            const msg = errBody.error?.message || response.statusText

            if (status === 503) {

                throw new Error(`OpenRouter 503: Model ${model} is currently unavailable on OpenRouter.`)

            }

            throw new Error(

                `OpenRouter Error ${status}: ${msg}`

            )

        }




        const data = await response.json()

        let rawText = data.choices?.[0]?.message?.content

        if (!rawText)

            throw new Error('OpenRouter returned empty refinement response.')




        rawText = rawText

            .replace(/```json/g, '')

            .replace(/```/g, '')

            .trim()




        let parsed

        try {

            parsed = JSON.parse(rawText)

        } catch (e) {

            throw new Error(

                'Failed to parse refinement JSON. Raw: ' +

                    rawText.substring(0, 200)

            )

        }




        // Token usage & cost for this refinement

        const rTokensIn = data.usage?.prompt_tokens || 0

        const rTokensOut = data.usage?.completion_tokens || 0

        const MODEL_RATES = {

            'google/gemini-3.5-flash': { input: 0.075 / 1000000, output: 0.30 / 1000000 },

            'google/gemini-3.1-pro-preview': { input: 1.25 / 1000000, output: 5.00 / 1000000 },

            'google/gemini-3.1-flash-lite': { input: 0.075 / 1000000, output: 0.30 / 1000000 },

            'google/gemini-3-flash-preview': { input: 0.075 / 1000000, output: 0.30 / 1000000 },

            'google/gemini-2.5-pro': { input: 1.25 / 1000000, output: 5.00 / 1000000 },

            'google/gemini-2.5-flash': { input: 0.075 / 1000000, output: 0.30 / 1000000 },

            'google/gemini-2.5-flash-lite': { input: 0.075 / 1000000, output: 0.30 / 1000000 },

            'google/gemini-1.5-pro': { input: 1.25 / 1000000, output: 5.00 / 1000000 },

            'google/gemini-1.5-flash': { input: 0.075 / 1000000, output: 0.30 / 1000000 },

            'deepseek/deepseek-v4-flash': { input: 0.14 / 1000000, output: 0.28 / 1000000 },

            'deepseek/deepseek-r1': { input: 0.55 / 1000000, output: 2.19 / 1000000 }

        };

        const rates = MODEL_RATES[model] || { input: 0.075 / 1000000, output: 0.30 / 1000000 };

        const refineBilling = `≈$${(rTokensIn * rates.input + rTokensOut * rates.output).toFixed(8)}`




        if (!parsed.replacement && !targetInstruction && parsed.instructions) {

            // Global refinement — returned full instructions

            // Normalize color → colorIndex

            for (const inst of parsed.instructions) {

                if (inst.color !== undefined && inst.colorIndex === undefined) {

                    inst.colorIndex = inst.color

                    delete inst.color

                }

            }

            onProgress('Global refinement received successfully!')

            return {

                replacement: parsed.instructions,

                meta: {

                    computeTime: '0.00',

                    coldStart: 0,

                    promptTokens: rTokensIn,

                    tokensOut: rTokensOut,

                    activeBilling: refineBilling,

                },

            }

        }




        if (!Array.isArray(parsed.replacement)) {

            throw new Error("Refinement response missing 'replacement' array.")

        }




        // Normalize: DeepSeek sometimes uses "color" instead of "colorIndex"

        for (const inst of parsed.replacement) {

            if (inst.color !== undefined && inst.colorIndex === undefined) {

                inst.colorIndex = inst.color

                delete inst.color

            }

        }




        onProgress('Refinement received successfully!')

        return {

            replacement: parsed.replacement,

            meta: {

                computeTime: '0.00',

                coldStart: 0,

                promptTokens: rTokensIn,

                tokensOut: rTokensOut,

                activeBilling: refineBilling,

            },

        }

    }

}




```




`PLAN.md`:




```md

# Vector Art Generator: Transition Plan




Here is the broad, 3-phase plan for transitioning the codebase from constrained pixel-art generation to free-form vector (SVG) art generation.




## Phase 1: Update the AI Schema and Prompts

**Goal:** Teach the AI to generate vector paths instead of constrained rectangles.

*   **Define the Vector Schema:** Replace the current rectangular JSON structure with a schema that supports SVG primitives (e.g., `<path d="...">`, `<circle>`, `<rect>`, `<polygon>`).

*   **Update System Prompts:** Rewrite the AI instructions to focus on creating cohesive vector graphics using Bezier curves and scalable shapes, instead of snapping to a grid.

*   **Remove Old Constraints:** Strip out the logic and validations that strictly enforced pixel-art grid boundaries and overlapping rules.




## Phase 2: Update the Rendering Engine

**Goal:** Render the new vector schema correctly in the browser.

*   **Build the SVG Pipeline:** Replace the existing `<canvas>` or grid-based rendering logic with a robust SVG rendering component.

*   **Data Mapping:** Ensure the frontend correctly parses the new vector JSON structure and dynamically maps it to standard SVG DOM elements.

*   **Scaling & ViewBox:** Implement responsive `viewBox` settings so the generated vector art scales infinitely and crisply on any screen size.




## Phase 3: Refinement and Advanced Features

**Goal:** Elevate the vector art experience with advanced styling and tooling.

*   **Advanced Styling Support:** Extend the schema and renderer to support advanced SVG attributes like linear/radial gradients, stroke weights, opacity, and path fills.

*   **SVG Export:** Implement a "Download SVG" feature, allowing users to save the generated art in a clean, production-ready `.svg` format.

*   **UI/UX Polish:** Update the branding from "Structural Constraint Art" to "Vector Art Generator" and refine the gallery to showcase scalable graphics.




```




`cleanup.py`:




```py

import re




with open('main.js', 'r') as f:

    content = f.read()




# Remove state fields

content = re.sub(r"\s*gridSize:\s*32,", "", content)

content = re.sub(r"\s*isVectorMode:\s*false,", "", content)




# Remove DOM fields

content = re.sub(r"\s*gridSizeSelect:\s*document.getElementById\('gridSize'\),", "", content)

content = re.sub(r"\s*vectorToggle:\s*document.getElementById\('vectorToggle'\),", "", content)




# Remove DOM event listeners and usages

content = re.sub(r"\s*DOM\.gridSizeSelect\.value\s*=\s*String\(state\.gridSize\)", "", content)

content = re.sub(r"\s*DOM\.vectorToggle\.checked\s*=\s*state\.isVectorMode", "", content)




content = re.sub(r"\s*DOM\.gridSizeSelect\.addEventListener\([\s\S]*?}\)", "", content)

content = re.sub(r"\s*DOM\.vectorToggle\.addEventListener\([\s\S]*?}\)", "", content)




# Remove isVectorMode references in saveFullState

content = re.sub(r"\s*isVectorMode:\s*state\.isVectorMode,", "", content)




# Remove gridSize references in saveFullState and metadata

content = re.sub(r"\s*gridSize:\s*state\.gridSize,", "", content)




# Replace state.gridSize with 1024 everywhere else

content = re.sub(r"state\.gridSize", "1024", content)




# Remove parameter gridSize where it's passed but just use 1024 inside

# wait, better to just let state.gridSize -> 1024 do its job, but there are function signatures:

# function drawCanvasRaster(instructions, palette, gridSize) { ... }

# function drawSvgVector(instructions, palette, gridSize) { ... }

# Let's remove drawCanvasRaster completely

content = re.sub(r"function drawCanvasRaster\([\s\S]*?}\n\n", "\n", content)

content = re.sub(r"\s*drawCanvasRaster\([\s\S]*?\)", "", content)




# Remove updateViewMode function and calls

content = re.sub(r"function updateViewMode\(\)\s*{[\s\S]*?}\n", "", content)

content = re.sub(r"\s*updateViewMode\(\)", "", content)




# We removed isVectorMode from updateViewMode, but what about other places?

# In handleCanvasClick:

# if (state.isVectorMode) { ... svg logic } else { ... canvas logic }

# Let's replace state.isVectorMode with true

content = re.sub(r"state\.isVectorMode", "true", content)




with open('main.js', 'w') as f:

    f.write(content)







```




`cleanup2.py`:




```py

import re




with open('main.js', 'r') as f:

    content = f.read()




# Replace `if (true) { ... } else { ... }` in handleCanvasClick

# It looks like:

#     if (true) {

#         let target = e.target;

#         while (target && target !== DOM.displaySvgContainer) {

#             if (target.hasAttribute('data-index')) {

#                 foundIndex = parseInt(target.getAttribute('data-index'), 10);

#                 break;

#             }

#             target = target.parentNode;

#         }

#     } else {

#         const activeEl = DOM.displayCanvas

#         ...

#         // clamp to grid bounds

#         ...

#         // Search instructions back-to-front

#         ...

#     }

# We can just manually replace this block.




pattern_click = re.compile(r"    if \(true\) \{\n(.*?)    \} else \{\n.*?    \}\n\n    if \(foundIndex === -1\)", re.DOTALL)

def repl_click(m):

    return "    " + m.group(1).strip() + "\n\n    if (foundIndex === -1)"

content = pattern_click.sub(repl_click, content)




# Clean up download function:

#     if (true) {

#         if (!state.currentSvgString) return

#         ...

#         URL.revokeObjectURL(url)

#     } else {

#         ...

#         document.body.removeChild(a)

#     }

pattern_dl = re.compile(r"    if \(true\) \{\n(.*?)    \} else \{\n.*?        document\.body\.removeChild\(a\)\n    \}", re.DOTALL)

def repl_dl(m):

    return "    " + m.group(1).strip() + "\n"

content = pattern_dl.sub(repl_dl, content)




# Remove `DOM.displayCanvas.classList.add('hidden')` etc since displayCanvas shouldn't exist anymore, wait.

# It doesn't hurt, but I can also remove displayCanvas from index.html




with open('main.js', 'w') as f:

    f.write(content)




```




`cleanup3.py`:




```py

import re




with open('main.js', 'r') as f:

    content = f.read()




# remove displayCanvas from DOM

content = re.sub(r"\s*displayCanvas:\s*document\.getElementById\('displayCanvas'\),", "", content)

content = re.sub(r"\s*DOM\.displayCanvas\.addEventListener\('click', handleCanvasClick\)", "", content)




# remove `DOM.displayCanvas.classList.add('hidden')`

content = re.sub(r"\s*DOM\.displayCanvas\.classList\.add\('hidden'\)", "", content)




# update activeEl logic

content = re.sub(r"const activeEl = true \? DOM\.displaySvgContainer : DOM\.displayCanvas", "const activeEl = DOM.displaySvgContainer", content)




# remove displaySvgContainer hidden class when rendering

content = re.sub(r"// Draw SVG \(Vector\)", r"DOM.displaySvgContainer.classList.remove('hidden')\n    // Draw SVG (Vector)", content)




with open('main.js', 'w') as f:

    f.write(content)




```




`main.js`:




```js

import { GenerationService } from './GenerationService.js'

import { OpenRouterService } from './OpenRouterService.js'




const PALETTES = {

    minimalistTech: [

        { hex: '#0f172a', name: 'Background / Sky (Slate 900)' },

        { hex: '#1e293b', name: 'Primary Shadows (Slate 800)' },

        { hex: '#e2e8f0', name: 'Primary Surface / Midtones (Slate 200)' },

        { hex: '#06b6d4', name: 'Highlights / Secondary Lighting (Cyan 500)' },

        { hex: '#3b82f6', name: 'Accents / Details (Blue 500)' },

    ],

    vintageEditorial: [

        { hex: '#fdf6e3', name: 'Background / Sky (Cream)' },

        { hex: '#8b7355', name: 'Primary Shadows / Mid-dark (Muted Brown)' },

        {

            hex: '#d4c4a8',

            name: 'Primary Surface / Midtones (Warm Muted Beige)',

        },

        {

            hex: '#c96a52',

            name: 'Highlights / Secondary Lighting (Burnt Copper)',

        },

        { hex: '#2a2a2a', name: 'Accents / Details (Charcoal Black)' },

    ],

    boldCorporate: [

        { hex: '#ffffff', name: 'Background / Sky (Pure White)' },

        { hex: '#9ca3af', name: 'Primary Shadows / Outlines (Darker Gray)' },

        { hex: '#e5e7eb', name: 'Primary Surface / Midtones (Clean Gray)' },

        {

            hex: '#1d4ed8',

            name: 'Highlights / Secondary Lighting (High-contrast Blue)',

        },

        { hex: '#111827', name: 'Accents / Details (Stark Black)' },

    ],

    gameboy: [

        { hex: '#9bbc0f', name: 'Background / Sky (Lightest Green)' },

        {

            hex: '#306230',

            name: 'Primary Shadows / Deep Midtones (Dark Green)',

        },

        { hex: '#8bac0f', name: 'Primary Surface / Midtones (Light Green)' },

        {

            hex: '#0f380f',

            name: 'Highlights / Details / Outlines (Darkest Green)',

        },

    ],

    pico8: [

        { hex: '#000000', name: 'Background / Sky (Black)' },

        { hex: '#1D2B53', name: 'Primary Shadows (Dark Blue)' },

        { hex: '#5F574F', name: 'Primary Surface / Dark Midtones (Dark Gray)' },

        {

            hex: '#C2C3C7',

            name: 'Primary Surface / Light Midtones (Light Gray)',

        },

        { hex: '#FFF1E8', name: 'Highlights / Brightest (White/Peach)' },

        { hex: '#FF004D', name: 'Detail Accent (Red)' },

        { hex: '#FFA300', name: 'Detail Accent (Orange)' },

        { hex: '#FFEC27', name: 'Detail Accent (Yellow)' },

        { hex: '#00E436', name: 'Detail Accent (Green)' },

        { hex: '#29ADFF', name: 'Detail Accent (Blue)' },

        { hex: '#83769C', name: 'Detail Accent (Lavender)' },

        { hex: '#FF77A8', name: 'Detail Accent (Pink)' },

        { hex: '#FFCCAA', name: 'Detail Accent (Light Peach)' },

        { hex: '#7E2553', name: 'Secondary Shadow (Dark Purple)' },

        { hex: '#008751', name: 'Secondary Dark (Dark Green)' },

        { hex: '#AB5236', name: 'Secondary Earth (Brown)' },

    ],

    nesMario: [

        { hex: '#0070ec', name: 'Background / Sky (Sky Blue)' },

        { hex: '#801200', name: 'Primary Shadows (Dark Red/Brown)' },

        {

            hex: '#fc9838',

            name: 'Primary Surface / Midtones (Mario Peach/Orange)',

        },

        { hex: '#fcfcfc', name: 'Highlights / Whites (White)' },

        { hex: '#d82800', name: 'Detail Accent (Mario Red)' },

        { hex: '#000000', name: 'Detail Accent (Black)' },

        { hex: '#a4e4fc', name: 'Detail Accent (Light Blue)' },

        { hex: '#00a800', name: 'Detail Accent (Luigi Green)' },

        { hex: '#b8f818', name: 'Detail Accent (Bright Green)' },

        { hex: '#e45c10', name: 'Detail Accent (Brick Brown)' },

        { hex: '#0000bc', name: 'Detail Accent (Dark Blue)' },

        { hex: '#b8b8b8', name: 'Detail Accent (Gray)' },

        { hex: '#f8d878', name: 'Detail Accent (Gold Yellow)' },

        { hex: '#f8b8f8', name: 'Detail Accent (Pink Highlight)' },

    ],

    segaGenesis: [

        { hex: '#000000', name: 'Background / Sky (Black)' },

        { hex: '#103090', name: 'Primary Shadows (Sega Blue)' },

        { hex: '#2060e0', name: 'Primary Surface / Midtones (Sonic Blue)' },

        { hex: '#ffffff', name: 'Highlights / Whites (White)' },

        { hex: '#e0a000', name: 'Detail Accent (Rings Gold)' },

        { hex: '#f0e040', name: 'Detail Accent (Bright Yellow)' },

        { hex: '#e03000', name: 'Detail Accent (Red)' },

        { hex: '#a00000', name: 'Detail Accent (Dark Red)' },

        { hex: '#008000', name: 'Detail Accent (Grass Green)' },

        { hex: '#00e000', name: 'Detail Accent (Lime Green)' },

        { hex: '#604020', name: 'Detail Accent (Ground Brown)' },

        { hex: '#a07040', name: 'Detail Accent (Light Ground Brown)' },

        { hex: '#808080', name: 'Detail Accent (Gray)' },

        { hex: '#c0c0c0', name: 'Detail Accent (Light Gray)' },

        { hex: '#f080b0', name: 'Detail Accent (Peach/Pink)' },

        { hex: '#e0b090', name: 'Detail Accent (Skin tone)' },

    ],

    sweetie16: [

        { hex: '#1a1c2c', name: 'Background / Sky (Dark Violet)' },

        { hex: '#333c57', name: 'Primary Shadows (Dark Steel)' },

        { hex: '#566c86', name: 'Primary Surface / Midtones (Steel Blue)' },

        { hex: '#f4f4f4', name: 'Highlights / Whites (White)' },

        { hex: '#b13e53', name: 'Detail Accent (Red)' },

        { hex: '#ef7d57', name: 'Detail Accent (Orange)' },

        { hex: '#ffcd75', name: 'Detail Accent (Yellow)' },

        { hex: '#a7f070', name: 'Detail Accent (Light Green)' },

        { hex: '#38b764', name: 'Detail Accent (Green)' },

        { hex: '#257179', name: 'Detail Accent (Dark Teal)' },

        { hex: '#29366f', name: 'Detail Accent (Blue)' },

        { hex: '#3b5dc9', name: 'Detail Accent (Light Blue)' },

        { hex: '#41a6f6', name: 'Detail Accent (Sky Blue)' },

        { hex: '#73eff7', name: 'Detail Accent (Cyan)' },

        { hex: '#94b0c2', name: 'Detail Accent (Light Gray)' },

        { hex: '#5d275d', name: 'Secondary Shadow (Plum)' },

    ],

    bubblegum: [

        { hex: '#1a1a2e', name: 'Background / Sky (Deep Space Background)' },

        { hex: '#189ad3', name: 'Primary Shadows (Soft Blue)' },

        { hex: '#e2b2f8', name: 'Primary Surface / Midtones (Pastel Purple)' },

        { hex: '#ffffff', name: 'Highlights / Whites (Crisp White)' },

        { hex: '#ff7597', name: 'Detail Accent (Bubblegum Pink)' },

        { hex: '#ff9ebe', name: 'Detail Accent (Soft Pink)' },

        { hex: '#75e6da', name: 'Detail Accent (Mint/Cyan)' },

        { hex: '#fbe3b5', name: 'Detail Accent (Vanilla Yellow)' },

    ],

    vita32: [

        { hex: '#0d0d0d', name: 'Background / Sky (Near Black)' },

        { hex: '#1a1c23', name: 'Primary Shadows (Dark Slate)' },

        { hex: '#2d2f3b', name: 'Shadow Midtones (Dim Slate)' },

        { hex: '#3d4154', name: 'Deep Midtones (Muted Indigo)' },

        { hex: '#4f5468', name: 'Midtones (Cool Gray)' },

        { hex: '#6b7280', name: 'Light Midtones (Gray)' },

        { hex: '#9ca3af', name: 'Surface (Silver)' },

        { hex: '#d1d5db', name: 'Highlights / Light Surface (Light Gray)' },

        { hex: '#f3f4f6', name: 'Bright Highlights (Near White)' },

        { hex: '#ffffff', name: 'Pure White (White)' },

        { hex: '#dc2626', name: 'Vibrant Red (Red)' },

        { hex: '#991b1b', name: 'Dark Red / Crimson (Dark Red)' },

        { hex: '#f97316', name: 'Orange (Orange)' },

        { hex: '#f59e0b', name: 'Amber / Gold (Amber)' },

        { hex: '#eab308', name: 'Yellow (Yellow)' },

        { hex: '#84cc16', name: 'Lime Green (Lime)' },

        { hex: '#22c55e', name: 'Vibrant Green (Green)' },

        { hex: '#059669', name: 'Emerald / Deep Green (Emerald)' },

        { hex: '#14b8a6', name: 'Teal (Teal)' },

        { hex: '#06b6d4', name: 'Cyan (Cyan)' },

        { hex: '#3b82f6', name: 'Blue (Blue)' },

        { hex: '#1d4ed8', name: 'Deep Blue (Dark Blue)' },

        { hex: '#6366f1', name: 'Indigo (Indigo)' },

        { hex: '#8b5cf6', name: 'Violet (Violet)' },

        { hex: '#a855f7', name: 'Purple (Purple)' },

        { hex: '#d946ef', name: 'Fuchsia (Fuchsia)' },

        { hex: '#ec4899', name: 'Pink (Pink)' },

        { hex: '#f43f5e', name: 'Rose (Rose)' },

        { hex: '#78350f', name: 'Brown / Earth (Brown)' },

        { hex: '#92400e', name: 'Warm Brown / Leather (Tan)' },

        { hex: '#a16207', name: 'Olive / Khaki (Olive)' },

        { hex: '#e2e8f0', name: 'Ice / Frost (Ice Blue)' },

    ],

}




// --- App State ---

const state = {

    apiKey: import.meta.env.VITE_GEMINI_API_KEY || '',

    openRouterKey: import.meta.env.VITE_OPENROUTER_API_KEY || '',

    provider: 'gemini', // 'gemini' | 'openrouter'

    fallbackEnabled: true,

    autoSaveEnabled: false,

    model: 'gemini-3.5-flash',

    prompt: '',

    paletteId: 'pico8',

    isGenerating: false,

    currentInstructions: null,

    selectedLayerIndices: new Set(),

    followUpPrompt: '',

    currentSvgString: '',

    currentMetadata: null,

    saveDirHandle: null,

    // Cumulative metrics across all operations

    cumulative: {

        totalComputeTimeMs: 0,

        totalCost: 0,

        totalTokensIn: 0,

        totalTokensOut: 0,

    },

}




// --- DOM Elements (add cumulative metrics) ---

const DOM = {

    apiKeyInput: document.getElementById('apiKey'),

    openRouterKeyInput: document.getElementById('openRouterKey'),

    modelSelect: document.getElementById('modelPreset'),

    promptInput: document.getElementById('prompt'),

    paletteSelect: document.getElementById('palette'),

    paletteSwatches: document.getElementById('paletteSwatches'),




    providerGemini: document.getElementById('providerGemini'),

    providerOpenRouter: document.getElementById('providerOpenRouter'),

    geminiKeyGroup: document.getElementById('geminiKeyGroup'),

    openrouterKeyGroup: document.getElementById('openrouterKeyGroup'),

    fallbackToggle: document.getElementById('fallbackToggle'),

    autoSaveToggle: document.getElementById('autoSaveToggle'),




    generateBtn: document.getElementById('generateBtn'),

    generateSpinner: document.getElementById('generateSpinner'),

    downloadBtn: document.getElementById('downloadBtn'),

    highlightCanvas: document.getElementById('highlightCanvas'),

    displaySvgContainer: document.getElementById('displaySvgContainer'),

    emptyState: document.getElementById('emptyState'),

    statusContainer: document.getElementById('statusContainer'),

    statusLogs: document.getElementById('statusLogs'),




    errorBar: document.getElementById('errorBar'),

    errorMessage: document.getElementById('errorMessage'),




    jsonOutput: document.getElementById('jsonOutput'),




    metrics: {

        computeTime: document.getElementById('metricComputeTime'),

        coldStart: document.getElementById('metricColdStart'),

        tokens: document.getElementById('metricTokens'),

        billing: document.getElementById('metricBilling'),

    },




    // New layer selection / follow-up elements

    selectedLayerPanel: document.getElementById('selectedLayerPanel'),

    selectedLayerIndex: document.getElementById('selectedLayerIndex'),

    selectedLayerSwatch: document.getElementById('selectedLayerSwatch'),

    selectedLayerColor: document.getElementById('selectedLayerColor'),

    selPos: document.getElementById('selPos'),

    selSize: document.getElementById('selSize'),

    selColorIndex: document.getElementById('selColorIndex'),

    selDesc: document.getElementById('selDesc'),

    followUpBar: document.getElementById('followUpBar'),

    followUpInput: document.getElementById('followUpInput'),

    refineBtn: document.getElementById('refineBtn'),




    // Cumulative totals

    metricCumulativeTime: document.getElementById('metricCumulativeTime'),

    metricCumulativeCost: document.getElementById('metricCumulativeCost'),

}




// --- State Persistence ---

const STORAGE_KEY = 'pixelArtState_v2'




function saveFullState() {

    try {

        const data = {

            apiKey: state.apiKey,

            openRouterKey: state.openRouterKey,

            provider: state.provider,

            fallbackEnabled: state.fallbackEnabled,

            autoSaveEnabled: state.autoSaveEnabled,

            model: state.model,

            prompt: state.prompt,

            paletteId: state.paletteId,

        }

        localStorage.setItem(STORAGE_KEY, JSON.stringify(data))

    } catch (e) {

        console.warn('Failed to save state to localStorage:', e)

    }

}




function restoreFullState() {

    try {

        const raw = localStorage.getItem(STORAGE_KEY)

        if (!raw) return

        const saved = JSON.parse(raw)

        Object.assign(state, saved)

        if (!state.apiKey) state.apiKey = import.meta.env.VITE_GEMINI_API_KEY || ''

        if (!state.openRouterKey) state.openRouterKey = import.meta.env.VITE_OPENROUTER_API_KEY || ''

    } catch (e) {

        console.warn('Failed to restore state from localStorage:', e)

    }

}




function appStateChange() {

    saveFullState()

}




// --- Auto-Save SVGs ---

async function autoSaveSvgAndMetadata() {

    if (!state.autoSaveEnabled || !state.currentMetadata) return




    // Request directory handle on first save

    if (!state.saveDirHandle) {

        try {

            state.saveDirHandle = await window.showDirectoryPicker({

                mode: 'readwrite',

                id: 'pixel-art-saves',

                startIn: 'documents',

            })

        } catch (e) {

            // User cancelled directory picker — show a warning but keep toggle checked

            addStatusLog('Warning: Auto-save skipped — directory not selected.')

            return

        }

    }




    try {

        const safePrompt = state.prompt

            .replace(/[^a-z0-9]/gi, '_')

            .replace(/_+/g, '_')

            .toLowerCase()

            .substring(0, 40) || 'vector_art'

        

        // Clean model name (e.g. google/gemini-2.5-flash -> gemini-2.5-flash)

        const safeModel = state.model

            .replace(/^google\//i, '')

            .replace(/[^a-z0-9.-]/gi, '_')

            .toLowerCase()




        // Extract cost value (e.g., "$0.00015" -> "0_00015")

        let costVal = '0'

        if (state.currentMetadata && state.currentMetadata.activeBilling) {

            const costMatch = String(state.currentMetadata.activeBilling).match(/[\d.]+/)

            if (costMatch) {

                costVal = parseFloat(costMatch[0]).toFixed(8).replace(/\.?0+$/, '')

                costVal = costVal.replace('.', '_')

            }

        }




        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').substring(0, 19)

        const basename = `${timestamp}_${safePrompt}_${safeModel}_${costVal}`




        // Save SVG

        const svgFile = await state.saveDirHandle.getFileHandle(`${basename}.svg`, { create: true })

        const svgWritable = await svgFile.createWritable()

        await svgWritable.write(state.currentSvgString)

        await svgWritable.close()




        // Save metadata

        const metaFile = await state.saveDirHandle.getFileHandle(`${basename}.meta.json`, { create: true })

        const metaWritable = await metaFile.createWritable()

        const meta = {

            prompt: state.prompt,

            model: state.model,

            provider: state.provider,

            palette: state.paletteId,

            instructions: state.currentInstructions,

            metadata: state.currentMetadata,

            generatedAt: new Date().toISOString(),

        }

        await metaWritable.write(JSON.stringify(meta, null, 2))

        await metaWritable.close()




        addStatusLog(`Auto-saved: ${basename}.svg + ${basename}.meta.json`)

    } catch (e) {

        console.warn('Auto-save failed:', e)

        addStatusLog(`Warning: Auto-save failed — ${e.message}`)

    }

}




// --- Initialization ---

function init() {

    // Restore full state from localStorage

    restoreFullState()




    // Apply saved values to DOM

    DOM.apiKeyInput.value = state.apiKey || ''

    DOM.openRouterKeyInput.value = state.openRouterKey || ''

    DOM.modelSelect.value = state.model

    DOM.promptInput.value = state.prompt || ''

    DOM.paletteSelect.value = state.paletteId

    DOM.fallbackToggle.checked = state.fallbackEnabled

    DOM.autoSaveToggle.checked = state.autoSaveEnabled




    // Set initial swatches

    renderPaletteSwatches(state.paletteId)




    // Set initial provider state

    switchProvider(state.provider)




    // If a model's provider doesn't match, adjust

    const selectedOpt = DOM.modelSelect.selectedOptions?.[0]

    if (selectedOpt && selectedOpt.dataset.provider !== state.provider) {

        switchProvider(selectedOpt.dataset.provider)

    }




    // Attach Event Listeners

    DOM.apiKeyInput.addEventListener('input', (e) => {

        state.apiKey = e.target.value.trim()

        appStateChange()

    })




    DOM.openRouterKeyInput.addEventListener('input', (e) => {

        state.openRouterKey = e.target.value.trim()

        appStateChange()

    })




    // Provider switching

    function switchProvider(provider) {

        state.provider = provider

        appStateChange()

        // Toggle button styles

        ;[DOM.providerGemini, DOM.providerOpenRouter].forEach((btn) => {

            const p = btn.dataset.provider

            if (p === provider) {

                btn.classList.remove('bg-dark-700', 'text-slate-300')

                btn.classList.add(

                    'bg-blue-600',

                    'hover:bg-blue-500',

                    'text-white',

                    'font-bold'

                )

            } else {

                btn.classList.remove(

                    'bg-blue-600',

                    'hover:bg-blue-500',

                    'text-white',

                    'font-bold'

                )

                btn.classList.add(

                    'bg-dark-700',

                    'hover:bg-dark-600',

                    'text-slate-300',

                    'font-medium'

                )

            }

        })

        // Toggle key field visibility

        DOM.geminiKeyGroup.classList.toggle('hidden', provider !== 'gemini')

        DOM.openrouterKeyGroup.classList.toggle(

            'hidden',

            provider !== 'openrouter'

        )




        // Filter model dropdown to show only matching models

        for (const opt of DOM.modelSelect.options) {

            const optProvider = opt.dataset.provider

            opt.style.display =

                !optProvider || optProvider === provider ? '' : 'none'

        }

        // If current selection is hidden, pick first visible

        if (DOM.modelSelect.selectedOptions[0]?.style.display === 'none') {

            for (const opt of DOM.modelSelect.options) {

                if (opt.style.display !== 'none') {

                    DOM.modelSelect.value = opt.value

                    state.model = opt.value

                    break

                }

            }

        }

    }




    DOM.providerGemini.addEventListener('click', () => switchProvider('gemini'))

    DOM.providerOpenRouter.addEventListener('click', () =>

        switchProvider('openrouter')

    )




    DOM.modelSelect.addEventListener('change', (e) => {

        state.model = e.target.value

        // Auto-switch provider based on selected model's data-provider attribute

        const selectedOpt = e.target.selectedOptions[0]

        const modelProvider = selectedOpt?.dataset?.provider

        if (modelProvider && modelProvider !== state.provider) {

            switchProvider(modelProvider)

        }

        appStateChange()

    })




    DOM.fallbackToggle.addEventListener('change', (e) => {

        state.fallbackEnabled = e.target.checked

        appStateChange()

    })




    DOM.autoSaveToggle.addEventListener('change', (e) => {

        state.autoSaveEnabled = e.target.checked

        appStateChange()

    })




    DOM.promptInput.addEventListener(

        'input',

        (e) => {

            state.prompt = e.target.value

            appStateChange()

        }

    )




    DOM.generateBtn.addEventListener('click', handleGenerate)




    DOM.downloadBtn.addEventListener('click', handleDownload)




    // --- Layer Selection & Refinement Listeners ---

    DOM.displaySvgContainer.addEventListener('click', handleCanvasClick)




    DOM.refineBtn.addEventListener('click', handleRefine)




    DOM.followUpInput.addEventListener('keydown', (e) => {

        if (e.key === 'Enter') {

            e.preventDefault()

            handleRefine()

        }

    })




    // Canvas container needed for highlight positioning

    DOM.canvasContainer = document.getElementById('canvasContainer')




    // Live editing of JSON instructions

    DOM.jsonOutput.addEventListener('input', (e) => {

        try {

            const parsed = JSON.parse(e.target.value)

            if (parsed.instructions && Array.isArray(parsed.instructions)) {

                state.currentInstructions = parsed.instructions

                renderMatrix()

            }

        } catch (err) {

            // ignore JSON parse errors while typing

        }

    })




    // Reposition highlight overlay on resize

    window.addEventListener('resize', () => {

        if (state.selectedLayerIndices.size > 0 && state.currentInstructions) {

            repositionHighlightCanvas()

        }

    })

}




// --- UI Updates ---

function renderPaletteSwatches(paletteId) {

    const colors = PALETTES[paletteId]

    DOM.paletteSwatches.innerHTML = ''

    colors.forEach((colorObj) => {

        const swatch = document.createElement('div')

        swatch.className = 'flex-1 h-full'

        swatch.style.backgroundColor = colorObj.hex

        swatch.title = colorObj.name

        DOM.paletteSwatches.appendChild(swatch)

    })

}




function setGeneratingState(isGenerating) {

    state.isGenerating = isGenerating

    DOM.generateBtn.disabled = isGenerating

    DOM.apiKeyInput.disabled = isGenerating

    DOM.promptInput.disabled = isGenerating

    DOM.refineBtn.disabled = isGenerating

    DOM.followUpInput.disabled = isGenerating




    if (isGenerating) {

        DOM.generateSpinner.classList.remove('hidden')

        DOM.generateBtn.classList.add('opacity-80', 'cursor-not-allowed')




        DOM.emptyState.classList.add('hidden')

        DOM.highlightCanvas.classList.add('hidden')

        DOM.displaySvgContainer.classList.add('hidden')

        DOM.statusContainer.classList.remove('hidden')

        DOM.statusLogs.innerHTML = ''




        // Hide layer selection while generating

        DOM.selectedLayerPanel.classList.add('hidden')

        DOM.followUpBar.classList.add('hidden')




        hideError()

    } else {

        DOM.generateSpinner.classList.add('hidden')

        DOM.generateBtn.classList.remove('opacity-80', 'cursor-not-allowed')

        DOM.statusContainer.classList.add('hidden')




        if (state.currentInstructions) {

            renderMatrix()

        } else {

            DOM.emptyState.classList.remove('hidden')

        }

    }

}




function addStatusLog(message) {

    if (!DOM.statusLogs) return




    const logItem = document.createElement('div')

    logItem.className =

        'py-1 border-b border-dark-700/30 flex items-start gap-2 text-slate-400'




    let prefix = '●'

    let prefixColor = 'text-blue-500'

    let textColor = 'text-slate-300'




    if (message.startsWith('Error:')) {

        prefixColor = 'text-red-500 animate-pulse'

        textColor = 'text-red-400 font-semibold'

    } else if (message.startsWith('Warning:')) {

        prefixColor = 'text-yellow-500'

        textColor = 'text-yellow-400'

    } else if (

        message.includes('complete!') ||

        message.includes('successfully')

    ) {

        prefixColor = 'text-emerald-500'

        textColor = 'text-emerald-400 font-semibold'

    } else if (

        message.includes('Sending request') ||

        message.includes('waiting')

    ) {

        prefixColor = 'text-cyan-500 animate-pulse'

        textColor = 'text-cyan-300'

    }




    logItem.innerHTML = `

        <span class="${prefixColor} text-[8px] mt-1 shrink-0">${prefix}</span>

        <span class="${textColor} break-words flex-1">${message}</span>

    `




    DOM.statusLogs.appendChild(logItem)

    DOM.statusLogs.scrollTop = DOM.statusLogs.scrollHeight

}




function showError(msg) {

    DOM.errorMessage.textContent = msg

    DOM.errorBar.classList.remove('hidden')

    setTimeout(hideError, 8000)

}




function hideError() {

    DOM.errorBar.classList.add('hidden')

    DOM.errorMessage.textContent = ''

}




function formatCostDisplay(costInDollars) {

    if (costInDollars === 0) return '0¢';

    if (costInDollars < 1) {

        const cents = costInDollars * 100;

        return `${cents.toPrecision(4)}¢`;

    }

    return `$${costInDollars.toPrecision(4)}`;

}




function formatBillingString(billingStr) {

    if (!billingStr) return '';

    const hasApprox = billingStr.includes('≈') || billingStr.includes('~');

    const costMatch = billingStr.match(/[\d.]+/);

    if (!costMatch) return billingStr;

    const costInDollars = parseFloat(costMatch[0]);

    const formatted = formatCostDisplay(costInDollars);

    return (hasApprox ? '≈' : '') + formatted;

}




function updateMetrics(metadata) {

    if (!metadata) return

    DOM.metrics.computeTime.textContent = `${metadata.computeTime}s`

    DOM.metrics.coldStart.textContent = `${metadata.coldStart}ms`

    DOM.metrics.tokens.textContent = `${metadata.promptTokens || 0} / ${metadata.tokensOut || 0}`

    DOM.metrics.billing.textContent = formatBillingString(metadata.activeBilling)

}




function updateCumulativeMetrics() {

    DOM.metricCumulativeTime.textContent = `${(state.cumulative.totalComputeTimeMs / 1000).toFixed(2)}s`

    DOM.metricCumulativeCost.textContent = formatCostDisplay(state.cumulative.totalCost)

}




function accumulateMetadata(metadata) {

    if (!metadata) return

    const computeMs = parseFloat(metadata.computeTime || 0) * 1000

    state.cumulative.totalComputeTimeMs += computeMs

    state.cumulative.totalTokensIn += metadata.promptTokens || 0

    state.cumulative.totalTokensOut += metadata.tokensOut || 0

    // Extract cost from billing string like "$0.00123"

    const costMatch = String(metadata.activeBilling).match(/[\d.]+/)

    if (costMatch) {

        state.cumulative.totalCost += parseFloat(costMatch[0])

    }

    updateCumulativeMetrics()

}




// --- Generation Logic ---

async function handleGenerate() {

    if (state.provider === 'gemini' && !state.apiKey) {

        showError('Please enter your Gemini API Key.')

        return

    }

    if (state.provider === 'openrouter' && !state.openRouterKey) {

        showError('Please enter your OpenRouter API Key.')

        return

    }

    if (!state.prompt.trim()) {

        showError('Please enter an asset description.')

        return

    }




    setGeneratingState(true)




    try {

        const palette = PALETTES[state.paletteId]




        const result = await generateWithProvider(state.provider, palette)




        state.currentInstructions = result.instructions

        state.currentMetadata = result.metadata




        // Update Wireframe JSON view

        DOM.jsonOutput.value = JSON.stringify(

            { instructions: result.instructions },

            null,

            2

        )




        // Update Performance Monitor

        updateMetrics(result.metadata)




        // Accumulate into cumulative totals

        accumulateMetadata(result.metadata)




        // Render Visuals

        renderMatrix()




        // Enable Download

        DOM.downloadBtn.disabled = false




        // Reset selections when new image generated

        clearLayerSelection()




        // Auto-save SVG + metadata

        await autoSaveSvgAndMetadata()

    } catch (error) {

        console.error('Generation failed:', error)

        // Attempt fallback to OpenRouter if Gemini failed and fallback is enabled

        if (

            state.provider === 'gemini' &&

            state.fallbackEnabled &&

            state.openRouterKey

        ) {

            addStatusLog(

                'Warning: Gemini failed. Falling back to OpenRouter...'

            )

            try {

                // Map Gemini model name to OpenRouter equivalent (prepend google/)

                const geminiToOpenRouter = state.model.startsWith('gemini-')

                    ? 'google/' + state.model

                    : 'deepseek/deepseek-v4-flash'

                const fallbackModel = geminiToOpenRouter

                addStatusLog(

                    `Fallback: trying ${fallbackModel} via OpenRouter...`

                )




                const palette = PALETTES[state.paletteId]

                const result = await OpenRouterService.generateVectorArt(

                    state.openRouterKey,

                    fallbackModel,

                    state.prompt,

                    1024,

                    palette,

                    (msg) => addStatusLog(msg)

                )




                state.currentInstructions = result.instructions

                state.currentMetadata = result.metadata

                DOM.jsonOutput.value = JSON.stringify(

                    { instructions: result.instructions },

                    null,

                    2

                )

                updateMetrics(result.metadata)

                renderMatrix()

                DOM.downloadBtn.disabled = false




                // Auto-save fallback result too

                await autoSaveSvgAndMetadata()




                addStatusLog('Fallback generation succeeded!')

                return

            } catch (fallbackError) {

                console.error('Fallback also failed:', fallbackError)

                showError(

                    `Gemini: ${error.message}. Fallback: ${fallbackError.message}`

                )

                return

            }

        }

        showError(error.message || 'Failed to generate asset.')

    } finally {

        setGeneratingState(false)

    }

}




async function generateWithProvider(provider, palette) {

    if (provider === 'openrouter') {

        addStatusLog(`Generating via OpenRouter (${state.model})...`)

        return await OpenRouterService.generateVectorArt(

            state.openRouterKey,

            state.model,

            state.prompt,

            1024,

            palette,

            (msg) => addStatusLog(msg)

        )

    } else {

        return await GenerationService.generateVectorArt(

            state.apiKey,

            state.model,

            state.prompt,

            1024,

            palette,

            (msg) => addStatusLog(msg)

        )

    }

}




// --- Rendering Engines ---

function renderMatrix() {

    if (!state.currentInstructions) return




    DOM.emptyState.classList.add('hidden')

    DOM.statusContainer.classList.add('hidden')




    // Draw Canvas (Raster)




    DOM.displaySvgContainer.classList.remove('hidden')

    // Draw SVG (Vector)

    drawSvgVector(

        state.currentInstructions,

        PALETTES[state.paletteId],

        1024

    )




    // Re-draw highlight if layer(s) selected, otherwise hide highlight canvas

    if (state.selectedLayerIndices.size > 0) {

        drawHighlight(

            state.selectedLayerIndices,

            1024

        )

    } else {

        DOM.highlightCanvas.classList.add('hidden')

    }

}




// --- Layer Selection & Highlight ---

function handleCanvasClick(e) {

    if (!state.currentInstructions) return




    let foundIndex = -1




    let target = e.target;

    while (target && target !== DOM.displaySvgContainer) {

        if (target.hasAttribute('data-index')) {

            foundIndex = parseInt(target.getAttribute('data-index'), 10);

            if (foundIndex === 0) foundIndex = -1; // Ignore background click

            break;

        }

        target = target.parentElement;

    }




    // Clicking empty area (no foreground rect) deselects

    if (foundIndex === -1) {

        clearLayerSelection()

        return

    }




    const shiftHeld = e.shiftKey




    if (shiftHeld) {

        // Toggle this index in/out of the current selection

        if (state.selectedLayerIndices.has(foundIndex)) {

            state.selectedLayerIndices.delete(foundIndex)

        } else {

            state.selectedLayerIndices.add(foundIndex)

        }

    } else {

        // No shift — replace selection with just this layer

        state.selectedLayerIndices.clear()

        state.selectedLayerIndices.add(foundIndex)

    }




    // Update highlights and UI

    drawHighlight(state.selectedLayerIndices, 1024)

    updateSelectedLayerUI(1024)

}




function drawHighlight(selectedIndices, gridSize) {

    const canvas = DOM.highlightCanvas

    canvas.width = gridSize

    canvas.height = gridSize




    // MUST remove hidden BEFORE repositioning (reposition checks hidden state)

    canvas.classList.remove('hidden')




    // Position highlight canvas exactly over displaySvgContainer

    repositionHighlightCanvas()




    const ctx = canvas.getContext('2d')




    if (!selectedIndices || selectedIndices.size === 0) return




    for (const idx of selectedIndices) {

        const inst = state.currentInstructions?.[idx]

        if (!inst) continue




        let minX = 0, minY = 0, maxX = 0, maxY = 0;




        const svgEl = DOM.displaySvgContainer.querySelector(`[data-index="${idx}"]`);

        if (svgEl && svgEl.getBBox) {

            const bbox = svgEl.getBBox();

            minX = bbox.x;

            minY = bbox.y;

            maxX = bbox.x + bbox.width;

            maxY = bbox.y + bbox.height;

        } else {

            continue;

        }




        const x = minX;

        const y = minY;

        const w = maxX - minX;

        const h = maxY - minY;




        // Outer glow (semi-transparent white border)

        ctx.strokeStyle = 'rgba(255, 255, 255, 0.9)'

        ctx.lineWidth = 2

        ctx.strokeRect(x - 1.5, y - 1.5, w + 3, h + 3)




        // Inner bright border

        ctx.strokeStyle = '#00e5ff'

        ctx.lineWidth = 1

        ctx.strokeRect(x - 1, y - 1, w + 2, h + 2)




        // Faint highlight fill

        ctx.fillStyle = 'rgba(0, 229, 255, 0.12)'

        ctx.fillRect(x, y, w, h)

    }

}




function updateSelectedLayerUI(gridSize) {

    const count = state.selectedLayerIndices.size

    if (count === 0) {

        // Show follow-up bar for no-selection refinement

        DOM.selectedLayerPanel.classList.add('hidden')

        DOM.followUpBar.classList.remove('hidden')

        DOM.followUpInput.value = ''

        DOM.followUpInput.placeholder = 'Refine the whole image...'

        DOM.followUpInput.focus()

        return

    }




    DOM.selectedLayerPanel.classList.remove('hidden')

    DOM.followUpBar.classList.remove('hidden')

    DOM.followUpInput.placeholder = 'e.g. make it taller, change color to red...'

    DOM.followUpInput.value = ''

    DOM.followUpInput.focus()




    if (count === 1) {

        const index = [...state.selectedLayerIndices][0]

        const inst = state.currentInstructions[index]

        const palette = PALETTES[state.paletteId]




        DOM.selectedLayerIndex.textContent = `#${index}`

        DOM.selPos.textContent = `(${inst.x ?? 0}, ${inst.y ?? 0})`

        DOM.selSize.textContent = `${inst.w ?? 0} × ${inst.h ?? 0}`

        DOM.selColorIndex.textContent = `${inst.colorIndex ?? 0}`




        const validIndex = Math.min(

            Math.max(0, inst.colorIndex ?? 0),

            palette.length - 1

        )

        const colorObj = palette[validIndex]

        const hex = colorObj.hex

        DOM.selectedLayerSwatch.style.backgroundColor = hex

        DOM.selectedLayerColor.textContent = `${hex} (${colorObj.name})`

        DOM.selectedLayerColor.style.color = hex




        const desc = inst.description || '—'

        DOM.selDesc.textContent = desc

        DOM.selDesc.title = desc

    } else {

        // Multiple selections — show summary

        const indices = [...state.selectedLayerIndices].sort((a, b) => a - b)

        DOM.selectedLayerIndex.textContent = `#${indices.join(', #')}`

        DOM.selPos.textContent = `${count} layers`

        DOM.selSize.textContent = '—'

        DOM.selColorIndex.textContent = '—'

        DOM.selectedLayerSwatch.style.backgroundColor = '#888'

        DOM.selectedLayerColor.textContent = `Multiple (${count})`

        DOM.selectedLayerColor.style.color = '#888'

        DOM.selDesc.textContent = '—'

        DOM.selDesc.title = ''

    }

}




function clearLayerSelection() {

    state.selectedLayerIndices.clear()

    DOM.selectedLayerPanel.classList.add('hidden')

    // Keep follow-up bar visible so user can refine without selection

    DOM.followUpBar.classList.remove('hidden')

    DOM.followUpInput.value = ''

    DOM.followUpInput.placeholder = 'Refine the whole image...'

    DOM.highlightCanvas.classList.add('hidden')

}




function repositionHighlightCanvas() {

    if (

        !DOM.highlightCanvas ||

        DOM.highlightCanvas.classList.contains('hidden')

    )

        return

    const activeEl = DOM.displaySvgContainer

    const displayRect = activeEl.getBoundingClientRect()

    const containerRect = DOM.canvasContainer.getBoundingClientRect()

    DOM.highlightCanvas.style.left =

        displayRect.left - containerRect.left + 'px'

    DOM.highlightCanvas.style.top = displayRect.top - containerRect.top + 'px'

    DOM.highlightCanvas.style.width = displayRect.width + 'px'

    DOM.highlightCanvas.style.height = displayRect.height + 'px'

}




// --- Follow-up Refinement ---

async function handleRefine() {

    const refineText = DOM.followUpInput.value.trim()

    if (!refineText || !state.currentInstructions) return




    if (state.provider === 'gemini' && !state.apiKey) {

        showError('Please enter your Gemini API Key.')

        return

    }

    if (state.provider === 'openrouter' && !state.openRouterKey) {

        showError('Please enter your OpenRouter API Key.')

        return

    }




    const selectedIndices = [...state.selectedLayerIndices].sort((a, b) => a - b)

    const palette = PALETTES[state.paletteId]

    const gridSize = 1024




    setGeneratingState(true)




    try {

        let result




        if (selectedIndices.length === 1) {

            // Single-selection refinement

            const index = selectedIndices[0]

            const inst = state.currentInstructions[index]




            if (state.provider === 'openrouter') {

                result = await OpenRouterService.refineLayer(

                    state.openRouterKey,

                    state.model,

                    state.prompt,

                    gridSize,

                    palette,

                    inst,

                    index,

                    refineText,

                    (msg) => addStatusLog(msg),

                    state.currentInstructions // pass all instructions for context

                )

            } else {

                result = await GenerationService.refineLayer(

                    state.apiKey,

                    state.model,

                    state.prompt,

                    gridSize,

                    palette,

                    inst,

                    index,

                    refineText,

                    (msg) => addStatusLog(msg),

                    state.currentInstructions

                )

            }




            // Replace the selected instruction with the refined version(s)

            const before = state.currentInstructions.slice(0, index)

            const after = state.currentInstructions.slice(index + 1)

            state.currentInstructions = [

                ...before,

                ...(result.replacement || []),

                ...after,

            ]




        } else {

            // Multi-selection or no-selection: do global refinement

            // When multiple selected, include a note about which layers to focus on

            const focusNote = selectedIndices.length > 0

                ? `Focus on these layer indices: ${selectedIndices.join(', ')}`

                : 'Apply to the entire composition.'




            if (state.provider === 'openrouter') {

                result = await OpenRouterService.refineLayer(

                    state.openRouterKey,

                    state.model,

                    state.prompt,

                    gridSize,

                    palette,

                    null, // no single target

                    -1,

                    `${refineText}\n\n${focusNote}`,

                    (msg) => addStatusLog(msg),

                    state.currentInstructions

                )

            } else {

                result = await GenerationService.refineLayer(

                    state.apiKey,

                    state.model,

                    state.prompt,

                    gridSize,

                    palette,

                    null,

                    -1,

                    `${refineText}\n\n${focusNote}`,

                    (msg) => addStatusLog(msg),

                    state.currentInstructions

                )

            }




            // Full replacement (global refinement)

            state.currentInstructions = result.replacement

        }




        // Update JSON view

        DOM.jsonOutput.value = JSON.stringify(

            { instructions: state.currentInstructions },

            null,

            2

        )




        // Update per-op metrics with refinement metadata

        if (result.meta) {

            updateMetrics(result.meta)

            accumulateMetadata(result.meta)

        }




        // Re-render

        renderMatrix()




        // Clear selection after refinement

        clearLayerSelection()




        addStatusLog('Refinement applied successfully!')




        // Auto-save the refined result

        await autoSaveSvgAndMetadata()




    } catch (error) {

        console.error('Refinement failed:', error)

        // Fallback refine if Gemini fails

        if (

            state.provider === 'gemini' &&

            state.fallbackEnabled &&

            state.openRouterKey

        ) {

            addStatusLog(

                'Warning: Gemini refinement failed. Falling back to OpenRouter...'

            )

            try {

                const geminiToOpenRouter = state.model.startsWith('gemini-')

                    ? 'google/' + state.model

                    : 'deepseek/deepseek-v4-flash'

                const fallbackModel = geminiToOpenRouter

                const selectedIndices = [...state.selectedLayerIndices].sort((a, b) => a - b)

                let result




                if (selectedIndices.length === 1) {

                    const index = selectedIndices[0]

                    const inst = state.currentInstructions[index]

                    result = await OpenRouterService.refineLayer(

                        state.openRouterKey,

                        fallbackModel,

                        state.prompt,

                        gridSize,

                        palette,

                        inst,

                        index,

                        refineText,

                        (msg) => addStatusLog(msg),

                        state.currentInstructions

                    )




                    const before = state.currentInstructions.slice(0, index)

                    const after = state.currentInstructions.slice(index + 1)

                    state.currentInstructions = [

                        ...before,

                        ...(result.replacement || []),

                        ...after,

                    ]

                } else {

                    const focusNote = selectedIndices.length > 0

                        ? `Focus on these layer indices: ${selectedIndices.join(', ')}`

                        : 'Apply to the entire composition.'




                    result = await OpenRouterService.refineLayer(

                        state.openRouterKey,

                        fallbackModel,

                        state.prompt,

                        gridSize,

                        palette,

                        null,

                        -1,

                        `${refineText}\n\n${focusNote}`,

                        (msg) => addStatusLog(msg),

                        state.currentInstructions

                    )




                    state.currentInstructions = result.replacement

                }




                DOM.jsonOutput.value = JSON.stringify(

                    { instructions: state.currentInstructions },

                    null,

                    2

                )




                // Update per-op metrics

                if (result.meta) {

                    updateMetrics(result.meta)

                    accumulateMetadata(result.meta)

                }




                renderMatrix()

                clearLayerSelection()

                addStatusLog('Fallback refinement succeeded!')




                await autoSaveSvgAndMetadata()

                return

            } catch (fbError) {

                showError(

                    `Refinement failed (Gemini: ${error.message}, fallback: ${fbError.message})`

                )

                return

            }

        }

        showError(error.message || 'Failed to refine layer.')

    } finally {

        setGeneratingState(false)

    }

}




function drawSvgVector(instructions, palette, gridSize) {

    let svgContent = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${gridSize} ${gridSize}" width="100%" height="100%" shape-rendering="geometricPrecision">`




    // Fill background with index 0

    const bgIndex = 0

    const bgColor = palette[bgIndex]?.hex || '#000000'

    svgContent += `<rect data-index="0" x="0" y="0" width="${gridSize}" height="${gridSize}" fill="${bgColor}" />`




    for (let i = 0; i < instructions.length; i++) {

        const inst = instructions[i]

        const rawIndex = inst.colorIndex !== undefined ? inst.colorIndex : inst.color !== undefined ? inst.color : 0

        const validIndex = Math.min(Math.max(0, rawIndex), palette.length - 1)

        const color = palette[validIndex]?.hex || '#000000'




        const opacityStr = inst.opacity !== undefined ? ` opacity="${inst.opacity}"` : ''

        const strokeColor = inst.strokeColorIndex !== undefined ? (palette[Math.min(Math.max(0, inst.strokeColorIndex), palette.length - 1)]?.hex || 'none') : 'none'

        const strokeStr = strokeColor !== 'none' ? ` stroke="${strokeColor}"` : ''

        const strokeWidthStr = inst.strokeWidth !== undefined ? ` stroke-width="${inst.strokeWidth}"` : ''

        const styleStr = `${opacityStr}${strokeStr}${strokeWidthStr}`




        if (inst.type === 'rect') {

            let w = inst.w

            let h = inst.h

            if (w === undefined || w < 0 || h === undefined || h < 0) {

                // Skip the instruction to prevent breaking the SVG context

                continue

            }

            const x = inst.x !== undefined ? inst.x : 0

            const y = inst.y !== undefined ? inst.y : 0

            svgContent += `<rect data-index="${i}" x="${x}" y="${y}" width="${w}" height="${h}" fill="${color}"${styleStr} />`

        } else if (inst.type === 'circle') {

            const cx = inst.cx !== undefined ? inst.cx : 0

            const cy = inst.cy !== undefined ? inst.cy : 0

            const r = inst.r !== undefined ? inst.r : 0

            if (r < 0) continue

            svgContent += `<circle data-index="${i}" cx="${cx}" cy="${cy}" r="${r}" fill="${color}"${styleStr} />`

        } else if (inst.type === 'polygon') {

            const points = inst.points || ''

            svgContent += `<polygon data-index="${i}" points="${points}" fill="${color}"${styleStr} />`

        } else if (inst.type === 'path') {

            const d = inst.d || ''

            svgContent += `<path data-index="${i}" d="${d}" fill="${color}"${styleStr} />`

        }

    }




    svgContent += `</svg>`

    DOM.displaySvgContainer.innerHTML = svgContent

    state.currentSvgString = svgContent

}




function handleDownload() {

    if (!state.currentInstructions) return




    let safePrompt = state.prompt

        .replace(/[^a-z0-9]/gi, '_')

        .toLowerCase()

        .substring(0, 30)

    if (!safePrompt) safePrompt = 'vector_art'




    if (!state.currentSvgString) return




    const blob = new Blob([state.currentSvgString], {

        type: 'image/svg+xml;charset=utf-8',

    })

    const url = URL.createObjectURL(blob)

    const a = document.createElement('a')

    a.href = url

    a.download = `${safePrompt}_vector.svg`

    document.body.appendChild(a)

    a.click()

    document.body.removeChild(a)

    URL.revokeObjectURL(url)

}




// Boot

init()




```




`package.json`:




```json

{

  "name": "vector-art-generator",

  "version": "1.0.0",

  "description": "",

  "main": "index.js",

  "scripts": {

    "dev": "vite",

    "build": "vite build",

    "preview": "vite preview",

    "test": "echo \"Error: no test specified\" && exit 1"

  },

  "keywords": [],

  "author": "",

  "license": "ISC",

  "devEngines": {

    "packageManager": {

      "name": "pnpm",

      "version": "^11.2.2",

      "onFail": "download"

    }

  },

  "type": "module",

  "devDependencies": {

    "vite": "^8.1.0"

  }

}




```

---

[2026-06-30 23:23] Assistant:
Defining the Approach
Gemini said
