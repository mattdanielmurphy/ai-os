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
fn prepare_spare_engine(project_path: String, engine: String) -> Result<(), String> {
    pty::prepare_spare_engine_inner(project_path, engine)
}

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
                    function initIsolation() {
                      const target = document.querySelector('.input-area-container');

                      if (!target) {
                        setTimeout(initIsolation, 500);
                        return;
                      }

                      target.style.setProperty('z-index', '9999999', 'important');

                      let current = target;
                      while (current && current !== document.body && current !== document.documentElement) {
                        const siblings = current.parentElement.children;
                        for (let sibling of siblings) {
                          if (sibling !== current) {
                            sibling.style.visibility = 'hidden';
                            sibling.style.pointerEvents = 'none';
                          }
                        }
                        current.style.visibility = 'visible';
                        if (current !== target) {
                          current.style.background = 'transparent';
                          current.style.backgroundImage = 'none';
                        }
                        current = current.parentElement;
                      }

                      document.documentElement.style.background = 'transparent';
                      document.body.style.background = 'transparent';

                      target.addEventListener('mousedown', (e) => {
                          if (e.target.tagName !== 'TEXTAREA' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'BUTTON' && !e.target.closest('button')) {
                              if (window.__TAURI__) {
                                  window.__TAURI__.window.appWindow.startDragging();
                              }
                          }
                      });

                      let lastHeight = 324;
                      let resizeTimeout;

                      function calculateAndSetSize() {
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
                          if (document.querySelector('user-message, model-message, message-list')) {
                              hasHistory = true;
                          } else {
                              let inputText = mainInput ? (mainInput.value || mainInput.innerText || "") : "";
                              let bodyText = document.body.innerText || "";
                              if (bodyText.length - inputText.length > 500) {
                                  hasHistory = true;
                              }
                          }
                          if (hasHistory) {
                              desiredHeight = 800;
                          }
                          desiredHeight = Math.round(desiredHeight * 1.8);
                          desiredHeight = Math.max(324, Math.min(1440, desiredHeight));
                          if (Math.abs(desiredHeight - lastHeight) > 5) {
                              lastHeight = desiredHeight;
                              if (window.__TAURI__) {
                                  window.__TAURI__.window.appWindow.setSize(new window.__TAURI__.window.PhysicalSize(960, desiredHeight));
                              }
                          }
                      }

                      const resizeObserver = new ResizeObserver(() => {
                          clearTimeout(resizeTimeout);
                          resizeTimeout = setTimeout(calculateAndSetSize, 50);
                      });
                      resizeObserver.observe(document.body);

                      const mutObserver = new MutationObserver(() => {
                          clearTimeout(resizeTimeout);
                          resizeTimeout = setTimeout(calculateAndSetSize, 50);
                      });
                      mutObserver.observe(document.body, { childList: true, subtree: true, characterData: true });

                      const chatWindow = document.querySelector('chat-window');
                      if (chatWindow) {
                        chatWindow.classList.remove('show-lm-background', 'lm-canvas-styling');
                      }

                      try {
                        const sheet = new CSSStyleSheet();
                        sheet.replaceSync(`
                          chat-window::before,
                          chat-window::after {
                            display: none !important;
                            background-image: none !important;
                            opacity: 0 !important;
                          }
                          chat-app {
                            padding-top: 0px !important;
                          }
                          .input-area-container {
                            z-index: 9999999 !important;
                          }
                        `);
                        document.adoptedStyleSheets = [...document.adoptedStyleSheets, sheet];
                      } catch (e) {
                        console.log('Constructable stylesheets blocked or unsupported, relying on class removal.', e);
                      }

                      document.addEventListener('keydown', (e) => {
                          if (e.metaKey && e.altKey && e.code === 'KeyI') {
                              if (window.__TAURI__) {
                                  window.__TAURI__.invoke('open_devtools');
                              }
                          }
                      });

                      const applyChatAppPadding = () => {
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

            let floating_window = tauri::WindowBuilder::new(
                &app_handle,
                "floating",
                tauri::WindowUrl::External("https://gemini.google.com/app".parse().unwrap()),
            )
            .title("Gemini Floating")
            .initialization_script(floating_init_script)
            .visible(false)
            .decorations(false)
            .transparent(true)
            .build()
            .unwrap();

            let _ = floating_window.set_size(tauri::Size::Physical(tauri::PhysicalSize {
                width: 960,
                height: 324,
            }));

            // --- global shortcut ---
            let app_handle_clone = app_handle.clone();
            let mut shortcut_manager = app.global_shortcut_manager();
            let _ = shortcut_manager.register("Cmd+Option+Space", move || {
                if let Some(window) = app_handle_clone.get_window("floating") {
                    if window.is_visible().unwrap_or(false) {
                        let _ = window.hide();
                    } else {
                        let _ = window.eval("window.location.href = 'https://gemini.google.com/app';");
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
            let staged_payload = Arc::new(Mutex::new(None));
            let last_active_account = Arc::new(Mutex::new(None));

            app.manage(AppState {
                sessions,
                active_project,
                app_handle,
                staged_payload,
                last_active_account,
            });

            Ok(())
        })
        .on_page_load(|window, _| {
            let _ = window.eval(
                r#"
                document.addEventListener('keydown', (e) => {
                    if (e.metaKey && e.altKey && e.code === 'KeyI') {
                        if (window.__TAURI__) {
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
            session::initialize_project_session,
            prepare_spare_engine,
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
            session::get_browser_context,
            session::dispatch_to_gemini,
            threads::search_project_threads,
            session::read_thread_notes_file,
            session::write_thread_notes_file,
            session::get_staged_payload,
            session::get_recent_workspaces,
            session::confirm_staged_execution
        ])
        .run(context)
        .expect("error while running tauri application");
}
