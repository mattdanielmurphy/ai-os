// Injected script for Gemini WebView
(function() {
    console.log("Gemini Bridge Active");

    // Detect ```bridge-action ... ```
    const observer = new MutationObserver(() => {
        const responseBlocks = document.querySelectorAll('pre');
        responseBlocks.forEach(block => {
            if (block.textContent.includes('```bridge-action')) {
                // Logic to extract action and send to http://127.0.0.1:19223/api/bridge/execute
            }
        });
    });
    observer.observe(document.body, { childList: true, subtree: true });

    // Handle /local or @local prompt prefixes
    const inputField = document.querySelector('textarea');
    if (inputField) {
        inputField.addEventListener('keydown', async (e) => {
            if (e.key === 'Enter' && (inputField.value.startsWith('/local') || inputField.value.startsWith('@local'))) {
                e.preventDefault();
                const response = await fetch('http://127.0.0.1:19223/api/bridge/context');
                const context = await response.text();
                inputField.value = context + "\n\n" + inputField.value;
                // Dispatch event to send message
            }
        });
    }
})();
