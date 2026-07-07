import { invoke as tauriInvoke } from '@tauri-apps/api/tauri'
import { listen as tauriListen } from '@tauri-apps/api/event'
import { appWindow as tauriAppWindow, PhysicalSize, PhysicalPosition } from '@tauri-apps/api/window'
import { open as tauriOpen } from '@tauri-apps/api/shell'
import type { EventCallback, UnlistenFn } from '@tauri-apps/api/event'

export const isBrowser = () => typeof window !== 'undefined' && 
  !(window as any).__TAURI_IPC__ && 
  !(window as any).__TAURI_INTERNALS__ && 
  !(window as any).__TAURI__

export async function invoke<T>(cmd: string, args?: any): Promise<T> {
  if (isBrowser()) {
    console.log(`[Mock Tauri] invoke called: ${cmd}`, args)
    return mockInvoke<T>(cmd, args)
  }
  return tauriInvoke<T>(cmd, args)
}

export async function listen<T>(event: string, handler: EventCallback<T>): Promise<UnlistenFn> {
  if (isBrowser()) {
    console.log(`[Mock Tauri] listen called: ${event}`)
    return mockListen(event, handler)
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
        console.log(`[Mock Tauri] open called: ${path}`, withApp)
        return
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

function mockListen<T>(event: string, handler: EventCallback<T>): UnlistenFn {
  if (event === 'pty_output') {
    let count = 0
    const interval = setInterval(() => {
      count++
      handler({
        event,
        id: 1,
        windowLabel: 'main',
        payload: {
          data: `\x1b[34m[Mock Terminal]\x1b[0m Generating sample log line ${count}...\r\n`,
          project_path: "/mock/path",
          terminal_type: "engine" 
        } as any
      } as any)
    }, 2000)
    return () => clearInterval(interval)
  }
  
  if (event === 'engine_status') {
    handler({
        event,
        id: 2,
        windowLabel: 'main',
        payload: { project_path: "/mock/path", status: 'Running' } as any
    } as any)
  }

  return () => {}
}
