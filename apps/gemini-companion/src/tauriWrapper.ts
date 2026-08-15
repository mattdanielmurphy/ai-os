import { invoke as tauriInvoke } from '@tauri-apps/api/tauri'
import { listen as tauriListen } from '@tauri-apps/api/event'
import { appWindow as tauriAppWindow, PhysicalSize, PhysicalPosition } from '@tauri-apps/api/window'
import { open as tauriOpen } from '@tauri-apps/api/shell'
import type { EventCallback, UnlistenFn } from '@tauri-apps/api/event'

export const isBrowser = () => typeof window !== 'undefined' && 
  !(window as any).__TAURI_IPC__ && 
  !(window as any).__TAURI_INTERNALS__ && 
  !(window as any).__TAURI__

let ws: WebSocket | null = null;
const pendingInvokes = new Map<string, { resolve: (val: any) => void; reject: (err: any) => void }>();
const eventListeners = new Map<string, Set<EventCallback<any>>>();
const activeTauriListeners = new Set<string>();

function connectWebSocket() {
  if (typeof window === 'undefined') return;

  if (ws) {
    try { ws.close(); } catch (e) {}
  }

  const wsUrl = 'ws://127.0.0.1:3031/ws';
  console.log(`[Tauri WS Bridge] Connecting to ${wsUrl}...`);
  const socket = new WebSocket(wsUrl);
  ws = socket;

  socket.onopen = () => {
    console.log('[Tauri WS Bridge] Connected successfully.');
    if (isBrowser()) {
      socket.send(JSON.stringify({ type: 'register', role: 'client' }));
      // Re-register existing active listeners
      for (const event of eventListeners.keys()) {
        socket.send(JSON.stringify({ type: 'listen', event }));
      }
    } else {
      socket.send(JSON.stringify({ type: 'register', role: 'host' }));
    }
  };

  socket.onmessage = async (msgEvent) => {
    try {
      const data = JSON.parse(msgEvent.data);
      if (isBrowser()) {
        if (data.type === 'invoke_result') {
          const pending = pendingInvokes.get(data.id);
          if (pending) {
            pendingInvokes.delete(data.id);
            if (data.success) {
              pending.resolve(data.data);
            } else {
              pending.reject(new Error(data.error));
            }
          }
        } else if (data.type === 'event') {
          const handlers = eventListeners.get(data.event);
          if (handlers) {
            for (const handler of handlers) {
              try {
                handler({
                  event: data.event,
                  id: 0,
                  windowLabel: 'main',
                  payload: data.payload
                });
              } catch (e) {
                console.error(`[Tauri WS Bridge] Error in event handler for ${data.event}:`, e);
              }
            }
          }
        }
      } else {
        // Host mode (Tauri App frontend)
        if (data.type === 'invoke') {
          try {
            const result = await tauriInvoke(data.cmd, data.args);
            socket.send(JSON.stringify({
              type: 'invoke_result',
              id: data.id,
              client_id: data.client_id,
              success: true,
              data: result
            }));
          } catch (err: any) {
            socket.send(JSON.stringify({
              type: 'invoke_result',
              id: data.id,
              client_id: data.client_id,
              success: false,
              error: err ? err.toString() : 'Unknown error'
            }));
          }
        } else if (data.type === 'open') {
          try {
            await tauriOpen(data.path, data.withApp);
            socket.send(JSON.stringify({
              type: 'invoke_result',
              id: data.id,
              client_id: data.client_id,
              success: true
            }));
          } catch (err: any) {
            socket.send(JSON.stringify({
              type: 'invoke_result',
              id: data.id,
              client_id: data.client_id,
              success: false,
              error: err ? err.toString() : 'Unknown error'
            }));
          }
        } else if (data.type === 'listen') {
          const eventName = data.event;
          if (!activeTauriListeners.has(eventName)) {
            activeTauriListeners.add(eventName);
            try {
              await tauriListen(eventName, (tauriEvent) => {
                if (socket.readyState === WebSocket.OPEN) {
                  socket.send(JSON.stringify({
                    type: 'event',
                    event: eventName,
                    payload: tauriEvent.payload
                  }));
                }
              });
            } catch (err) {
              console.error(`[Tauri WS Bridge] Failed to listen to Tauri event ${eventName}:`, err);
              activeTauriListeners.delete(eventName);
            }
          }
        }
      }
    } catch (e) {
      console.error('[Tauri WS Bridge] Error parsing message:', e);
    }
  };

  socket.onclose = () => {
    console.log('[Tauri WS Bridge] Connection closed. Reconnecting in 2s...');
    setTimeout(connectWebSocket, 2000);
  };

  socket.onerror = (err) => {
    console.error('[Tauri WS Bridge] WebSocket error:', err);
  };
}

if (typeof window !== 'undefined') {
  connectWebSocket();
}

function sendWsMessage(message: any): Promise<void> {
  return new Promise((resolve, reject) => {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      const checkInterval = setInterval(() => {
        if (ws && ws.readyState === WebSocket.OPEN) {
          clearInterval(checkInterval);
          try {
            ws.send(JSON.stringify(message));
            resolve();
          } catch (e) {
            reject(e);
          }
        }
      }, 100);
      setTimeout(() => {
        clearInterval(checkInterval);
        reject(new Error('[Tauri WS Bridge] Connection timeout'));
      }, 2000);
    } else {
      try {
        ws.send(JSON.stringify(message));
        resolve();
      } catch (e) {
        reject(e);
      }
    }
  });
}

export async function invoke<T>(cmd: string, args?: any): Promise<T> {
  const ptyCmds = [
    "write_to_pty",
    "resize_pty",
    "is_engine_running",
    "toggle_process_pause",
    "switch_active_project",
    "spawn_fresh_engine",
    "initialize_project_session",
    "copy_tmux_selection",
    "refresh_tmux_session",
  ]
  if (ptyCmds.includes(cmd)) {
    if (args) {
      if (args.threadId === undefined) {
        if (args.terminalType === "mini") {
          args.threadId = ""
        } else {
          args.threadId = (window as any).activeThreadId || ""
        }
      }
    }
  }

  if (isBrowser()) {
    return new Promise<T>((resolve, reject) => {
      const id = Math.random().toString(36).substring(2, 15);
      pendingInvokes.set(id, { resolve, reject });
      sendWsMessage({ type: 'invoke', id, cmd, args }).catch((err) => {
        pendingInvokes.delete(id);
        console.warn(`[Tauri WS Bridge] Send failed, falling back to mock: ${cmd}`, err);
        mockInvoke<T>(cmd, args).then(resolve).catch(reject);
      });
    });
  }
  return tauriInvoke<T>(cmd, args)
}

export async function listen<T>(event: string, handler: EventCallback<T>): Promise<UnlistenFn> {
  if (isBrowser()) {
    let handlers = eventListeners.get(event);
    if (!handlers) {
      handlers = new Set();
      eventListeners.set(event, handlers);
    }
    handlers.add(handler);

    sendWsMessage({ type: 'listen', event }).catch((err) => {
      console.warn('[Tauri WS Bridge] Failed to register listener on host:', err);
    });

    return () => {
      const currentHandlers = eventListeners.get(event);
      if (currentHandlers) {
        currentHandlers.delete(handler);
        if (currentHandlers.size === 0) {
          eventListeners.delete(event);
        }
      }
    };
  }
  return tauriListen<T>(event, handler)
}

const mockAppWindow = {
  hide: async () => console.log('[Mock Tauri] appWindow.hide()'),
  show: async () => console.log('[Mock Tauri] appWindow.show()'),
  close: async () => console.log('[Mock Tauri] appWindow.close()'),
  setSize: async (size: any) => console.log('[Mock Tauri] appWindow.setSize()', size),
  setPosition: async (position: any) => console.log('[Mock Tauri] appWindow.setPosition()', position),
  center: async () => console.log('[Mock Tauri] appWindow.center()'),
  innerPosition: async () => ({ x: 0, y: 0 }),
  outerPosition: async () => ({ x: 0, y: 0 }),
  innerSize: async () => ({ width: 800, height: 600 }),
  outerSize: async () => ({ width: 800, height: 600 }),
  setFocus: async () => console.log('[Mock Tauri] appWindow.setFocus()'),
  isFocused: async () => true,
  onResized: async (_cb: any) => { console.log('[Mock Tauri] appWindow.onResized()'); return () => {}; },
  onMoved: async (_cb: any) => { console.log('[Mock Tauri] appWindow.onMoved()'); return () => {}; },
};

export const appWindow = new Proxy(tauriAppWindow || {}, {
  get(target, prop) {
    if (isBrowser()) {
      const val = (mockAppWindow as any)[prop];
      return typeof val === 'function' ? val.bind(mockAppWindow) : val;
    }
    const val = (target as any)[prop];
    return typeof val === 'function' ? val.bind(target) : val;
  }
}) as any;

export async function open(path: string, withApp?: string): Promise<void> {
    if (isBrowser()) {
        return new Promise<void>((resolve, reject) => {
          const id = Math.random().toString(36).substring(2, 15);
          pendingInvokes.set(id, { resolve, reject });
          sendWsMessage({ type: 'open', id, path, withApp }).catch((err) => {
            pendingInvokes.delete(id);
            console.warn(`[Tauri WS Bridge] Open failed to send to host, ignoring: ${path}`, err);
            resolve();
          });
        });
    }
    return tauriOpen(path, withApp)
}

export { PhysicalSize, PhysicalPosition }

async function mockInvoke<T>(cmd: string, _args?: any): Promise<T> {
  switch (cmd) {
    case 'get_project_threads':
    case 'get_all_agy_threads':
    case 'search_project_threads':
      return [] as any as T
    case 'file_exists':
      return true as any as T
    case 'read_thread_log':
      return "Mock thread log content" as any as T
    case 'is_engine_running':
      return true as any as T
    case 'spawn_fresh_engine':
    case 'start_existing_session':
      return { shell_pid: 12345, is_new_session: true } as any as T
    case 'get_browser_context':
      return { url: 'http://localhost:3000', title: 'Mock Page' } as any as T
    case 'select_directory':
      return "/mock/selected/directory" as any as T
    case 'create_new_project':
      return "/mock/new/project" as any as T
    case 'load_prompt_draft':
      return "" as any as T
    case 'get_initial_project':
      return "" as any as T
    case 'get_config':
      return "{}" as any as T
    case 'get_quota':
      return '{"Models": []}' as any as T
    default:
      console.warn(`[Mock Tauri] Unhandled invoke: ${cmd}`)
      return {} as T
  }
}
