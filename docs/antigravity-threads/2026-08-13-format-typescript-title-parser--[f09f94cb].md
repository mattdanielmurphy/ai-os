---
title: "Format TypeScript Title Parser"
date: "2026-08-13"
conversation_id: "f09f94cb-24e0-438f-9535-b4cc1d567029"
source: "antigravity"
---

# Format TypeScript Title Parser

## User

Cleanly format `/Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.ts` into clean, well-formatted multi-line TypeScript. Fix the syntax errors (remove `@ts-expect-error` comments placed inside statement positions or replace with proper `// @ts-ignore` line comments or `(window as any)` typecasts).

Here is the exact implementation to write to `/Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.ts`:

```typescript
export function decodeHtmlEntities(text: string): string {
  const entities: Record<string, string> = {
    '&amp;': '&',
    '&#39;': "'",
    '&quot;': '"',
    '&lt;': '<',
    '&gt;': '>',
    '&nbsp;': ' ',
  };
  return text.replace(/&amp;|&#39;|&quot;|&lt;|&gt;|&nbsp;/g, (m) => entities[m] || m);
}

export function normalizeBrackets(text: string): string {
  return text
    .replace(/（/g, '(')
    .replace(/）/g, ')')
    .replace(/【/g, '[')
    .replace(/】/g, ']')
    .replace(/［/g, '[')
    .replace(/］/g, ']');
}

export function stripNoiseTags(text: string): string {
  const noisePatterns = [
    /\(official (video|music video|audio|lyric video|hd video)\)/gi,
    /\((lyric video|visualizer|full album|full album stream|hq|hd|4k|1080p|lyrics|audio|explicit|clean|deluxe edition)\)/gi,
    /\(remastered.*?\)/gi,
    /\(\d{4} remaster\)/gi,
    /\[official (video|music video|audio|lyric video|hd video)\]/gi,
    /\[(lyric video|visualizer|full album|full album stream|hq|hd|4k|1080p|lyrics|audio|explicit|clean|deluxe edition)\]/gi,
    /\[remastered.*?\]/gi,
    /\[\d{4} remaster\]/gi,
  ];

  let result = text;
  let previous: string;
  do {
    previous = result;
    for (const pattern of noisePatterns) {
      result = result.replace(pattern, '');
    }
  } while (result !== previous);

  return result.trim().replace(/\s+/g, ' ');
}

export function repairUnmatchedBrackets(text: string): string {
  let openCount = 0;
  let cleaned = '';
  for (let i = 0; i < text.length; i++) {
    const char = text[i];
    if (char === '(' || char === '
<truncated 1840 bytes>
 === 'function') {
      const cap = await LM.capabilities();
      return cap.available === 'readily' ? 'available' : 'unavailable';
    }
  } catch {
    return 'unavailable';
  }
  return 'unavailable';
}

export async function parseYouTubeTitleHybrid(rawTitle: string, channelName?: string): Promise<{ artist: string | null; title: string }> {
  const cleaned = cleanYouTubeTitle(rawTitle);
  if (typeof self !== 'undefined' && (await getChromeAIAvailability()) === 'available') {
    let session: any = null;
    try {
      const globalAny = self as any;
      const LM = globalAny.LanguageModel ?? globalAny.ai?.languageModel;
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 1500);

      session = await LM.create({
        systemPrompt: 'Extract artist and title from YouTube video title. Return JSON object with keys "artist" and "title".',
        responseConstraint: {
          type: 'object',
          properties: {
            artist: { type: 'string' },
            title: { type: 'string' },
          },
          required: ['title'],
        },
      });

      const resultText = await session.prompt(cleaned, { signal: controller.signal });
      clearTimeout(timeout);
      const parsed = JSON.parse(resultText);
      if (parsed && typeof parsed.title === 'string') {
        return {
          artist: parsed.artist || (channelName && channelName.endsWith(' - Topic') ? channelName.replace(' - Topic', '') : null),
          title: parsed.title,
        };
      }
    } catch (e) {
      console.warn('AI Parsing failed, falling back to regex:', e);
    } finally {
      if (session && typeof session.destroy === 'function') {
        session.destroy();
      }
    }
  }

  return parseYouTubeTitle(rawTitle, channelName);
}
```

Write this exact clean TypeScript code to `/Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.ts`.

---

## Assistant

The file `/Users/matt/projects/music-cross-linker/app/lib/youtube/titleParser.ts` has been cleaned, formatted, and updated to fix syntax errors by replacing misplaced `@ts-expect-error` comments with appropriate `as any` typecasts.

---
