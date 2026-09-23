mod types;

#[path = "../../../gemini-companion/src-tauri/src/server.rs"]
mod server;

const PERPLEXITY_ENGINE: &str = include_str!("../../../gemini-companion/src-tauri/engines/perplexity-engine.js");
const GEMINI_ENGINE: &str = include_str!("../../../gemini-companion/src-tauri/engines/gemini-engine.js");

#[derive(serde::Deserialize)]
struct QueryCallbackPayload {
    #[serde(alias = "queryId")]
    query_id: Option<String>,
    response: Option<String>,
    error: Option<String>,
    err_msg: Option<String>,
    payload: Option<Box<QueryCallbackPayload>>,
}

#[tauri::command]
async fn query_callback(
    query_id: Option<String>,
    response: Option<String>,
    error: Option<String>,
    err_msg: Option<String>,
    payload: Option<QueryCallbackPayload>,
) -> Result<(), String> {
    let query_id = query_id
        .or_else(|| payload.as_ref().and_then(|item| item.query_id.clone()))
        .or_else(|| payload.as_ref().and_then(|item| item.payload.as_ref().and_then(|nested| nested.query_id.clone())))
        .unwrap_or_default();
    let response = response
        .or_else(|| payload.as_ref().and_then(|item| item.response.clone()))
        .or_else(|| payload.as_ref().and_then(|item| item.payload.as_ref().and_then(|nested| nested.response.clone())));
    let error = error
        .or(err_msg)
        .or_else(|| payload.as_ref().and_then(|item| item.error.clone()))
        .or_else(|| payload.as_ref().and_then(|item| item.err_msg.clone()))
        .or_else(|| payload.as_ref().and_then(|item| item.payload.as_ref().and_then(|nested| nested.error.clone())));

    if server::resolve_query_callback(&query_id, response, error).await {
        Ok(())
    } else {
        Err("Query ID not found or timed out".to_string())
    }
}

#[cfg(target_os = "macos")]
fn disable_app_nap() {
    use cocoa::base::nil;
    use cocoa::foundation::NSString;
    use objc::runtime::{Class, Object};
    use objc::{msg_send, sel, sel_impl};

    unsafe {
        if let Some(process_info_cls) = Class::get("NSProcessInfo") {
            let process_info: *mut Object = msg_send![process_info_cls, processInfo];
            if !process_info.is_null() {
                let options: u64 = 0x00FFFFFF | (1 << 8) | (1 << 14) | (1 << 20);
                let reason = NSString::alloc(nil).init_str("AIOS Query Companion");
                let _: *mut Object = msg_send![process_info, beginActivityWithOptions:options reason:reason];
            }
        }
    }
}

pub fn create_perplexity_window(app_handle: &tauri::AppHandle) -> Result<tauri::Window, tauri::Error> {
    tauri::WindowBuilder::new(
        app_handle,
        "perplexity_main",
        tauri::WindowUrl::External("https://www.perplexity.ai".parse().unwrap()),
    )
    .title("AIOS Query Companion")
    .initialization_script(PERPLEXITY_ENGINE)
    .visible(false)
    .decorations(false)
    .inner_size(1.0, 1.0)
    .build()
}

pub fn create_gemini_window(app_handle: &tauri::AppHandle) -> Result<tauri::Window, tauri::Error> {
    tauri::WindowBuilder::new(
        app_handle,
        "gemini_main",
        tauri::WindowUrl::External("https://gemini.google.com/app".parse().unwrap()),
    )
    .title("AIOS Query Companion")
    .initialization_script(GEMINI_ENGINE)
    .visible(false)
    .decorations(false)
    .inner_size(1.0, 1.0)
    .build()
}

fn main() {
    #[cfg(target_os = "macos")]
    disable_app_nap();

    let app = tauri::Builder::default()
        .setup(|app| {
            #[cfg(target_os = "macos")]
            app.set_activation_policy(tauri::ActivationPolicy::Accessory);

            let app_handle = app.handle();
            create_perplexity_window(&app_handle)?;
            server::spawn_axum_server(app_handle);
            Ok(())
        })
        .on_window_event(|event| {
            if let tauri::WindowEvent::CloseRequested { api, .. } = event.event() {
                api.prevent_close();
                let _ = event.window().hide();
            }
        })
        .invoke_handler(tauri::generate_handler![query_callback])
        .build(tauri::generate_context!())
        .expect("AIOS Query Companion failed");

    app.run(|_, event| {
        if let tauri::RunEvent::ExitRequested { api, .. } = event {
            api.prevent_exit();
        }
    });
}
