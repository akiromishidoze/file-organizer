#!/usr/bin/env bash
# Install the File Organizer as a clickable desktop app (Linux XDG).
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APPS="$HOME/.local/share/applications"
ICONS="$HOME/.local/share/icons/hicolor/scalable/apps"

mkdir -p "$APPS" "$ICONS"

cat > "$ICONS/file-organizer.svg" <<'SVG'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect x="4" y="12" width="56" height="44" rx="4" fill="#6366f1"/>
  <path d="M4 16a4 4 0 0 1 4-4h16l6 6h26a4 4 0 0 1 4 4v4H4z" fill="#818cf8"/>
  <rect x="12" y="28" width="10" height="10" rx="1" fill="#fbbf24"/>
  <rect x="27" y="28" width="10" height="10" rx="1" fill="#34d399"/>
  <rect x="42" y="28" width="10" height="10" rx="1" fill="#f87171"/>
  <rect x="12" y="42" width="10" height="8" rx="1" fill="#60a5fa"/>
  <rect x="27" y="42" width="10" height="8" rx="1" fill="#c084fc"/>
  <rect x="42" y="42" width="10" height="8" rx="1" fill="#f472b6"/>
</svg>
SVG

cat > "$APPS/file-organizer.desktop" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=File Organizer
GenericName=File Organizer
Comment=Auto-sort folders by file type
Exec="$DIR/launch.sh"
Icon=file-organizer
Terminal=false
Categories=Utility;FileTools;
StartupNotify=true
EOF

chmod +x "$DIR/launch.sh" "$APPS/file-organizer.desktop"
update-desktop-database "$APPS" 2>/dev/null || true

echo "Installed. Look for 'File Organizer' in your app menu."
echo "Desktop entry: $APPS/file-organizer.desktop"
echo "Icon:          $ICONS/file-organizer.svg"
