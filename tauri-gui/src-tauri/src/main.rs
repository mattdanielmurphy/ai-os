mod types;
mod pty;
mod threads;
mod server;
mod session;

use std::sync::{Arc, Mutex};
use std::collections::HashMap;
use tauri::Manager;
use tauri::GlobalShortcutManager;

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

fn main() {
    let path = std::env::var("PATH").unwrap_or_else(|_| "/usr/bin:/bin:/usr/sbin:/sbin".to_string());
    let home = std::env::var("HOME").unwrap_or_default();
    let new_path = format!(
        "/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/local/sbin:{}/.local/bin:{}/.cargo/bin:{}/.gemini/antigravity-cli/bin:{}/.nvm/versions/node/v18.17.0/bin:{}/.nvm/versions/node/v26.3.0/bin:{}/bin:{}",
        home, home, home, home, home, home, path
    );
    std::env::set_var("PATH", new_path);

    let context = tauri::generate_context!();
    tauri::Builder::default()
        .menu(tauri::Menu::os_default(&context.package_info().name))
        .setup(|app| {
            let app_handle = app.handle();

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
                            appWin.setDecorations(true);

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
                          resizeTimeout = setTimeout(calculateAndSetSize, 50);
                      });
                      resizeObserver.observe(document.body);

                      const mutObserver = new MutationObserver(() => {
                          if (isTransformed) return;
                          clearTimeout(resizeTimeout);
                          resizeTimeout = setTimeout(calculateAndSetSize, 50);
                      });
                      mutObserver.observe(document.body, { childList: true, subtree: true, characterData: true });

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
                    if (document.readyState === 'loading') {
                        document.addEventListener('DOMContentLoaded', initIsolation);
                    } else {
                        initIsolation();
                    }
                })();
            "#;

            let userscript_code = std::fs::read_to_string("/Users/matt/projects/ai-os/userscripts/gemini.js").unwrap_or_default();
            let full_init_script = format!("{}\n{}", userscript_code, floating_init_script);

            let floating_window = tauri::WindowBuilder::new(
                &app_handle,
                "floating",
                tauri::WindowUrl::External("https://gemini.google.com/app".parse().unwrap()),
            )
            .title("Gemini")
            .initialization_script(&full_init_script)
            .visible(true)
            .decorations(false)
            .transparent(true)
            .build()
            .unwrap();

            let target_h = 760.0;
            let target_w = 1200.0;

            let _ = floating_window.set_size(tauri::Size::Logical(tauri::LogicalSize {
                width: target_w,
                height: target_h,
            }));
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

            let app_handle_coding = app_handle.clone();
            let _ = shortcut_manager.register("Cmd+Option+C", move || {
                if let Some(window) = app_handle_coding.get_window("main") {
                    if window.is_visible().unwrap_or(false) {
                        let _ = window.hide();
                    } else {
                        let _ = window.show();
                        let _ = window.set_focus();
                    }
                }
            });

            // --- spawn servers ---
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
        .on_page_load(|window, _| {
            let _ = window.eval(
                r#"
                document.addEventListener('keydown', (e) => {
                    if (e.metaKey && e.altKey && (e.code === 'KeyI' || e.key === 'i' || e.key === 'I')) {
                        if (window.__TAURI__ && window.__TAURI__.invoke) {
                            window.__TAURI__.invoke('open_devtools');
                        }
                    }
                });
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
        ])
        .run(context)
        .expect("error while running tauri application");
}
