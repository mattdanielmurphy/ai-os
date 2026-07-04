import { invoke } from '@tauri-apps/api/tauri'
import { getRelativeDateStr, getFullDateStr } from '../dateUtils'
// @ts-ignore
import styles from './ActionBar.module.css'

interface ThreadLog {
    id: string;
    latest_leaf_id: string;
    title: string;
    snippet: string;
    filepath?: string;
    mtime: number;
}

interface ThreadSearchResult {
    thread: ThreadLog;
    score: number;
    preview: string;
}

export class ActionBar {
    private overlay: HTMLDivElement;
    private input: HTMLInputElement;
    private resultsContainer: HTMLDivElement;
    private activeProjectCallback: () => string | null;
    private onSelectThread: (thread: ThreadLog) => void;
    private selectedIndex: number = -1;
    private currentResults: ThreadSearchResult[] = [];

    constructor(
        activeProjectCallback: () => string | null,
        onSelectThread: (thread: ThreadLog) => void
    ) {
        this.activeProjectCallback = activeProjectCallback;
        this.onSelectThread = onSelectThread;

        this.overlay = document.createElement('div');
        this.overlay.className = styles.actionBarOverlay;
        this.overlay.dataset.ui = 'action-bar';

        const container = document.createElement('div');
        container.className = styles.actionBarContainer;

        this.input = document.createElement('input');
        this.input.className = styles.actionBarInput;
        this.input.placeholder = 'Search active threads...';
        
        this.resultsContainer = document.createElement('div');
        this.resultsContainer.className = styles.actionBarResults;

        container.appendChild(this.input);
        container.appendChild(this.resultsContainer);
        this.overlay.appendChild(container);
        document.body.appendChild(this.overlay);

        this.setupListeners();
    }

    private setupListeners() {
        document.addEventListener('keydown', (e) => {
            if (e.key === 'k' && e.metaKey) {
                e.preventDefault();
                this.toggle();
            }
        });

        this.overlay.addEventListener('mousedown', (e) => {
            if (e.target === this.overlay) {
                this.close();
            }
        });

        let debounceTimeout: any = null;
        this.input.addEventListener('input', () => {
            clearTimeout(debounceTimeout);
            debounceTimeout = setTimeout(() => this.performSearch(), 300);
        });

        this.input.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                this.setSelectedIndex((this.selectedIndex + 1) % this.currentResults.length);
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                this.setSelectedIndex(this.selectedIndex <= 0 ? this.currentResults.length - 1 : this.selectedIndex - 1);
            } else if (e.key === 'Enter') {
                e.preventDefault();
                if (this.selectedIndex >= 0 && this.selectedIndex < this.currentResults.length) {
                    this.onSelectThread(this.currentResults[this.selectedIndex].thread);
                    this.close();
                }
            } else if (e.key === 'Escape') {
                e.preventDefault();
                this.close();
            }
        });
    }

    private setSelectedIndex(index: number) {
        if (this.currentResults.length === 0) return;
        this.selectedIndex = index;
        const children = this.resultsContainer.children;
        for (let i = 0; i < children.length; i++) {
            if (i === index) {
                children[i].classList.add(styles.selected);
                (children[i] as HTMLElement).scrollIntoView({ block: 'nearest' });
            } else {
                children[i].classList.remove(styles.selected);
            }
        }
    }

    private async performSearch() {
        const query = this.input.value.trim();
        const projectPath = this.activeProjectCallback();
        
        if (!query || !projectPath) {
            this.currentResults = [];
            this.renderResults();
            return;
        }

        try {
            const results = await invoke<ThreadSearchResult[]>('search_project_threads', {
                projectPath,
                query
            });
            this.currentResults = results;
            this.selectedIndex = results.length > 0 ? 0 : -1;
            this.renderResults();
        } catch (err) {
            console.error('Search failed:', err);
            this.resultsContainer.innerHTML = `<div class="${styles.emptyState}">Error performing search</div>`;
        }
    }

    private renderResults() {
        this.resultsContainer.innerHTML = '';
        if (this.currentResults.length === 0 && this.input.value.trim()) {
            this.resultsContainer.innerHTML = `<div class="${styles.emptyState}">No results found</div>`;
            return;
        }

        this.currentResults.forEach((result, index) => {
            const el = document.createElement('div');
            el.className = styles.actionBarResultItem;
            if (index === this.selectedIndex) {
                el.classList.add(styles.selected);
            }
            
            const headerEl = document.createElement('div');
            headerEl.className = styles.actionBarResultHeader;

            const titleEl = document.createElement('div');
            titleEl.className = styles.actionBarResultTitle;
            titleEl.textContent = result.thread.title || result.thread.id;

            const dateEl = document.createElement('div');
            dateEl.className = styles.actionBarResultDate;
            const ts = result.thread.mtime > 0 ? result.thread.mtime * 1000 : Date.now();
            dateEl.textContent = getRelativeDateStr(ts);
            dateEl.title = getFullDateStr(ts);

            headerEl.appendChild(titleEl);
            headerEl.appendChild(dateEl);
            
            const previewEl = document.createElement('div');
            previewEl.className = styles.actionBarResultPreview;
            previewEl.textContent = result.preview;

            el.appendChild(headerEl);
            el.appendChild(previewEl);

            el.addEventListener('click', () => {
                this.onSelectThread(result.thread);
                this.close();
            });

            this.resultsContainer.appendChild(el);
        });
    }

    public toggle() {
        if (this.overlay.classList.contains(styles.active)) {
            this.close();
        } else {
            this.open();
        }
    }

    public open() {
        this.overlay.classList.add(styles.active);
        this.input.focus();
        this.input.select();
        this.performSearch();
    }

    public close() {
        this.overlay.classList.remove(styles.active);
    }
}
