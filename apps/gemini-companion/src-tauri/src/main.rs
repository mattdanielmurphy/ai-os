mod cloud_sync;
mod fs_bridge;
mod shell_bridge;
mod context_snapshot;
mod proxy;
mod pty;
mod server;
mod session;
mod threads;
mod types;

use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use tauri::GlobalShortcutManager;
use tauri::Manager;

use crate::types::AppState;

#[tauri::command]
fn spawn_fresh_engine(
    project_path: String,
    engine: String,
    thread_id: Option<String>,
    state: tauri::State<AppState>,
) -> Result<u32, String> {
    let app_handle = state.app_handle.clone();
    pty::spawn_fresh_engine(project_path, engine, thread_id, app_handle, state)
}

#[derive(serde::Deserialize)]
pub struct QueryCallbackPayload {
    #[serde(alias = "queryId")]
    pub query_id: String,
    pub response: Option<String>,
    pub error: Option<String>,
}

#[tauri::command]
async fn query_callback(
    payload: QueryCallbackPayload,
) -> Result<(), String> {
    let mut callbacks = server::get_query_callbacks().lock().await;
    if let Some(tx) = callbacks.remove(&payload.query_id) {
        if let Some(e) = payload.error {
            let _ = tx.send(Err(e));
        } else {
            let _ = tx.send(Ok(payload.response.unwrap_or_default()));
        }
        Ok(())
    } else {
        Err("Query ID not found or timed out".to_string())
    }
}

fn main() {
    std::env::set_var("RUST_BACKTRACE", "1");
    std::panic::set_hook(Box::new(|panic_info| {
        let backtrace = std::backtrace::Backtrace::capture();
        let home = std::env::var("HOME").unwrap_or_default();
        let log_dir = std::path::Path::new(&home)
            .join(".ai-os")
            .join("crash_logs");
        let _ = std::fs::create_dir_all(&log_dir);
        let timestamp = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();
        let file_path = log_dir.join(format!("crash_{}.log", timestamp));
        let msg = format!("Panic: {}\nBacktrace:\n{:?}", panic_info, backtrace);
        let _ = std::fs::write(&file_path, &msg);
        eprintln!("[AI-OS CRASH LOG WRITTEN] {}", file_path.display());
    }));
    let path =
        std::env::var("PATH").unwrap_or_else(|_| "/usr/bin:/bin:/usr/sbin:/sbin".to_string());
    let home = std::env::var("HOME").unwrap_or_default();
    let new_path = format!(
        "/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/local/sbin:{}/.local/bin:{}/.cargo/bin:{}/.gemini/antigravity-cli/bin:{}/.nvm/versions/node/v18.17.0/bin:{}/.nvm/versions/node/v26.3.0/bin:{}/bin:{}",
        home, home, home, home, home, home, path
    );
    std::env::set_var("PATH", new_path);

    let context = tauri::generate_context!();
    let app_name = &context.package_info().name;

    let app_menu = tauri::Menu::new()
        .add_native_item(tauri::MenuItem::About(
            app_name.to_string(),
            tauri::AboutMetadata::default(),
        ))
        .add_native_item(tauri::MenuItem::Separator)
        .add_native_item(tauri::MenuItem::Services)
        .add_native_item(tauri::MenuItem::Separator)
        .add_native_item(tauri::MenuItem::Hide)
        .add_native_item(tauri::MenuItem::HideOthers)
        .add_native_item(tauri::MenuItem::ShowAll)
        .add_native_item(tauri::MenuItem::Separator)
        .add_native_item(tauri::MenuItem::Quit);

    let file_menu = tauri::Menu::new()
        .add_item(tauri::CustomMenuItem::new("new_window", "New Gemini Window").accelerator("Cmd+N"))
        .add_item(tauri::CustomMenuItem::new("new_pplx_window", "New Perplexity Window").accelerator("Cmd+Shift+P"))
        .add_native_item(tauri::MenuItem::Separator)
        .add_native_item(tauri::MenuItem::CloseWindow);

    let edit_menu = tauri::Menu::new()
        .add_native_item(tauri::MenuItem::Undo)
        .add_native_item(tauri::MenuItem::Redo)
        .add_native_item(tauri::MenuItem::Separator)
        .add_native_item(tauri::MenuItem::Cut)
        .add_native_item(tauri::MenuItem::Copy)
        .add_native_item(tauri::MenuItem::Paste)
        .add_native_item(tauri::MenuItem::SelectAll)
        .add_native_item(tauri::MenuItem::Separator)
        .add_item(tauri::CustomMenuItem::new("find", "Find on Page...").accelerator("Cmd+F"));

    let view_menu = tauri::Menu::new()
        .add_item(tauri::CustomMenuItem::new("reload", "Reload Page").accelerator("Cmd+R"))
        .add_item(
            tauri::CustomMenuItem::new("toggle_devtools", "Toggle Developer Tools")
                .accelerator("Cmd+Alt+I"),
        )
        .add_native_item(tauri::MenuItem::Separator)
        .add_native_item(tauri::MenuItem::EnterFullScreen);

    let window_menu = tauri::Menu::new()
        .add_native_item(tauri::MenuItem::Minimize)
        .add_native_item(tauri::MenuItem::Zoom)
        .add_native_item(tauri::MenuItem::Separator)
        .add_item(tauri::CustomMenuItem::new("focus_gemini", "Gemini Window").accelerator("Cmd+1"))
        .add_item(tauri::CustomMenuItem::new("focus_perplexity", "Perplexity Window").accelerator("Cmd+2"))
        .add_item(
            tauri::CustomMenuItem::new("focus_coding", "Coding Harness Window")
                .accelerator("Cmd+3"),
        )
        .add_item(
            tauri::CustomMenuItem::new(
                "toggle_quick_prompt",
                "Toggle Quick Prompt Floating Window",
            )
            .accelerator("Cmd+Alt+Space"),
        );

    let coding_menu = tauri::Menu::new()
        .add_item(
            tauri::CustomMenuItem::new("new_engine", "Spawn Fresh Engine")
                .accelerator("Cmd+Shift+N"),
        )
        .add_item(
            tauri::CustomMenuItem::new("switch_project", "Switch Active Project...")
                .accelerator("Cmd+O"),
        )
        .add_item(
            tauri::CustomMenuItem::new("search_threads", "Search AI Threads...")
                .accelerator("Cmd+Shift+F"),
        );

    let help_menu = tauri::Menu::new().add_item(tauri::CustomMenuItem::new(
        "help_docs",
        "AI-OS Documentation",
    ));

    let menu = tauri::Menu::new()
        .add_submenu(tauri::Submenu::new(app_name, app_menu))
        .add_submenu(tauri::Submenu::new("File", file_menu))
        .add_submenu(tauri::Submenu::new("Edit", edit_menu))
        .add_submenu(tauri::Submenu::new("View", view_menu))
        .add_submenu(tauri::Submenu::new("Window", window_menu))
        .add_submenu(tauri::Submenu::new("Coding Engine", coding_menu))
        .add_submenu(tauri::Submenu::new("Help", help_menu));

    tauri::Builder::default()
        .menu(menu)
        .setup(|app| {
            let app_handle = app.handle();
            cloud_sync::start_sync_scheduler(app_handle.clone());
            // ... (rest of setup)

            // --- floating window init script ---
            let floating_init_script = r#"
                (function() {
                    let isTransformed = false;
                    let modifiedElements = [];
                    let addedStyleSheet = null;

                    function transformToNormalWebview() {
                        if (isTransformed) return;
                        isTransformed = true;

                        for (let el of modifiedElements) {
                            if (el && el.style) {
                                el.style.visibility = '';
                                el.style.pointerEvents = '';
                                el.style.background = '';
                                el.style.backgroundImage = '';
                            }
                        }
                        modifiedElements = [];

                        document.documentElement.style.background = '#131314';
                        document.body.style.background = '#131314';
                        const cw = document.querySelector('chat-window');
                        if (cw) {
                            cw.style.background = '#131314';
                        }
                        document.documentElement.style.paddingTop = '';
                        if (document.body) {
                            document.body.style.paddingTop = '';
                        }

                        const target = document.querySelector('.input-area-container');
                        if (target) {
                            target.style.zIndex = '';
                        }

                        if (addedStyleSheet && document.adoptedStyleSheets) {
                            try {
                                document.adoptedStyleSheets = document.adoptedStyleSheets.filter(s => s !== addedStyleSheet);
                            } catch (e) {}
                        }

                        const chatApp = document.querySelector('chat-app');
                        if (chatApp) {
                            chatApp.style.paddingTop = '';
                        }

                        if (window.__TAURI__) {
                            const appWin = window.__TAURI__.window.appWindow;
                            try {
                                if (appWin && typeof appWin.setDecorations === 'function') {
                                    appWin.setDecorations(true);
                                }
                            } catch (e) {
                                console.log('setDecorations ignored or unsupported in runtime:', e);
                            }

                            const screenH = window.screen.availHeight || 900;
                            const screenW = window.screen.availWidth || 1440;
                            const targetH = Math.min(760, Math.max(500, Math.floor(screenH * 0.80)));
                            const targetW = Math.min(1200, Math.max(800, Math.floor(screenW * 0.82)));

                            if (window.__TAURI__.window.LogicalSize) {
                                appWin.setSize(new window.__TAURI__.window.LogicalSize(targetW, targetH));
                            } else {
                                appWin.setSize(new window.__TAURI__.window.PhysicalSize(targetW, targetH));
                            }
                            appWin.center();
                        }
                    }

                    function initIsolation() {
                      const target = document.querySelector('.input-area-container');

                      if (!target) {
                        setTimeout(initIsolation, 500);
                        return;
                      }

                      if (isTransformed) return;

                      target.style.setProperty('z-index', '9999999', 'important');

                      let current = target;
                      while (current && current !== document.body && current !== document.documentElement) {
                        const siblings = current.parentElement.children;
                        for (let sibling of siblings) {
                          if (sibling !== current) {
                            sibling.style.visibility = 'hidden';
                            sibling.style.pointerEvents = 'none';
                            modifiedElements.push(sibling);
                          }
                        }
                        current.style.visibility = 'visible';
                        if (current !== target) {
                          current.style.background = 'transparent';
                          current.style.backgroundImage = 'none';
                          modifiedElements.push(current);
                        }
                        current = current.parentElement;
                      }

                      document.documentElement.style.background = 'transparent';
                      document.body.style.background = 'transparent';

                      target.addEventListener('mousedown', (e) => {
                          if (isTransformed) return;
                          if (e.target.tagName !== 'TEXTAREA' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'BUTTON' && !e.target.closest('button')) {
                              if (window.__TAURI__) {
                                  window.__TAURI__.window.appWindow.startDragging();
                              }
                          }
                      });

                      document.addEventListener('keydown', (e) => {
                          if (e.metaKey && e.altKey && (e.code === 'KeyI' || e.key === 'i' || e.key === 'I')) {
                              if (window.__TAURI__ && window.__TAURI__.invoke) {
                                  window.__TAURI__.invoke('open_devtools');
                              }
                          }
                          if (!isTransformed && e.key === 'Enter' && !e.shiftKey && !e.isComposing) {
                              const active = document.activeElement;
                              if (active && (active.tagName === 'TEXTAREA' || active.isContentEditable || active.getAttribute('contenteditable') === 'true' || active.closest('rich-textarea, .input-area-container'))) {
                                  setTimeout(transformToNormalWebview, 100);
                              }
                          }
                      }, true);

                      document.addEventListener('click', (e) => {
                          if (isTransformed) return;
                          const btn = e.target.closest('button');
                          if (btn) {
                              const aria = (btn.getAttribute('aria-label') || '').toLowerCase();
                              const className = (btn.className || '').toString().toLowerCase();
                              if (aria.includes('send') || className.includes('send') || btn.querySelector('mat-icon[fonticon*="send"]') || btn.closest('.send-button-container')) {
                                  setTimeout(transformToNormalWebview, 100);
                              }
                          }
                      }, true);

                      let lastHeight = 324;
                      let resizeTimeout;

                      function calculateAndSetSize() {
                          if (isTransformed) return;

                          if (document.querySelector('user-message, model-message, message-list, .conversation-container, .response-container-content')) {
                              transformToNormalWebview();
                              return;
                          }

                          let desiredHeight = 180;
                          const textboxes = Array.from(document.querySelectorAll('textarea, [contenteditable="true"], rich-textarea'));
                          let mainInput = null;
                          let maxArea = 0;
                          for (const tb of textboxes) {
                              const rect = tb.getBoundingClientRect();
                              const area = rect.width * rect.height;
                              if (area > maxArea) {
                                  maxArea = area;
                                  mainInput = tb;
                              }
                          }
                          if (mainInput) {
                              const rect = mainInput.getBoundingClientRect();
                              if (rect.height > 60) {
                                  desiredHeight += (rect.height - 60);
                              }
                          }
                          let hasHistory = false;
                          let inputText = mainInput ? (mainInput.value || mainInput.innerText || "") : "";
                          let bodyText = document.body.innerText || "";
                          if (bodyText.length - inputText.length > 2500) {
                              hasHistory = true;
                          }
                          if (hasHistory) {
                              transformToNormalWebview();
                              return;
                          }
                          desiredHeight = Math.round(desiredHeight * 1.8);
                          desiredHeight = Math.max(324, Math.min(1440, desiredHeight));
                          if (Math.abs(desiredHeight - lastHeight) > 5) {
                              lastHeight = desiredHeight;
                              if (window.__TAURI__) {
                                  if (window.__TAURI__.window.LogicalSize) {
                                      window.__TAURI__.window.appWindow.setSize(new window.__TAURI__.window.LogicalSize(960, desiredHeight));
                                  } else {
                                      window.__TAURI__.window.appWindow.setSize(new window.__TAURI__.window.PhysicalSize(960, desiredHeight));
                                  }
                              }
                          }
                      }

                      const resizeObserver = new ResizeObserver(() => {
                          if (isTransformed) return;
                          clearTimeout(resizeTimeout);
                          resizeTimeout = setTimeout(calculateAndSetSize, 100);
                      });
                      const inputContainer = document.querySelector('.input-area-container');
                      if (inputContainer) resizeObserver.observe(inputContainer);

                      const mutObserver = new MutationObserver((mutations) => {
                          if (isTransformed) return;
                          let shouldCheck = false;
                          for (const m of mutations) {
                              if (m.addedNodes.length > 0 || m.removedNodes.length > 0) {
                                  shouldCheck = true;
                                  break;
                              }
                          }
                          if (!shouldCheck) return;
                          clearTimeout(resizeTimeout);
                          resizeTimeout = setTimeout(calculateAndSetSize, 100);
                      });
                      mutObserver.observe(document.body, { childList: true, subtree: true });

                      const chatWindow = document.querySelector('chat-window');
                      if (chatWindow) {
                        chatWindow.classList.remove('show-lm-background', 'lm-canvas-styling');
                      }

                      const applyChatAppPadding = () => {
                        if (isTransformed) return;
                        const chatApp = document.querySelector('chat-app');
                        if (chatApp) {
                          chatApp.style.setProperty('padding-top', '0px', 'important');
                          chatApp.style.paddingTop = '0px';
                        }
                      };
                      applyChatAppPadding();
                      const chatAppObserver = new MutationObserver(applyChatAppPadding);
                      chatAppObserver.observe(document.body, { childList: true, subtree: true });
                    }
                    function resetToFloatingMiniMode() {
                        isTransformed = false;
                        document.documentElement.style.background = 'transparent';
                        document.body.style.background = 'transparent';
                        initIsolation();
                    }

                    if (document.readyState === 'loading') {
                        document.addEventListener('DOMContentLoaded', initIsolation);
                    } else {
                        initIsolation();
                    }
                })();
            "#;

            // NOTE: This is a symlink to the GENERATED file
            // ~/projects/userscript-bundler/compiled/gemini-enhancements.user.js.
            // Do NOT edit it directly — edit the source modules in
            // ~/projects/userscript-bundler/userscripts/gemini-enhancements/ and
            // rebuild with `cd ~/projects/userscript-bundler && node bundler.cjs`.
            let userscript_code = std::fs::read_to_string("/Users/matt/projects/ai-os/userscripts/gemini-DO-NOT-EDIT.js").unwrap_or_default();
            let gemini_engine_code = std::fs::read_to_string("/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/engines/gemini-engine.js").unwrap_or_default();
            let full_gemini_init_script = format!("{}\n{}", userscript_code, gemini_engine_code);
            let pplx_engine_code = std::fs::read_to_string("/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/engines/perplexity-engine.js").unwrap_or_default();

            // 1. Expanded Normal Gemini Window (App Launch Target)
            let gemini_main_window = tauri::WindowBuilder::new(
                &app_handle,
                "gemini_main",
                tauri::WindowUrl::External("https://gemini.google.com/app".parse().unwrap()),
            )
            .title("Gemini")
            .initialization_script(&full_gemini_init_script)
            .visible(true)
            .decorations(true)
            .transparent(false)
            .inner_size(1200.0, 760.0)
            .build()
            .unwrap();

            let _ = gemini_main_window.center();

            // 2. Dedicated Perplexity Window
            let perplexity_main_window = tauri::WindowBuilder::new(
                &app_handle,
                "perplexity_main",
                tauri::WindowUrl::External("https://www.perplexity.ai".parse().unwrap()),
            )
            .title("Perplexity")
            .initialization_script(&pplx_engine_code)
            .visible(true)
            .decorations(true)
            .transparent(false)
            .inner_size(1200.0, 760.0)
            .build()
            .unwrap();

            let _ = perplexity_main_window.center();

            // 3. Dedicated Floating Mini-Window Mode (Triggered only by Cmd+Option+Space)
            let full_floating_init_script = format!("{}\n{}", userscript_code, floating_init_script);

            let floating_window = tauri::WindowBuilder::new(
                &app_handle,
                "floating",
                tauri::WindowUrl::External("https://gemini.google.com/app".parse().unwrap()),
            )
            .title("Gemini Quick Prompt")
            .initialization_script(&full_floating_init_script)
            .visible(false)
            .decorations(false)
            .transparent(true)
            .inner_size(960.0, 324.0)
            .build()
            .unwrap();

            let _ = floating_window.center();

            // Hide the default coding window ("main") on startup
            if let Some(main_win) = app_handle.get_window("main") {
                let _ = main_win.hide();
            }

            // --- global shortcuts ---
            let app_handle_clone = app_handle.clone();
            let mut shortcut_manager = app.global_shortcut_manager();
            let _ = shortcut_manager.register("Cmd+Option+Space", move || {
                if let Some(window) = app_handle_clone.get_window("floating") {
                    if window.is_visible().unwrap_or(false) {
                        let _ = window.hide();
                    } else {
                        let _ = window.show();
                        let _ = window.set_focus();
                    }
                }
            });


            // Check for pending prompt file created when CLI launched app
            let home_dir = std::env::var("HOME").unwrap_or_default();
            let pending_prompt_path = std::path::Path::new(&home_dir).join(".ai-os").join("pending_prompt.txt");
            if pending_prompt_path.exists() {
                if let Ok(prompt) = std::fs::read_to_string(&pending_prompt_path) {
                    let _ = std::fs::remove_file(&pending_prompt_path);
                    let js_prompt = serde_json::to_string(&prompt).unwrap_or_default();
                    let eval_script = format!(
                        r#"
                        (function() {{
                            if (window.injectAndSendPrompt) {{
                                window.injectAndSendPrompt({});
                            }} else {{
                                window.__pendingPrompt = {};
                            }}
                        }})();
                        "#,
                        js_prompt, js_prompt
                    );
                    let _ = gemini_main_window.eval(&eval_script);
                }
            }

            // Check for pending Perplexity prompt file created when CLI launched app
            let pending_pplx_prompt_path = std::path::Path::new(&home_dir).join(".ai-os").join("pending_pplx_prompt.txt");
            if pending_pplx_prompt_path.exists() {
                if let Ok(prompt) = std::fs::read_to_string(&pending_pplx_prompt_path) {
                    let _ = std::fs::remove_file(&pending_pplx_prompt_path);
                    let js_prompt = serde_json::to_string(&prompt).unwrap_or_default();
                    let eval_script = format!(
                        r#"
                        (function() {{
                            if (window.injectAndSendPrompt) {{
                                window.injectAndSendPrompt({});
                            }} else if (window.__proximaPerplexity && window.__proximaPerplexity.send) {{
                                window.__proximaPerplexity.send({});
                            }}
                        }})();
                        "#,
                        js_prompt, js_prompt
                    );
                    let _ = perplexity_main_window.eval(&eval_script);
                }
            }

            // --- spawn servers ---
            proxy::spawn_proxy_server(app_handle.clone());
            server::spawn_axum_server(app_handle.clone());

            // --- state ---
            let sessions = Arc::new(Mutex::new(HashMap::new()));
            let active_project = Arc::new(Mutex::new(None));
            let last_active_account = Arc::new(Mutex::new(None));

            app.manage(AppState {
                sessions,
                active_project,
                app_handle,
                last_active_account,
            });

            Ok(())
        })
        .on_menu_event(|event| {
            let app_handle = event.window().app_handle();
            match event.menu_item_id() {
                "new_window" => {
                    if let Some(win) = app_handle.get_window("gemini_main") {
                        let _ = win.show();
                        let _ = win.unminimize();
                        let _ = win.set_focus();
                    }
                }
                "new_pplx_window" => {
                    if let Some(win) = app_handle.get_window("perplexity_main") {
                        let _ = win.show();
                        let _ = win.unminimize();
                        let _ = win.set_focus();
                    }
                }
                "find" => {
                    let _ = event.window().eval(r#"
                        if (window.find) {
                            const query = prompt('Find in page:');
                            if (query) window.find(query);
                        }
                    "#);
                }
                "reload" => {
                    let _ = event.window().eval("window.location.reload();");
                }
                "toggle_devtools" => {
                    if event.window().is_devtools_open() {
                        event.window().close_devtools();
                    } else {
                        event.window().open_devtools();
                    }
                }
                "focus_gemini" => {
                    if let Some(win) = app_handle.get_window("gemini_main") {
                        let _ = win.show();
                        let _ = win.unminimize();
                        let _ = win.set_focus();
                    }
                }
                "focus_perplexity" => {
                    if let Some(win) = app_handle.get_window("perplexity_main") {
                        let _ = win.show();
                        let _ = win.unminimize();
                        let _ = win.set_focus();
                    }
                }
                "focus_coding" => {
                    if let Some(win) = app_handle.get_window("main") {
                        let _ = win.show();
                        let _ = win.unminimize();
                        let _ = win.set_focus();
                    }
                }
                "toggle_quick_prompt" => {
                    if let Some(win) = app_handle.get_window("floating") {
                        if win.is_visible().unwrap_or(false) {
                            let _ = win.hide();
                        } else {
                            let _ = win.show();
                            let _ = win.set_focus();
                        }
                    }
                }
                "help_docs" => {
                    let _ = event.window().eval("window.open('https://github.com/mattdanielmurphy/ai-os', '_blank');");
                }
                _ => {}
            }
        })
        .on_page_load(|window, _| {
            let _ = window.eval(
                r#"
                document.addEventListener('keydown', (e) => {
                    if (e.metaKey && e.altKey && (e.code === 'KeyI' || e.key === 'i' || e.key === 'I')) {
                        if (window.__TAURI__ && window.__TAURI__.invoke) {
                            window.__TAURI__.invoke('open_devtools');
                        }
                    }
                    if (e.metaKey && (e.code === 'KeyT' || e.key === 't' || e.key === 'T')) {
                        e.preventDefault();
                        e.stopPropagation();
                        const btn = document.querySelector('[data-test-id="new-chat-button"] a') ||
                                    document.querySelector('[data-test-id="new-chat-button"]') ||
                                    document.querySelector('a[aria-label="New chat"]');
                        if (btn) {
                            btn.click();
                        } else {
                            window.location.href = 'https://gemini.google.com/app';
                        }
                    }
                }, true);
            "#,
            );
        })
        .invoke_handler(tauri::generate_handler![
            session::refresh_tmux_session,
            spawn_fresh_engine,
            session::switch_active_project,
            session::write_to_pty,
            session::resize_pty,
            session::is_engine_running,
            session::toggle_process_pause,
            session::close_project_session,
            session::select_directory,
            session::create_new_project,
            session::get_initial_project,
            threads::get_project_threads,
            threads::delete_thread,
            threads::get_all_agy_threads,
            session::copy_tmux_selection,
            session::open_path,
            session::save_prompt_draft,
            session::load_prompt_draft,
            threads::read_thread_log,
            threads::file_exists,
            threads::patch_thread_log_with_output,
            session::open_devtools,
            session::get_quota,
            session::ensure_hermes_running,
            threads::search_project_threads,
            query_callback,
        ])
        .run(context)
        .expect("error while running tauri application");
}
