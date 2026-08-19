---
title: "Refactor TrustedHTML Security Fix"
date: "2026-08-14"
conversation_id: "8f1b7e8c-94e1-4423-abb2-b26fb9016dab"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; position: absolute; top: 0; left: 0; right: 0; bottom: 0; padding: 4rem 1.5rem; scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 13, 2026</span>

<span style="display: block; width: 100%; margin-top: 8px;">

<span title="Sent at " style="display: table; margin-left: auto; max-width: 75%; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

Please update `userscripts/gemini-enhancements/05-prompt-tools.js` to fix the TrustedHTML assignment error in `injectImmersiveModalButton`.

Specifically, replace the `btn.innerHTML = ...` assignments in `injectImmersiveModalButton` with DOM/SVG creation helpers using `document.createElementNS("http://www.w3.org/2000/svg", ...)` and `btn.replaceChildren(...)`.

Target file: `/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js`

Current code around line 1331:
```javascript

function injectImmersiveModalButton() {
	const panel = document.querySelector('immersive-panel')
	if (!panel) return
	
	const toolbar = panel.querySelector('toolbar')
	if (!toolbar) return

	if (toolbar.querySelector('.ai-os-expand-btn')) return

	const btn = document.createElement('button')
	btn.className = 'ai-os-expand-btn'
	btn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/></svg>`
	btn.style.cssText = "background: transparent; border: none; color: inherit; cursor: pointer; padding: 4px; border-radius: 4px; display: flex; align-items: center; justify-content: center; opacity: 0.7;"
	btn.title = "Expand/Collapse Panel"

	btn.addEventListener('mouseenter', () => btn.style.opacity = "1")
	btn.addEventListener('mouseleave', () => btn.style.opacity = "0.7")

	let clickOutsideHandler = null

	btn.addEventListener('click', (e) => {
		e.stopPropagation()
		if (panel.classList.contains('ai-os-immersive-modal')) {
			exitModal()
		} else {
			enterModal()
		}
	})

	function enterModal() {
		panel.classList.add('ai-os-immersive-modal')
		btn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 14h6v6M20 10h-6V4M14 10l7-7M3 21l7-7"/></svg>`
		
		// Setup cl
<truncated 1008 bytes>
cument.createElementNS("http://www.w3.org/2000/svg", "svg")
		svg.setAttribute("width", "18")
		svg.setAttribute("height", "18")
		svg.setAttribute("viewBox", "0 0 24 24")
		svg.setAttribute("fill", "none")
		svg.setAttribute("stroke", "currentColor")
		svg.setAttribute("stroke-width", "2")
		svg.setAttribute("stroke-linecap", "round")
		svg.setAttribute("stroke-linejoin", "round")
		const path = document.createElementNS("http://www.w3.org/2000/svg", "path")
		path.setAttribute("d", pathD)
		svg.appendChild(path)
		return svg
	}

	const btn = document.createElement('button')
	btn.className = 'ai-os-expand-btn'
	btn.appendChild(createSvg("M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"))
	btn.style.cssText = "background: transparent; border: none; color: inherit; cursor: pointer; padding: 4px; border-radius: 4px; display: flex; align-items: center; justify-content: center; opacity: 0.7;"
	btn.title = "Expand/Collapse Panel"

	btn.addEventListener('mouseenter', () => btn.style.opacity = "1")
	btn.addEventListener('mouseleave', () => btn.style.opacity = "0.7")

	let clickOutsideHandler = null

	btn.addEventListener('click', (e) => {
		e.stopPropagation()
		if (panel.classList.contains('ai-os-immersive-modal')) {
			exitModal()
		} else {
			enterModal()
		}
	})

	function enterModal() {
		panel.classList.add('ai-os-immersive-modal')
		btn.replaceChildren(createSvg("M4 14h6v6M20 10h-6V4M14 10l7-7M3 21l7-7"))
		
		// Setup click outside
		clickOutsideHandler = (event) => {
			if (!panel.contains(event.target)) {
				exitModal()
			}
		}
		document.addEventListener('click', clickOutsideHandler, true)
	}

	function exitModal() {
		panel.classList.remove('ai-os-immersive-modal')
		btn.replaceChildren(createSvg("M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"))
		if (clickOutsideHandler) {
			document.removeEventListener('click', clickOutsideHandler, true)
			clickOutsideHandler = null
		}
	}

	toolbar.appendChild(btn)
}
```

</span>



<span title="Responded at 2:28am" style="display: table; margin-right: auto; max-width: 85%; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 14px 18px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

The update to `injectImmersiveModalButton` in [`05-prompt-tools.js`](file:///Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js) [✏️](http://127.0.0.1:8643/open_zed?path=/Users/matt/projects/userscript-bundler/userscripts/gemini-enhancements/05-prompt-tools.js) is complete. The function now uses a helper to construct SVG elements programmatically, avoiding the TrustedHTML assignment error.

</span>



</span>

</span>