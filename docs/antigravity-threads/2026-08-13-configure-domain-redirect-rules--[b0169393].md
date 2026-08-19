---
title: "Configure Domain Redirect Rules"
date: "2026-08-13"
conversation_id: "b0169393-593c-4369-ab24-10e70108c483"
source: "antigravity"
---

# Configure Domain Redirect Rules

## User

Add a redirect for music.mattmurphy.ca or /music path in /Users/matt/projects/mattmurphy.ca/next.config.js or vercel.json if needed.

Specifically, in /Users/matt/projects/mattmurphy.ca/vercel.json, add a redirect or rewrite rule, or in next.config.js redirects/rewrites, so that requests to `music.mattmurphy.ca` or wildcard path redirects appropriately.

Wait, check vercel.json in /Users/matt/projects/mattmurphy.ca/vercel.json:
Add a redirect to `vercel.json` under `redirects`:
{
  "source": "/:path*",
  "has": [
    {
      "type": "host",
      "value": "music.mattmurphy.ca"
    }
  ],
  "destination": "https://music-cross-linker.vercel.app/:path*",
  "permanent": true
}

Or in next.config.js:
async redirects() {
  return [
    {
      source: '/:path*',
      has: [
        {
          type: 'host',
          value: 'music.mattmurphy.ca',
        },
      ],
      destination: 'https://music-cross-linker.vercel.app/:path*',
      permanent: true,
    },
  ]
}

Let's check target Vercel domain or URL for music cross linker project or if music.mattmurphy.ca should redirect to the music cross linker app deployment or domain.
Wait, edit /Users/matt/projects/mattmurphy.ca/vercel.json to include host matching redirect or general redirect. Let's update vercel.json in /Users/matt/projects/mattmurphy.ca/vercel.json.

File: /Users/matt/projects/mattmurphy.ca/vercel.json
Update vercel.json to:
{
	"crons": [
		{
			"path": "/api/cron/keep-alive",
			"schedule": "0 0 * * *"
		}
	],
	"redirects": [
		{
			"source": "/subtitles",
			"destination": "https://netflix-subtitle-display.vercel.app",
			"permanent": true
		},
		{
			"source": "/:path*",
			"has": [
				{
					"type": "host",
					"value": "music.mattmurphy.ca"
				}
			],
			"destination": "https://music-cross-linker.vercel.app/:path*",
			"permanent": true
		}
	]
}
Also check next.config.js and add `redirects` method as fallback or complementary redirect rule:
async redirects() {
  return [
    {
      source: '/:path*',
      has: [
        {
          type: 'host',
          value: 'music.mattmurphy.ca',
        },
      ],
      destination: 'https://music-cross-linker.vercel.app/:path*',
      permanent: true,
    },
    {
      source: '/music',
      destination: 'https://music-cross-linker.vercel.app',
      permanent: true,
    },
    {
      source: '/music/:path*',
      destination: 'https://music-cross-linker.vercel.app/:path*',
      permanent: true,
    }
  ]
}
Perform the file edits for /Users/matt/projects/mattmurphy.ca/vercel.json and /Users/matt/projects/mattmurphy.ca/next.config.js.

---

## Assistant

The requested changes have been applied to the project configuration files.

- **[`vercel.json`](file:///Users/matt/projects/mattmurphy.ca/vercel.json)**: Added a redirect rule matching the host `music.mattmurphy.ca` to `https://music-cross-linker.vercel.app/:path*`.
- **[`next.config.js`](file:///Users/matt/projects/mattmurphy.ca/next.config.js)**: Added an `async redirects()` method containing rules for:
    - Host-based redirection for `music.mattmurphy.ca`.
    - Path-based redirection for `/music` and `/music/:path*`.

---
