import re
import os

def enrich_file_links(text: str) -> str:
    pattern = r'\[([^\]]+)\]\((file:///[^\s\)]+)\)'

    def replacer(match):
        full_match = match.group(0)
        label = match.group(1)
        url = match.group(2)

        end_pos = match.end()
        remainder = text[end_pos:end_pos + 60]
        if remainder.startswith(' (⚡ [Zed]') or remainder.startswith(' (🔍 [Finder]') or 'ai-os://reveal' in remainder:
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

        ext = os.path.splitext(system_path)[1].lower()
        is_markdown = ext in ['.md', '.markdown']

        zed_line_suffix = ''
        if line_start:
            zed_line_suffix = f':{line_start}'
            if line_end:
                zed_line_suffix = f':{line_start}:{line_end}'

        zed_link = f'zed://file{system_path}{zed_line_suffix}'
        finder_link = f'ai-os://reveal?path={system_path}'

        if is_markdown:
            return f'[{label}]({url}) (⚡ [Zed]({zed_link}) | 🔍 [Finder]({finder_link}))'
        else:
            return f'[{label}]({zed_link}) (🔍 [Finder]({finder_link}) | 📄 [View]({url}))'

    return re.sub(pattern, replacer, text)
