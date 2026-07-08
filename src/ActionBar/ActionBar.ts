// @ts-ignore
import styles from './ActionBar.module.css'

export interface CommandItem {
    name: string;
    description: string;
    action: () => void;
}

export class ActionBar {
    private overlay: HTMLDivElement;
    private input: HTMLInputElement;
    private resultsContainer: HTMLDivElement;
    private selectedIndex: number = -1;
    private commands: CommandItem[] = [];
    private currentResults: CommandItem[] = [];
    private previousFocus: HTMLElement | null = null;

    constructor() {
        this.overlay = document.createElement('div');
        this.overlay.className = styles.actionBarOverlay;
        this.overlay.dataset.ui = 'action-bar';

        const container = document.createElement('div');
        container.className = styles.actionBarContainer;

        this.input = document.createElement('input');
        this.input.className = styles.actionBarInput;
        this.input.placeholder = 'Search commands...';
        
        this.resultsContainer = document.createElement('div');
        this.resultsContainer.className = styles.actionBarResults;

        container.appendChild(this.input);
        container.appendChild(this.resultsContainer);
        this.overlay.appendChild(container);
        document.body.appendChild(this.overlay);

        this.setupListeners();
    }

    public setCommands(commands: CommandItem[]) {
        this.commands = commands;
        this.performSearch();
    }

    private setupListeners() {
        document.addEventListener('keydown', (e) => {
            if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
                e.preventDefault();
                e.stopPropagation();
                this.toggle();
            }
        }, true);

        this.overlay.addEventListener('mousedown', (e) => {
            if (e.target === this.overlay) {
                this.close();
            }
        });

        let debounceTimeout: any = null;
        this.input.addEventListener('input', () => {
            clearTimeout(debounceTimeout);
            debounceTimeout = setTimeout(() => this.performSearch(), 100);
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
                    const cmd = this.currentResults[this.selectedIndex];
                    this.close();
                    cmd.action();
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

    private performSearch() {
        const query = this.input.value.trim().toLowerCase();
        
        if (!query) {
            this.currentResults = [...this.commands];
        } else {
            this.currentResults = this.commands.filter(cmd => 
                cmd.name.toLowerCase().includes(query) || 
                cmd.description.toLowerCase().includes(query)
            );
        }

        this.selectedIndex = this.currentResults.length > 0 ? 0 : -1;
        this.renderResults();
    }

    private renderResults() {
        this.resultsContainer.innerHTML = '';
        if (this.currentResults.length === 0) {
            this.resultsContainer.innerHTML = `<div class="${styles.emptyState}">No commands found</div>`;
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
            titleEl.textContent = result.name;

            headerEl.appendChild(titleEl);
            
            const previewEl = document.createElement('div');
            previewEl.className = styles.actionBarResultPreview;
            previewEl.textContent = result.description;

            el.appendChild(headerEl);
            el.appendChild(previewEl);

            el.addEventListener('click', () => {
                this.close();
                result.action();
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
        this.previousFocus = document.activeElement as HTMLElement;
        this.overlay.classList.add(styles.active);
        
        // Reset query
        this.input.value = '';
        this.performSearch();

        // Focus immediately
        this.input.focus();
        this.input.select();
        
        // Focus again after visibility classes are applied to guarantee it sticks
        setTimeout(() => {
            this.input.focus();
            this.input.select();
        }, 50);
    }

    public close() {
        this.overlay.classList.remove(styles.active);
        if (this.previousFocus) {
            this.previousFocus.focus();
            this.previousFocus = null;
        }
    }
}
