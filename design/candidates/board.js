// Builds the swatch board page from candidates.json.
import { readFileSync, writeFileSync } from 'fs';
const d = JSON.parse(readFileSync(new URL('./candidates.json', import.meta.url)));
const s = d.light.scales.stone, sd = d.dark.scales.stone;
const html = readFileSync(new URL('./board.template.html', import.meta.url), 'utf8')
  .replace('/*DATA*/', 'const D=' + JSON.stringify(d) + ';')
  .replace('/*TOKENS*/', `:root{--bg:${d.light.background};--fg:${s[11]};--muted:${s[10]};--line:${s[5]};--panel:${s[1]}}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:${d.dark.background};--fg:${sd[11]};--muted:${sd[10]};--line:${sd[5]};--panel:${sd[1]};color-scheme:dark}}
:root[data-theme="dark"]{--bg:${d.dark.background};--fg:${sd[11]};--muted:${sd[10]};--line:${sd[5]};--panel:${sd[1]};color-scheme:dark}`);
writeFileSync(process.argv[2], html);
console.log('wrote', process.argv[2], html.length);
