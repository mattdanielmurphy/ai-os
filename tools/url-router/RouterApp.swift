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
            exit(0)
        }

        // STRICT MATCH: Only intercept requests explicitly targeted to our loopback action server port (8643)
        // AND containing known action endpoints (e.g. open_zed, set_delegation).
        let isLocalAction = urlString.hasPrefix("http://127.0.0.1:8643/") || urlString.hasPrefix("http://localhost:8643/")

        if isLocalAction {
            let task = Process()
            task.executableURL = URL(fileURLWithPath: "/usr/bin/curl")
            task.arguments = ["-s", urlString]
            try? task.run()
            task.waitUntilExit()
            exit(0)
        } else {
            // Unmatched external URL -> Pass along directly to Chrome without intercepting
            var targetURLString = urlString
            if !targetURLString.lowercased().hasPrefix("http://") && !targetURLString.lowercased().hasPrefix("https://") {
                targetURLString = "https://" + targetURLString
            }
            
            guard let finalURL = URL(string: targetURLString) else {
                exit(0)
            }
            
            if let chromeURL = NSWorkspace.shared.urlForApplication(withBundleIdentifier: "com.google.Chrome") {
                let configuration = NSWorkspace.OpenConfiguration()
                configuration.activates = true
                NSWorkspace.shared.open([finalURL], withApplicationAt: chromeURL, configuration: configuration) { _, _ in
                    exit(0)
                }
            } else {
                NSWorkspace.shared.open(finalURL)
                exit(0)
            }
        }
    }
}

let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.run()
