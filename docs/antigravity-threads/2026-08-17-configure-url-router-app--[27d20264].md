---
title: "Configure URL Router App"
date: "2026-08-17"
conversation_id: "27d20264-e327-4d23-b4e4-6483ee352179"
source: "antigravity"
---

# Configure URL Router App

## User

Please overwrite the following two files with the exact specified content:

File 1: `/Users/matt/projects/ai-os/tools/url-router/RouterApp.swift`
```swift
import AppKit

class AppDelegate: NSObject, NSApplicationDelegate {
    func applicationWillFinishLaunching(_ notification: Notification) {
        NSAppleEventManager.shared().setEventHandler(
            self,
            andSelector: #selector(handleGetURL(_:withReplyEvent:)),
            forEventClass: AEEventClass(kInternetEventClass),
            andEventID: AEEventID(kAEGetURL)
        )
    }

    private func openInRealBrowser(urls: [URL]) {
        guard !urls.isEmpty else {
            exit(0)
        }

        if let chromeURL = NSWorkspace.shared.urlForApplication(withBundleIdentifier: "com.google.Chrome") {
            let configuration = NSWorkspace.OpenConfiguration()
            configuration.activates = true
            NSWorkspace.shared.open(urls, withApplicationAt: chromeURL, configuration: configuration) { _, _ in
                exit(0)
            }
        } else {
            for url in urls {
                NSWorkspace.shared.open(url)
            }
            exit(0)
        }
    }

    func application(_ sender: NSApplication, openFiles filenames: [String]) {
        let urls = filenames.map { URL(fileURLWithPath: $0) }
        openInRealBrowser(urls: urls)
    }

    func application(_ sender: NSApplication, openFile filename: String) -> Bool {
        let url = URL(fileURLWithPath: filename)
        openInRealBrowser(urls: [url])
        return true
    }

    func application(_ application: NSApplication, open urls: [URL]) {
        openInRealBrowser(urls: urls)
    }

    @objc func handleGetURL(_ event: NSAppleEventDescriptor, withReplyEvent replyEvent: NSAppleEventDescriptor) {
        guard let urlString = event.paramDescriptor(forKeyword: keyDirectObject)?.stringValue else {
            exit(0)
        }

        let isLocalAction = urlString.hasPrefix("http://127.0.0.1:8643/") || urlString.hasPrefix("http
<truncated 2768 bytes>
/matt/projects/ai-os/tools/url-router/RouterApp.swift -o "$APP_PATH/Contents/MacOS/AIOSURLRouter"

cat << 'PLISTEOF' > "$APP_PATH/Contents/Info.plist"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>CFBundleDevelopmentRegion</key>
	<string>en</string>
	<key>CFBundleExecutable</key>
	<string>AIOSURLRouter</string>
	<key>CFBundleIdentifier</key>
	<string>com.aios.urlrouter</string>
	<key>CFBundleInfoDictionaryVersion</key>
	<string>6.0</string>
	<key>CFBundleName</key>
	<string>AIOSURLRouter</string>
	<key>LSUIElement</key>
	<true/>
	<key>CFBundlePackageType</key>
	<string>APPL</string>
	<key>CFBundleShortVersionString</key>
	<string>1.0</string>
	<key>CFBundleURLTypes</key>
	<array>
		<dict>
			<key>CFBundleURLName</key>
			<string>Web site URL</string>
			<key>CFBundleURLRole</key>
			<string>Viewer</string>
			<key>CFBundleURLSchemes</key>
			<array>
				<string>http</string>
				<string>https</string>
			</array>
		</dict>
	</array>
	<key>CFBundleDocumentTypes</key>
	<array>
		<dict>
			<key>CFBundleTypeName</key>
			<string>HTML Document</string>
			<key>CFBundleTypeRole</key>
			<string>Viewer</string>
			<key>LSHandlerRank</key>
			<string>Alternate</string>
			<key>CFBundleTypeExtensions</key>
			<array>
				<string>html</string>
				<string>htm</string>
				<string>shtml</string>
				<string>xhtml</string>
			</array>
			<key>LSItemContentTypes</key>
			<array>
				<string>public.html</string>
				<string>public.xhtml</string>
			</array>
		</dict>
	</array>
	<key>NSPrincipalClass</key>
	<string>NSApplication</string>
</dict>
</plist>
PLISTEOF

codesign --force --deep --sign - "$APP_PATH"
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "$APP_PATH"

echo "Swift App Bundle built & registered successfully!"
```

---
