async function syncGeminiThreads() {
    try {
        // Logic to extract thread from Gemini DOM/API
        // ... (assumed extraction logic)
        const payload = {
            provider: 'gemini',
            thread_id: 'test-thread-1',
            title: 'Test Thread',
            updated_at: Date.now(),
            messages: [{ role: 'user', content: 'hello' }]
        };
        await fetch('http://127.0.0.1:19223/api/cloud-sync/ingest', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
    } catch (e) {
        console.error('Gemini Sync Failed:', e);
    }
}
syncGeminiThreads();
