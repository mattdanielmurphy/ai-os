const customStringify = (obj, indent = '') => {
    if (obj === null) return 'null';
    if (typeof obj === 'string') {
        if (obj.includes('\n') || obj.includes('"')) {
            return `\`\n${obj}\n${indent}\``;
        }
        return `"${obj}"`;
    }
    if (typeof obj === 'number' || typeof obj === 'boolean') {
        return String(obj);
    }
    if (Array.isArray(obj)) {
        if (obj.length === 0) return '[]';
        let res = '[\n';
        const nextIndent = indent + '  ';
        for (let i = 0; i < obj.length; i++) {
            res += nextIndent + customStringify(obj[i], nextIndent) + (i < obj.length - 1 ? ',' : '') + '\n';
        }
        res += indent + ']';
        return res;
    }
    if (typeof obj === 'object') {
        const keys = Object.keys(obj);
        if (keys.length === 0) return '{}';
        let res = '{\n';
        const nextIndent = indent + '  ';
        for (let i = 0; i < keys.length; i++) {
            const key = keys[i];
            res += nextIndent + `"${key}": ` + customStringify(obj[key], nextIndent) + (i < keys.length - 1 ? ',' : '') + '\n';
        }
        res += indent + '}';
        return res;
    }
    return String(obj);
};

const obj = {
    CodeContent: "## Goal\nFix the TUI live stream spinner bug where `\\r` and `\\b` escape characters were not properly processed, causing the loading string to duplicate in the display. Also fix the appearance of `(B` character set escape sequences.\n\n## Changes Made\n- Modified `src/main.ts` line 1194 to fix the `\\r` and `\\b` escape characters.",
    Description: "Add log for TUI spinner fix",
    Overwrite: false,
    TargetFile: "/Users/matthewmurphy/projects/ai-os/.agent-logs/2026-07-04_16-29-tui-live-stream-spinner-fix-2.md",
    toolAction: "Writing agent log",
    toolSummary: "Write agent log"
};

console.log(customStringify(obj));
