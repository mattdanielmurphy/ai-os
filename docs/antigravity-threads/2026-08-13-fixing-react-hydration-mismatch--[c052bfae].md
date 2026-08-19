---
title: "Fixing React Hydration Mismatch"
date: "2026-08-13"
conversation_id: "c052bfae-af9f-4a28-8417-18895e13adbd"
source: "antigravity"
---

# Fixing React Hydration Mismatch

## User

## Error Type
Console Error

## Error Message
A tree hydrated but some attributes of the server rendered HTML didn't match the client properties. This won't be patched up. This can happen if a SSR-ed Client Component used:

- A server/client branch `if (typeof window !== 'undefined')`.
- Variable input such as `Date.now()` or `Math.random()` which changes each time it's called.
- Date formatting in a user's locale which doesn't match the server.
- External changing data without sending a snapshot of it along with the HTML.
- Invalid HTML tag nesting.

It can also happen if the client has a browser extension installed which messes with the HTML before React loaded.

https://react.dev/link/hydration-mismatch

  ...
    <ScrollAndMaybeFocusHandler cacheNode={{rsc:{...}, ...}}>
      <InnerScrollAndFocusHandlerOld focusAndScrollRef={{scrollRef:null, ...}} cacheNode={{rsc:{...}, ...}}>
        <ErrorBoundary errorComponent={undefined} errorStyles={undefined} errorScripts={undefined}>
          <LoadingBoundary name="https%3A/w..." loading={null}>
            <HTTPAccessFallbackBoundary notFound={undefined} forbidden={undefined} unauthorized={undefined}>
              <RedirectBoundary>
                <RedirectErrorBoundary router={{...}}>
                  <InnerLayoutRouter url="/https:/ww..." tree={[...]} params={{url:[...]}} cacheNode={{rsc:{...}, ...}} ...>
                    <SegmentViewNode type="page" pagePath="[...url]/p...">
                      <SegmentTrieNode>
                      <Page>
                        <ResolvingRedirect lookupUrl="https://ww..." videoId="5r5ktX6ECDk">
                          <div className="main-content">
                            <div className="track-card">
                              <div className="player-wra...">
                                <iframe
                                  src="https://www.youtube.com/embed/5r5ktX6ECDk?autoplay=1"
                                  title="YouTube video player"
                                  frameBorder="0"
+                                 allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture..."
-                                 allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture..."
                                  allowFullScreen={true}
                                  style={{width:"100%",height:"100%",aspectRatio:"16/9"}}
-                                 webkitallowfullscreen="true"
-                                 mozallowfullscreen="true"
-                                 msallowfullscreen="true"
                                >
                              ...
                    ...
                  ...
        ...



    at iframe (<anonymous>:null:null)
    at ResolvingRedirect (app/components/ResolvingRedirect.tsx:64:13)
    at Page (app/[...url]/page.tsx:68:12)

## Code Frame
  62 |         <div className="player-wrapper">
  63 |           {videoId ? (
> 64 |             <iframe
     |             ^
  65 |               src={`https://www.youtube.com/embed/${videoId}?a...
  66 |               title="YouTube video player"
  67 |               frameBorder="0"

Next.js version: 16.2.12 (Turbopack)

---

## Assistant

### Summary of Work

#### Root Cause
The console hydration warning occurred because Next.js/React 19 SSR renders legacy vendor-prefixed iframe attributes (such as `webkitallowfullscreen`, `mozallowfullscreen`, `msallowfullscreen`) into the server HTML stream. During client-side hydration, React compares the server attributes with the client DOM property expectations, resulting in a hydration mismatch error on the YouTube player `<iframe>` inside `app/components/ResolvingRedirect.tsx`.

#### Fix Applied
1. **Updated [`ResolvingRedirect.tsx`](file:///Users/matt/projects/music-cross-linker/app/components/ResolvingRedirect.tsx#L64-L72)**: Added `suppressHydrationWarning={true}` to the YouTube `<iframe>` element (matching the pattern already used in [`YouTubeSection.tsx`](file:///Users/matt/projects/music-cross-linker/app/components/track-view/YouTubeSection.tsx#L32)).
2. **Build Verification**: Ran `bun run build` and verified that static page generation and TypeScript compilation completed with 0 errors.
3. **Pushed & Logged**: Auto-committed changes, updated [`DEVELOPMENT_JOURNAL.md`](file:///Users/matt/projects/music-cross-linker/DEVELOPMENT_JOURNAL.md), and generated work log [`agent-logs/2026-08-12_18-26_fix-resolving-redirect-hydration-mismatch.md`](file:///Users/matt/projects/music-cross-linker/agent-logs/2026-08-12_18-26_fix-resolving-redirect-hydration-mismatch.md).

For reference, you can review the thread log: .

---
