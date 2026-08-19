---
title: "Update Caddyfile Reverse Proxy"
date: "2026-08-13"
conversation_id: "1417c991-b071-4b58-9c0b-9e37de9209c7"
source: "antigravity"
---

# Update Caddyfile Reverse Proxy

## User

Please update `/Users/matt/projects/ai-os/Caddyfile` to expose `https://localhost:8082` (or `https://127.0.0.1:8082`) using `tls internal` and proxy to the LLM server on port 8000 (or LiteLLM proxy port).

Content of `/Users/matt/projects/ai-os/Caddyfile`:

```caddyfile
# Caddyfile for LLM Server HTTPS Reverse Proxy

# Expose HTTPS on localhost:8082
https://localhost:8082 {
    tls internal
    reverse_proxy 127.0.0.1:8000 {
        flush_interval -1
        transport http {
            read_timeout 300s
            write_timeout 300s
        }
        header_up Host {host}
        header_up X-Real-IP {remote_host}
        header_up X-Forwarded-For {remote_host}
        header_up X-Forwarded-Proto {scheme}
    }
}
```

Use `write_to_file` with `Overwrite: true` to update `/Users/matt/projects/ai-os/Caddyfile`.

---

## Assistant

The `Caddyfile` has been updated as requested.

---
