import re
import os
import urllib.parse

def enrich_file_links(text: str) -> str:
    """
    Enriches file links into clean, minimalist links with an optional Zed icon link:
      [label](file:///path/to/file.ext#L10) [⚡](http://127.0.0.1:8643/open_zed?path=/path/to/file.ext:10)

    - Primary link: Standard [label](file:///path/to/file.ext) which opens in Antigravity.
    - Zed action: A tiny ⚡ link pointing to http://127.0.0.1:8643/open_zed?path=...
      intercepted by AIOSURLRouter.app & url_action_listener.
    """
    pattern = r'\[([^\]]+)\]\((file:///[^\s\)]+)\)'

    def replacer(match):
        full_match = match.group(0)
        label = match.group(1)
        url = match.group(2)

        # Idempotency: skip if already appended with ⚡ link
        end_pos = match.end()
        remainder = text[end_pos:end_pos + 60]
        if remainder.startswith(' [⚡]') or 'open_zed' in remainder:
            return full_match

        clean_url = url
        line_start = None
        line_end = None

        if '#' in url:
            clean_url, fragment = url.split('#', 1)
            m_line = re.search(r'L(\d+)(?:-L?(\d+))?', fragment)
            if m_line:
                line_start = m_line.group(1)
                line_end = m_line.group(2)

        system_path = clean_url[7:] if clean_url.startswith('file://') else clean_url

        zed_line_suffix = ''
        if line_start:
            zed_line_suffix = f':{line_start}'
            if line_end:
                zed_line_suffix = f':{line_start}:{line_end}'

        full_zed_path = f'{system_path}{zed_line_suffix}'
        encoded_path = urllib.parse.quote(full_zed_path)
        router_zed_url = f'http://127.0.0.1:8643/open_zed?path={encoded_path}'

        return f'[{label}]({url}) [⚡]({router_zed_url})'

    return re.sub(pattern, replacer, text)
