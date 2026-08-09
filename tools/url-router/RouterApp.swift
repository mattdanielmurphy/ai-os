import AppKit

class AppDelegate: NSObject, NSApplicationDelegate {
    func applicationDidFinishLaunching(_ notification: Notification) {
        NSAppleEventManager.shared().setEventHandler(
            self,
            andSelector: #selector(handleGetURL(_:withReplyEvent:)),
            forEventClass: AEEventClass(kInternetEventClass),
            andEventID: AEEventID(kAEGetURL)
        )
    }

    @objc func handleGetURL(_ event: NSAppleEventDescriptor, withReplyEvent replyEvent: NSAppleEventDescriptor) {
        guard let urlString = event.paramDescriptor(forKeyword: keyDirectObject)?.stringValue else {
            NSApp.terminate(nil)
            return
        }

        // Check if URL matches our local listener target
        if urlString.hasPrefix("http://127.0.0.1:8643") || urlString.hasPrefix("http://localhost:8643") {
            let task = Process()
            task.executableURL = URL(fileURLWithPath: "/usr/bin/curl")
            task.arguments = ["-s", urlString]
            
            // Wait for curl task to complete synchronously before terminating app
            try? task.run()
            task.waitUntilExit()
            NSApp.terminate(nil)
        } else {
            var targetURLString = urlString
            if !targetURLString.lowercased().hasPrefix("http://") && !targetURLString.lowercased().hasPrefix("https://") {
                targetURLString = "https://" + targetURLString
            }
            
            guard let finalURL = URL(string: targetURLString) else {
                NSApp.terminate(nil)
                return
            }
            
            // Forward all non-ai-os links to Google Chrome
            if let chromeURL = NSWorkspace.shared.urlForApplication(withBundleIdentifier: "com.google.Chrome") {
                let configuration = NSWorkspace.OpenConfiguration()
                configuration.activates = true
                NSWorkspace.shared.open([finalURL], withApplicationAt: chromeURL, configuration: configuration) { _, _ in
                    DispatchQueue.main.async {
                        NSApp.terminate(nil)
                    }
                }
            } else {
                NSWorkspace.shared.open(finalURL)
                NSApp.terminate(nil)
            }
        }
    }
}

let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.run()
