#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_PATH="/Applications/AIOSURLRouter.app"

rm -rf "$APP_PATH"
osacompile -o "$APP_PATH" "$SCRIPT_DIR/router.applescript"

PLIST="$APP_PATH/Contents/Info.plist"

# Add HTTP and HTTPS URL Schemes & Role
plutil -insert CFBundleURLTypes -xml '
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
</array>' "$PLIST"

# Add Document Types for HTML files so macOS recognizes it as a browser app
plutil -insert CFBundleDocumentTypes -xml '
<array>
  <dict>
    <key>CFBundleTypeName</key>
    <string>HTML Document</string>
    <key>CFBundleTypeRole</key>
    <string>Viewer</string>
    <key>LSItemContentTypes</key>
    <array>
      <string>public.html</string>
      <string>public.xhtml</string>
    </array>
  </dict>
</array>' "$PLIST"

# Re-sign app bundle
codesign --force --deep --sign - "$APP_PATH"

# Force register with LaunchServices
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f -r -ui "$APP_PATH"
killall SystemSettings 2>/dev/null || true

echo "Successfully built, configured, and registered AIOSURLRouter.app at $APP_PATH"
