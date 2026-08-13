export function renderFileView(filename: string, content: string): string {
  const safeContent = content
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>${filename}</title>
  <style>
    body { font-family: monospace; padding: 20px; background: #0f172a; color: #f8fafc; }
    pre { white-space: pre-wrap; word-break: break-all; }
  </style>
</head>
<body>
  <h2>File: ${filename}</h2>
  <hr/>
  <pre><code>${safeContent}</code></pre>
</body>
</html>`;
}

export function renderDirectoryView(dirName: string, items: { name: string; isDir: boolean; path: string; size?: number }[], token: string): string {
  const rows = items.map(item => {
    const href = `${item.path}?token=${token}`;
    const icon = item.isDir ? "📁" : "📄";
    const sizeStr = item.size !== undefined ? ` (${item.size} bytes)` : "";
    return `<li>${icon} <a href="${href}">${item.name}</a>${sizeStr}</li>`;
  }).join("\n");

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Directory: ${dirName}</title>
  <style>
    body { font-family: sans-serif; padding: 20px; background: #0f172a; color: #f8fafc; }
    a { color: #38bdf8; text-decoration: none; }
    a:hover { text-decoration: underline; }
    ul { list-style: none; padding-left: 0; }
    li { margin: 8px 0; font-family: monospace; }
  </style>
</head>
<body>
  <h2>Directory: ${dirName}</h2>
  <p><a href="/manifest?token=${token}">View Full Codebase Manifest</a></p>
  <hr/>
  <ul>
    ${rows}
  </ul>
</body>
</html>`;
}

export function renderManifestView(files: { path: string; size: number }[], token: string): string {
  const rows = files.map(file => {
    const href = `/${file.path}?token=${token}`;
    return `<li>📄 <a href="${href}">${file.path}</a> (${file.size} bytes)</li>`;
  }).join("\n");

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Codebase Manifest</title>
  <style>
    body { font-family: sans-serif; padding: 20px; background: #0f172a; color: #f8fafc; }
    a { color: #38bdf8; text-decoration: none; }
    a:hover { text-decoration: underline; }
    ul { list-style: none; padding-left: 0; }
    li { margin: 6px 0; font-family: monospace; }
  </style>
</head>
<body>
  <h2>Codebase Manifest (${files.length} files)</h2>
  <hr/>
  <ul>
    ${rows}
  </ul>
</body>
</html>`;
}
