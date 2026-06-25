import fs from 'fs';
import path from 'path';

const CACHE_FILE = path.resolve(process.cwd(), 'tmp/pricing_cache.json');

// Accurate fallback pricing for Gemini models per 1M tokens
const FALLBACK_PRICING = {
  'gemini-3.5-flash': { input: 1.50, output: 9.00 },
  'gemini-3.1-flash-lite': { input: 0.25, output: 1.50 },
  'gemini-3.1-pro': { input: 2.00, output: 12.00 },
  'gemini-2.5-pro': { input: 1.25, output: 10.00 },
  'gemini-2.5-flash': { input: 0.30, output: 2.50 },
  'gemini-2.5-flash-lite': { input: 0.10, output: 0.40 },
  'gemini-2.0-flash-lite': { input: 0.10, output: 0.40 },
  'gemini-2.0-flash': { input: 0.075, output: 0.30 },
  'gemini-1.5-pro': { input: 1.25, output: 5.00 },
  'gemini-1.5-flash': { input: 0.075, output: 0.30 },
  'default': { input: 0.30, output: 2.50 } // Fallback default
};

let pricingData = {};

export function getCachedPricing() {
  return pricingData;
}

export function formatTokens(count) {
  if (count === undefined || count === null || isNaN(count)) return '0';
  if (count < 1000) return String(count);
  if (count < 1000000) {
    const val = count / 1000;
    return (val >= 10 ? Math.round(val) : val.toFixed(1).replace(/\.0$/, '')) + 'k';
  }
  const val = count / 1000000;
  return val.toFixed(1).replace(/\.0$/, '') + 'M';
}

// Map model names to OpenRouter or Fallback pricing
function matchModelPricing(modelName) {
  if (!modelName) return FALLBACK_PRICING.default;
  const nameLower = modelName.toLowerCase();

  // 1. Try to find a match in the dynamic pricing data
  // OpenRouter model IDs look like: "google/gemini-2.5-flash"
  const dynamicKeys = Object.keys(pricingData);
  for (const key of dynamicKeys) {
    const keyLower = key.toLowerCase();
    if (keyLower === nameLower || keyLower.endsWith('/' + nameLower) || nameLower.includes(keyLower) || keyLower.includes(nameLower)) {
      const match = pricingData[key];
      if (match && match.pricing) {
        return {
          input: parseFloat(match.pricing.prompt) * 1000000,
          output: parseFloat(match.pricing.completion) * 1000000
        };
      }
    }
  }

  // 2. Fall back to local database
  const fallbackKeys = Object.keys(FALLBACK_PRICING);
  for (const key of fallbackKeys) {
    if (nameLower.includes(key)) {
      return FALLBACK_PRICING[key];
    }
  }

  return FALLBACK_PRICING.default;
}

export function calculateCost(model, inputTokens, outputTokens) {
  const pricing = matchModelPricing(model);
  const inputCost = (inputTokens * pricing.input) / 1000000;
  const outputCost = (outputTokens * pricing.output) / 1000000;
  return inputCost + outputCost;
}

export async function loadPricing() {
  // Load cache synchronously first to ensure immediate availability
  try {
    if (fs.existsSync(CACHE_FILE)) {
      const content = fs.readFileSync(CACHE_FILE, 'utf8');
      pricingData = JSON.parse(content);
    }
  } catch (err) {
    // Ignore cache load errors
  }

  // Trigger background fetch with a timeout
  try {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), 2000); // 2 second timeout

    const res = await fetch('https://openrouter.ai/api/v1/models', { signal: controller.signal });
    clearTimeout(id);

    if (res.ok) {
      const data = await res.json();
      if (data && Array.isArray(data.data)) {
        const newPricing = {};
        data.data.forEach(m => {
          if (m.id && m.pricing) {
            newPricing[m.id] = m;
          }
        });
        pricingData = newPricing;

        // Ensure tmp dir exists
        const tmpDir = path.dirname(CACHE_FILE);
        if (!fs.existsSync(tmpDir)) {
          fs.mkdirSync(tmpDir, { recursive: true });
        }
        fs.writeFileSync(CACHE_FILE, JSON.stringify(pricingData, null, 2), 'utf8');
      }
    }
  } catch (err) {
    // Fail silently in background to keep app execution completely uninterrupted
  }
}
