import { invoke } from '@tauri-apps/api/tauri';

export interface TodoItem {
    text: string;
    completed: boolean;
    lineIndex: number;
}

export class ThreadNotesManager {
    static async getNotesContent(): Promise<string> {
        try {
            return await invoke<string>('read_thread_notes_file');
        } catch (e) {
            console.error('Failed to read thread notes:', e);
            return '';
        }
    }

    static async saveNotesContent(content: string): Promise<void> {
        try {
            await invoke('write_thread_notes_file', { content });
        } catch (e) {
            console.error('Failed to write thread notes:', e);
        }
    }

    static async toggleTodo(lineIndex: number) {
        const content = await this.getNotesContent();
        const lines = content.split('\n');
        if (lineIndex >= 0 && lineIndex < lines.length) {
            const line = lines[lineIndex];
            if (line.includes('- [ ] ')) {
                lines[lineIndex] = line.replace('- [ ] ', '- [x] ');
            } else if (line.includes('- [x] ')) {
                lines[lineIndex] = line.replace('- [x] ', '- [ ] ');
            }
            await this.saveNotesContent(lines.join('\n'));
        }
    }

    static async ensureHeading(projectPath: string, threadId: string, threadName: string | null) {
        let content = await this.getNotesContent();
        let lines = content.split('\n');
        
        const projectName = projectPath.split('/').pop() || 'Unknown Project';
        const projectHeading = `# ${projectName}`;
        
        let projectIndex = lines.findIndex(l => l.trim() === projectHeading);
        if (projectIndex === -1) {
            lines.push('');
            lines.push(projectHeading);
            projectIndex = lines.length - 1;
        }

        const threadHeading = `## ${threadName ? threadName + ' (' + threadId + ')' : threadId}`;
        const justIdHeading = `## ${threadId}`;
        
        let threadIndex = lines.findIndex(l => l.trim() === threadHeading || l.trim() === justIdHeading || l.trim().includes(`(${threadId})`));
        if (threadIndex === -1) {
            lines.splice(projectIndex + 1, 0, threadHeading, '- [ ] ');
        }
        
        await this.saveNotesContent(lines.join('\n'));
    }

    static async getTodosForThread(threadId: string): Promise<TodoItem[]> {
        const content = await this.getNotesContent();
        const lines = content.split('\n');
        const todos: TodoItem[] = [];
        
        let inTargetThread = false;
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            
            if (line.startsWith('## ')) {
                if (line.includes(threadId)) {
                    inTargetThread = true;
                } else {
                    inTargetThread = false;
                }
            } else if (line.startsWith('# ')) {
                inTargetThread = false;
            }
            
            if (inTargetThread) {
                const matchUnchecked = line.match(/^(\s*)-\s*\[\s\]\s+(.*)/);
                const matchChecked = line.match(/^(\s*)-\s*\[x\]\s+(.*)/i);
                
                if (matchUnchecked) {
                    todos.push({ text: matchUnchecked[2], completed: false, lineIndex: i });
                } else if (matchChecked) {
                    todos.push({ text: matchChecked[2], completed: true, lineIndex: i });
                }
            }
        }
        
        return todos;
    }
}

export async function renderThreadNotesSidebar(projectPath: string | null, threadId: string | null) {
    const sidebar = document.getElementById('thread-notes-sidebar');
    const content = document.getElementById('thread-notes-content');
    if (!sidebar || !content) return;
    
    if (!projectPath || !threadId) {
        sidebar.style.display = 'none';
        return;
    }
    
    sidebar.style.display = 'flex';
    content.innerHTML = '<div style="color: var(--text-muted); font-style: italic;">Loading notes...</div>';
    
    const todos = await ThreadNotesManager.getTodosForThread(threadId);
    
    content.innerHTML = '';
    
    if (todos.length === 0) {
        const noTodos = document.createElement('div');
        noTodos.style.color = 'var(--text-muted)';
        noTodos.style.fontStyle = 'italic';
        noTodos.innerText = 'No todos found for this thread.';
        content.appendChild(noTodos);
        
        const initBtn = document.createElement('button');
        initBtn.className = 'btn-primary';
        initBtn.style.marginTop = '10px';
        initBtn.innerText = 'Initialize Thread Notes';
        initBtn.onclick = async () => {
            await ThreadNotesManager.ensureHeading(projectPath, threadId, null);
            renderThreadNotesSidebar(projectPath, threadId);
        };
        content.appendChild(initBtn);
        return;
    }
    
    const list = document.createElement('div');
    list.style.display = 'flex';
    list.style.flexDirection = 'column';
    list.style.gap = '8px';
    
    for (const todo of todos) {
        const row = document.createElement('label');
        row.style.display = 'flex';
        row.style.gap = '8px';
        row.style.alignItems = 'flex-start';
        row.style.cursor = 'pointer';
        
        const cb = document.createElement('input');
        cb.type = 'checkbox';
        cb.checked = todo.completed;
        cb.onchange = async () => {
            await ThreadNotesManager.toggleTodo(todo.lineIndex);
            await renderThreadNotesSidebar(projectPath, threadId);
        };
        
        const text = document.createElement('span');
        text.innerText = todo.text;
        if (todo.completed) {
            text.style.textDecoration = 'line-through';
            text.style.color = 'var(--text-muted)';
        }
        
        row.appendChild(cb);
        row.appendChild(text);
        list.appendChild(row);
    }
    
    content.appendChild(list);
}
