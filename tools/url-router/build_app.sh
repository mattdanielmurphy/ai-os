#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_PATH="$SCRIPT_DIR/AIOSURLRouter.app"

rm -rf "$APP_PATH"
osacompile -o "$APP_PATH" "$SCRIPT_DIR/router.applescript"

# Update Info.plist to register as URL handler and run as UIElement (background app)
PLIST="$APP_PATH/Contents/Info.plist"

plutil -insert LSUIElement -bool true "$PLIST" 2>/dev/null || plutil -replace LSUIElement -bool true "$PLIST"

# Add HTTP and HTTPS URL Schemes
plutil -insert CFBundleURLTypes -xml '
<array>
  <dict>
    <key>CFBundleURLName</key>
    <string>com.aios.urlrouter</string>
    <key>CFBundleURLSchemes</key>
    <array>
      <string>http</string>
      <string>https</string>
    </array>
  </dict>
</array>' "$PLIST"

# Force register with LaunchServices
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "$APP_PATH"

echo "Successfully built and registered AIOSURLRouter.app at $APP_PATH"
