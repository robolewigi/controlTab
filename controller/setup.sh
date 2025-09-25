#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

APP_NAME="Controller ConTab"
EXEC_PATH="$SCRIPT_DIR/controllerConTab"
ICON_PATH="$SCRIPT_DIR/main.png"
DESKTOP_FILE="$HOME/.local/share/applications/controllerConTab.desktop"

echo "[1/3] Installing on gnome terminal and its dependencies..."
echo "if not working then on terminal './controllerConTab' at location"
sudo apt update
sudo apt install -y libsdl2-2.0-0 libsdl2-dev libsdl2-image-2.0-0 libsdl2-image-dev x11-utils gnome-terminal

echo "[2/3] Preparing executable..."
chmod +x "$EXEC_PATH"

echo "[3/3] Creating desktop entry..."
mkdir -p "$(dirname "$DESKTOP_FILE")"
cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Name=$APP_NAME
Exec=gnome-terminal -- bash -c '"$SCRIPT_DIR/controllerConTab"; exec bash'
Icon=$ICON_PATH
Type=Application
Terminal=true
Categories=Utility;
EOF

chmod +x "$DESKTOP_FILE"
update-desktop-database "$(dirname "$DESKTOP_FILE")" || true

echo "✅ Setup complete. '$APP_NAME' will now open in GNOME Terminal."
