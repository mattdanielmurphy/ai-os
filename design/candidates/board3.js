// Builds board v3 from directions.json.
import { readFileSync, writeFileSync } from 'fs';
const d = readFileSync(new URL('./directions.json', import.meta.url), 'utf8');
const html = readFileSync(new URL('./board3.template.html', import.meta.url), 'utf8').replace('/*DATA*/', 'const D=' + d + ';');
writeFileSync(process.argv[2], html); console.log('wrote', html.length);
