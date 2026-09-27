# AI-OS Distribution Policy

`agy-mcp` is maintained as a first-party component of the private AI-OS
monorepo at `tools/agy-mcp`.

It is not released from, contributed to, or configured to publish through
`Boulea7/agy-mcp`. The imported source keeps its MIT license and provenance in
[`UPSTREAM.md`](../UPSTREAM.md), but AI-OS changes belong in this repository.

## Supported installation

Install the checked-out monorepo copy as the live MCP bridge:

```bash
AI_OS_ROOT="$(git rev-parse --show-toplevel)"
uv tool install --force --editable "$AI_OS_ROOT/tools/agy-mcp"
```

The global `agymcp` registration runs that editable installation. It will pick
up committed AI-OS source changes without any PyPI release or upstream push.

## Future distribution

If a standalone package is ever needed, establish a separate AI-OS-owned
package identity, repository workflow, and publisher before enabling it. Do
not reuse the upstream repository's GitHub Actions, owner, or PyPI publisher.
