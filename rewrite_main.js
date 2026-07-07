const fs = require('fs');
let code = fs.readFileSync('/Users/matt/projects/ai-os/src/main.ts', 'utf8');

// Replace targetPath quote stripping
code = code.replace(
    /let targetPath = ''\s+if \(call\.args\) \{[\s\S]*?else if \(typeof call\.args\.SearchPath === 'string'\) targetPath = call\.args\.SearchPath\s*\}/,
    `let targetPath = ''
                    if (call.args) {
                        if (typeof call.args.TargetFile === 'string') targetPath = call.args.TargetFile
                        else if (typeof call.args.AbsolutePath === 'string') targetPath = call.args.AbsolutePath
                        else if (typeof call.args.DirectoryPath === 'string') targetPath = call.args.DirectoryPath
                        else if (typeof call.args.SearchPath === 'string') targetPath = call.args.SearchPath
                    }
                    if (targetPath.startsWith('"') && targetPath.endsWith('"')) {
                        targetPath = targetPath.slice(1, -1)
                    } else if (targetPath.startsWith("'") && targetPath.endsWith("'")) {
                        targetPath = targetPath.slice(1, -1)
                    }`
);

// Fix wrapping in `marked.Renderer`
code = code.replace(
    /<pre style="margin:0;"><code class="language-\$\{lang\}">\$\{escapedText\}<\/code><\/pre>/g,
    '<pre style="margin:0; white-space: pre-wrap; word-wrap: break-word;"><code class="language-${lang}">${escapedText}</code></pre>'
);

// Fix padding, max-height, and width in argsListHtml rendering
code = code.replace(
    /const parsedHtml = marked\.parse\(mdString\) as string;\s*argsListHtml \+= `<tr><td style="vertical-align: top; padding: 4px 8px 4px 0; font-weight: 600; color: var\(--text-muted\); width: 160px; word-break: break-word;">\$\{key\}<\/td><td style="padding: 4px 0;"><div class="prose prose-sm prose-headings:text-gray-950 prose-pre:bg-transparent prose-pre:border-0 compact-prose" style="width: 100%; box-sizing: border-box; max-height: 400px; overflow-y: auto;">\$\{parsedHtml\}<\/div><\/td><\/tr>`/,
    `const parsedHtml = marked.parse(mdString) as string;
                            argsListHtml += \`<tr><td style="vertical-align: top; padding: 4px 8px 4px 0; font-weight: 600; color: var(--text-muted); width: 160px; word-break: break-word;">\${key}</td><td style="padding: 4px 0;"><div class="prose prose-sm prose-headings:text-gray-950 prose-pre:bg-transparent prose-pre:border-0 compact-prose" style="width: 100%; box-sizing: border-box;">\${parsedHtml}</div></td></tr>\``
);

code = code.replace(
    /\} else if \(typeof displayValue === 'string'\) \{\s*argsListHtml \+= `<tr><td style="vertical-align: top; padding: 4px 8px 4px 0; font-weight: 600; color: var\(--text-muted\); width: 160px; word-break: break-word;">\$\{key\}<\/td><td style="padding: 4px 0; word-break: break-word;"><span style="color: var\(--text-muted\);">\$\{displayValue\.replace\(\/&\/g, '&amp;'\)\.replace\(\/<\/g, '&lt;'\)\.replace\(\/>\/g, '&gt;'\)\}<\/span><\/td><\/tr>`\s*\} else \{\s*argsListHtml \+= `<tr><td style="vertical-align: top; padding: 4px 8px 4px 0; font-weight: 600; color: var\(--text-muted\); width: 160px; word-break: break-word;">\$\{key\}<\/td><td style="padding: 4px 0; word-break: break-word;"><pre style="display:inline-block; margin:0; padding:4px 8px; font-size:0.8em; background: rgba\(0,0,0,0\.05\); border-radius: 4px; max-height: 400px; overflow-y: auto;"><code>\$\{JSON\.stringify\(displayValue, null, 2\)\.replace\(\/&\/g, '&amp;'\)\.replace\(\/<\/g, '&lt;'\)\.replace\(\/>\/g, '&gt;'\)\}<\/code><\/pre><\/td><\/tr>`\s*\}/,
    `} else if (typeof displayValue === 'string') {
                            let strVal = displayValue;
                            if (strVal.startsWith('"') && strVal.endsWith('"')) strVal = strVal.slice(1, -1);
                            if (strVal.startsWith("'") && strVal.endsWith("'")) strVal = strVal.slice(1, -1);
                            argsListHtml += \`<tr><td style="vertical-align: top; padding: 4px 8px 4px 0; font-weight: 600; color: var(--text-muted); width: 160px; word-break: break-word;">\${key}</td><td style="padding: 4px 0; word-break: break-word;"><span style="color: var(--text-muted);">\${strVal.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')}</span></td></tr>\`
                        } else {
                            const jsonStr = JSON.stringify(displayValue, null, 2);
                            const parsedHtml = marked.parse(\`\\\`\\\`\\\`json\\n\${jsonStr}\\n\\\`\\\`\\\`\`) as string;
                            argsListHtml += \`<tr><td style="vertical-align: top; padding: 4px 8px 4px 0; font-weight: 600; color: var(--text-muted); width: 160px; word-break: break-word;">\${key}</td><td style="padding: 4px 0;"><div class="prose prose-sm prose-headings:text-gray-950 prose-pre:bg-transparent prose-pre:border-0 compact-prose" style="width: 100%; box-sizing: border-box;">\${parsedHtml}</div></td></tr>\`
                        }`
);

// Fix catch block max-height
code = code.replace(
    /argsHtml = `<div style="padding: 4px 10px; width: 100%; box-sizing: border-box;"><div class="prose prose-sm prose-headings:text-gray-950 prose-pre:bg-transparent prose-pre:border-0 compact-prose" style="width: 100%; box-sizing: border-box; max-height: 400px; overflow-y: auto;">\$\{parsedHtml\}<\/div><\/div>`/,
    'argsHtml = `<div style="padding: 4px 10px; width: 100%; box-sizing: border-box;"><div class="prose prose-sm prose-headings:text-gray-950 prose-pre:bg-transparent prose-pre:border-0 compact-prose" style="width: 100%; box-sizing: border-box;">${parsedHtml}</div></div>`'
);

fs.writeFileSync('/Users/matt/projects/ai-os/src/main.ts', code, 'utf8');
