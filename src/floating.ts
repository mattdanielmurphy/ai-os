import './styles.scss';
import { invoke, appWindow } from './tauriWrapper';

let attachedContext: any = null;

document.addEventListener('DOMContentLoaded', () => {
    const attachBtn = document.getElementById('attach-btn') as HTMLButtonElement | null;
    const promptInput = document.getElementById('prompt-input') as HTMLInputElement | null;
    const contextBadge = document.getElementById('context-badge') as HTMLDivElement | null;

    if (attachBtn && contextBadge) {
        attachBtn.addEventListener('click', async () => {
            try {
                // Call the Tauri command to get the active browser context
                const result = await invoke('get_browser_context');
                attachedContext = result;
                
                // Show badge
                contextBadge.classList.remove('hidden');
                contextBadge.classList.add('flex');
            } catch (e) {
                console.error("Failed to attach browser context:", e);
                // The backend returns an error string if it fails
                alert("Failed to attach browser context: " + String(e));
            }
        });
    }

    if (promptInput) {
        promptInput.addEventListener('keydown', async (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                const prompt = promptInput.value.trim();
                if (!prompt && !attachedContext) return;
                
                try {
                    // Dispatch the command with the prompt and context
                    await invoke('dispatch_to_gemini', {
                        prompt,
                        context: attachedContext
                    });
                    
                    // Reset UI
                    promptInput.value = '';
                    attachedContext = null;
                    if (contextBadge) {
                        contextBadge.classList.add('hidden');
                        contextBadge.classList.remove('flex');
                    }
                    
                    // Hide the window
                    await appWindow.hide();
                } catch(err) {
                    console.error("Failed to dispatch to Gemini:", err);
                    alert("Dispatch failed: " + String(err));
                }
            }
        });
    }
});
