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
        defer {
            NSApp.terminate(nil)
        }
        
        guard let urlString = event.paramDescriptor(forKeyword: keyDirectObject)?.stringValue else { return }

        // Check if URL matches our local listener target
        if urlString.hasPrefix("http://127.0.0.1:8643") || urlString.hasPrefix("http://localhost:8643") {
            let task = Process()
            task.executableURL = URL(fileURLWithPath: "/usr/bin/curl")
            task.arguments = ["-s", urlString]
            try? task.run()
        } else {
            // Guarantee valid URL object with fallback scheme if missing (e.g. google.com -> https://google.com)
            var targetURLString = urlString
            if !targetURLString.lowercased().hasPrefix("http://") && !targetURLString.lowercased().hasPrefix("https://") {
                targetURLString = "https://" + targetURLString
            }
            
            guard let finalURL = URL(string: targetURLString) else { return }
            
            // Forward all non-ai-os links to Google Chrome
            if let chromeURL = NSWorkspace.shared.urlForApplication(withBundleIdentifier: "com.google.Chrome") {
                let configuration = NSWorkspace.OpenConfiguration()
                configuration.activates = true
                NSWorkspace.shared.open([finalURL], withApplicationAt: chromeURL, configuration: configuration, completionHandler: nil)
            } else {
                // Fallback to default browser handler if Chrome isn't found
                NSWorkspace.shared.open(finalURL)
            }
        }
    }
}

let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.run()
