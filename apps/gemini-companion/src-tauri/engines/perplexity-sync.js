async function syncPerplexityThreads() {
    try {
        // Logic to extract thread from Perplexity session token
        // ... (assumed extraction logic)
        const payload = {
            provider: 'perplexity',
            thread_id: 'test-thread-2',
            title: 'Perplexity Thread',
            updated_at: Date.now(),
            messages: [{ role: 'user', content: 'hello' }]
        };
        await fetch('http://127.0.0.1:19223/api/cloud-sync/ingest', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
    } catch (e) {
        console.error('Perplexity Sync Failed:', e);
    }
}
syncPerplexityThreads();
