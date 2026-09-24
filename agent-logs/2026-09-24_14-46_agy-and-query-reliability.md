# Agy and Query Reliability Repair

- Reproduced the agy bridge failure: `agy-bridge` returned exit code 0 with an empty assistant payload while the direct `agy` CLI returned the expected reply. The bridge now defaults to noninteractive permission approval and rejects an empty zero-exit response; the checked-out source suite passed 563 tests and the active bridge smoke test returned its expected output.
- Reworked pre-flight quota reporting to call `ag-quota --all -j` live-first, select each account's default model rather than preview buckets, and label cache fallback explicitly. Live verification reported two accounts and 97.5% on the active default model.
- Rebuilt and restarted `query-aios-companion`. The reachable companion was not authenticated to Perplexity; the debug probe now reports `AUTH=false` without revealing credentials, and pre-flight says sign-in is required rather than “connected”.
