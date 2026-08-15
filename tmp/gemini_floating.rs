    let floating_init_script = r#"
        (function() {
            function initIsolation() {
                const target = document.querySelector('.text-input-field') || document.querySelector('rich-textarea')?.parentElement?.parentElement || document.querySelector('form');
                if (!target) {
                    setTimeout(initIsolation, 500);
                    return;
                }

                // 1. Inject styles
                const styleEl = document.createElement('style');
                styleEl.id = 'ai-os-isolation-styles';
                styleEl.textContent = `
                    .ai-os-compressed * {
                        visibility: hidden !important;
                    }

                    .ai-os-compressed html, .ai-os-compressed body, .ai-os-compressed .isolated-path, .ai-os-compressed .isolated-target, .ai-os-compressed .isolated-target * {
                        visibility: visible !important;
                    }

                    .ai-os-compressed .isolated-target {
                        width: 100vw !important; 
                        height: 100vh !important;
                        position: fixed !important;
                        top: 0 !important;
                        left: 0 !important;
                        z-index: 2147483647 !important;
                        margin: 0 !important;
                        background: var(--md-sys-color-surface) !important;
                        display: flex !important; 
                        justify-content: center;
                        align-items: center;
                        border-radius: 12px;
                        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
                    }

                    .ai-os-compressed .isolated-path {
                        background: none !important;
                        border: none !important;
                        box-shadow: none !important;
                        transform: none !important;
                        overflow: visible !important;
                        opacity: 1 !important;
                    }

                    .ai-os-compressed html, .ai-os-compressed body {
                        background: transparent !important;
                        margin: 0 !important;
                        padding: 0 !important;
                    }
                    
                    #ai-os-toggle-mode {
                        position: fixed;
                        top: 10px;
                        right: 10px;
                        z-index: 2147483648;
                        background: #333;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 5px 10px;
                        cursor: pointer;
                    }
                `;
                document.head.appendChild(styleEl);

                // 2. Add classes to the target and its ancestors
                target.classList.add('isolated-target');
                let curr = target.parentElement;
                while (curr && curr !== document.documentElement) {
                    curr.classList.add('isolated-path');
                    curr = curr.parentElement;
                }
                
                // 3. Add a button to toggle modes
                const toggleBtn = document.createElement('button');
                toggleBtn.id = 'ai-os-toggle-mode';
                toggleBtn.textContent = 'Expand';
                toggleBtn.onclick = () => {
                    const isCompressed = document.body.classList.contains('ai-os-compressed');
                    if (isCompressed) {
                        document.body.classList.remove('ai-os-compressed');
                        toggleBtn.textContent = 'Compress';
                        if (window.__TAURI__) {
                            window.__TAURI__.window.appWindow.setSize(new window.__TAURI__.window.PhysicalSize(1000, 800));
                        }
                    } else {
                        document.body.classList.add('ai-os-compressed');
                        toggleBtn.textContent = 'Expand';
                        if (window.__TAURI__) {
                            window.__TAURI__.window.appWindow.setSize(new window.__TAURI__.window.PhysicalSize(660, 80));
                        }
                    }
                };
                document.body.appendChild(toggleBtn);

                // Enable compressed mode by default
                document.body.classList.add('ai-os-compressed');
                if (window.__TAURI__) {
                    window.__TAURI__.window.appWindow.setSize(new window.__TAURI__.window.PhysicalSize(660, 80));
                }

                console.log("Isolation complete.");
                
                // Expand window slightly on input
                const richTextArea = target.querySelector('rich-textarea') || target.querySelector('textarea') || target.querySelector('div[contenteditable="true"]');
                if (richTextArea) {
                    richTextArea.addEventListener('input', () => {
                         if (document.body.classList.contains('ai-os-compressed')) {
                             if (window.__TAURI__) {
                                 // Simple expansion heuristic based on height or just a fixed larger height
                                 window.__TAURI__.window.appWindow.setSize(new window.__TAURI__.window.PhysicalSize(660, 400));
                             }
                         }
                    });
                }
            }
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', initIsolation);
            } else {
                initIsolation();
            }
        })();
    "#;

    let floating_window = tauri::WindowBuilder::new(
        &app_handle,
        "floating",
        tauri::WindowUrl::External("https://gemini.google.com".parse().unwrap())
    )
    .title("Gemini Floating")
    .initialization_script(floating_init_script)
    .decorations(false)
    .transparent(true)
    .always_on_top(true)
    .visible(false)
    .build()
    .unwrap();
    
    // Set initial size
    let _ = floating_window.set_size(tauri::Size::Physical(tauri::PhysicalSize { width: 660, height: 80 }));
