# Bridge Output Reliability

- Reproduced the production symptom: the direct `agy` CLI returned its smoke reply while `agy-bridge` returned `success: true` and an empty assistant payload.
- Added tests for the CLI default, argv propagation, and empty-response failure handling. `uv run pytest -q` passed all 563 tests.
