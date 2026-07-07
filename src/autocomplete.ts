import { readDir } from '@tauri-apps/api/fs';

interface Suggestion {
    text: string;
    description?: string;
    isCommand?: boolean;
}

const COMMANDS: Suggestion[] = [
    { text: '/model', description: 'Change the AI model', isCommand: true },
    { text: '/clear', description: 'Clear the context', isCommand: true },
    { text: '/goal', description: 'Set a long-running goal', isCommand: true },
    { text: '/schedule', description: 'Schedule a recurring task', isCommand: true },
    { text: '/grill-me', description: 'Interactive interview for design decisions', isCommand: true },
];

export class Autocompleter {
    private textarea: HTMLTextAreaElement;
    private popup: HTMLDivElement;
    private selectedIndex: number = 0;
    private suggestions: Suggestion[] = [];
    
    private isActive: boolean = false;
    private getCwd: () => string;
    private cursorOffsetStart: number = 0;

    constructor(textarea: HTMLTextAreaElement, getCwd: () => string) {
        this.textarea = textarea;
        this.getCwd = getCwd;
        
        this.popup = document.createElement('div');
        this.popup.className = 'autocomplete-popup';
        this.popup.style.display = 'none';
        
        // Append to the wrapper so it can be positioned absolutely above textarea
        const parent = this.textarea.parentElement;
        if (parent) {
            parent.style.position = 'relative';
            parent.appendChild(this.popup);
        }

        this.attachListeners();
    }

    private attachListeners() {
        this.textarea.addEventListener('input', this.onInput.bind(this));
        this.textarea.addEventListener('keydown', this.onKeyDown.bind(this), { capture: true });
        this.textarea.addEventListener('blur', () => {
            setTimeout(() => this.hide(), 150);
        });
    }

    private async onInput() {
        const val = this.textarea.value;
        const cursorPos = this.textarea.selectionStart;
        
        // Find the word being typed
        const beforeCursor = val.substring(0, cursorPos);
        const match = beforeCursor.match(/(?:^|\s)(\/[^\s]*)$/);
        const pathMatch = beforeCursor.match(/(?:^|\s)([\.~]?\/[^\s]*)$/);
        
        let query = '';
        let isPath = false;
        
        if (match) {
            query = match[1];
            this.cursorOffsetStart = cursorPos - query.length;
        } else if (pathMatch) {
            query = pathMatch[1];
            isPath = true;
            this.cursorOffsetStart = cursorPos - query.length;
        } else {
            this.hide();
            return;
        }
        
        
        this.suggestions = [];

        if (!isPath || query.startsWith('/')) {
            // Check commands
            const cmdMatches = COMMANDS.filter(cmd => cmd.text.startsWith(query));
            this.suggestions.push(...cmdMatches);
        }

        // Try path completion
        if (query.includes('/') && !this.suggestions.find(s => s.isCommand && s.text === query)) {
             try {
                 const pathSuggestions = await this.getPathSuggestions(query);
                 this.suggestions.push(...pathSuggestions);
             } catch(err) {
                 // ignore fs errors
             }
        }

        if (this.suggestions.length > 0) {
            this.show();
        } else {
            this.hide();
        }
    }

    private async getPathSuggestions(query: string): Promise<Suggestion[]> {
        const lastSlash = query.lastIndexOf('/');
        let dirPath = query.substring(0, lastSlash);
        const prefix = query.substring(lastSlash + 1);
        
        if (dirPath === '') dirPath = '/';
        
        // Resolve relative
        let targetDir = dirPath;
        if (targetDir.startsWith('./')) {
            targetDir = this.getCwd() + targetDir.substring(1);
        } else if (targetDir === '.') {
            targetDir = this.getCwd();
        } else if (targetDir.startsWith('~/')) {
             targetDir = '/Users/matt' + targetDir.substring(1);
        }
        
        try {
            const entries = await readDir(targetDir);
            const matches = entries.filter(e => e.name && e.name.startsWith(prefix));
            return matches.map(e => {
                const isDir = e.children !== undefined || e.name?.indexOf('.') === -1; // rough heuristic if metadata not loaded
                const fullPath = dirPath === '/' ? `/${e.name}` : `${dirPath}/${e.name}`;
                return { text: fullPath, description: isDir ? 'Directory' : 'File' };
            });
        } catch(e) {
            return [];
        }
    }

    private onKeyDown(e: KeyboardEvent) {
        if (!this.isActive) return;

        if (e.key === 'ArrowDown') {
            e.preventDefault();
            e.stopPropagation();
            this.selectedIndex = (this.selectedIndex + 1) % this.suggestions.length;
            this.render();
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            e.stopPropagation();
            this.selectedIndex = (this.selectedIndex - 1 + this.suggestions.length) % this.suggestions.length;
            this.render();
        } else if (e.key === 'Enter' || e.key === 'Tab') {
            e.preventDefault();
            e.stopPropagation();
            this.selectCurrent();
        } else if (e.key === 'Escape') {
            e.preventDefault();
            this.hide();
        }
    }

    private selectCurrent() {
        if (!this.isActive || this.suggestions.length === 0) return;
        const selected = this.suggestions[this.selectedIndex];
        
        const val = this.textarea.value;
        const before = val.substring(0, this.cursorOffsetStart);
        const after = val.substring(this.textarea.selectionStart);
        
        this.textarea.value = before + selected.text + ' ' + after;
        const newCursorPos = before.length + selected.text.length + 1;
        this.textarea.selectionStart = newCursorPos;
        this.textarea.selectionEnd = newCursorPos;
        
        this.hide();
        // Trigger input event to resize textarea
        this.textarea.dispatchEvent(new Event('input'));
    }

    private show() {
        this.isActive = true;
        this.selectedIndex = 0;
        this.render();
        this.popup.style.display = 'block';
    }

    private hide() {
        this.isActive = false;
        this.popup.style.display = 'none';
    }

    private render() {
        this.popup.innerHTML = '';
        this.suggestions.forEach((s, idx) => {
            const item = document.createElement('div');
            item.className = 'autocomplete-item' + (idx === this.selectedIndex ? ' selected' : '');
            
            const textSpan = document.createElement('span');
            textSpan.className = 'autocomplete-text';
            textSpan.textContent = s.text;
            
            const descSpan = document.createElement('span');
            descSpan.className = 'autocomplete-desc';
            descSpan.textContent = s.description || '';
            
            item.appendChild(textSpan);
            item.appendChild(descSpan);
            
            item.onmousedown = (e) => {
                e.preventDefault(); // prevent blur
                this.selectedIndex = idx;
                this.selectCurrent();
            };
            
            this.popup.appendChild(item);
        });
    }
}
