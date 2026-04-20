# File Organizer

Auto-sorts a folder's files into category subfolders (Images, Documents, Videos, Audio, Archives, Code, etc.). Comes in three flavors:

- **CLI** — `organize.py`, pure Python, zero dependencies
- **HTTP API** — `backend/server.py`, stdlib-only Python server
- **Web UI** — React + TypeScript (Vite) frontend that talks to the API

## Requirements

- Python 3.10+
- Node.js 18+ and npm (only for the web UI)

## 1. CLI usage

No install needed — just run it.

```bash
# Preview what would happen (safe, nothing moves):
python3 organize.py --dry-run

# Organize ~/Downloads:
python3 organize.py

# Organize a specific folder:
python3 organize.py -p ~/Desktop

# Keep watching and auto-sort new files every 5 seconds:
python3 organize.py --watch

# Custom interval (10 seconds):
python3 organize.py --watch -i 10

# See all options:
python3 organize.py --help
```

## 2. Web UI

The web UI needs **two processes running at the same time**: the Python backend and the React dev server.

### First-time setup

Install the frontend dependencies:

```bash
cd frontend
npm install
cd ..
```

### Running

Open **two terminals**.

**Terminal 1 — Backend API (port 5174):**

```bash
cd "/path/to/File Organizer"
python3 backend/server.py
```

**Terminal 2 — Frontend dev server (port 5173):**

```bash
cd "/path/to/File Organizer/frontend"
npm run dev
```

Then open http://localhost:5173 in your browser.

### How to use the UI

1. Enter a folder path in the **Folder** field (defaults to `~/Downloads`).
2. Click **Preview** — shows a table of files with destination categories. Nothing is moved.
3. Click **Organize N** — confirms, then actually moves the files into category subfolders.

The "Organize" button is only enabled after a successful preview, so you always see what will happen before anything moves.

### Production build

```bash
cd frontend
npm run build
npm run preview   # serves dist/ locally for verification
```

The backend must still be running for the built frontend to work.

## 3. Desktop app (Linux) — one click, no terminal

Install once:

```bash
cd "/path/to/File Organizer"
cd frontend && npm install && npm run build && cd ..
./install-launcher.sh
```

Then find **File Organizer** in your application menu. Clicking it starts the backend (which serves the built frontend) and opens your browser to the UI. Closing the browser tab doesn't stop it — the backend keeps running until you kill the process or reboot. To stop it: `pkill -f "backend/server.py"`.

To uninstall:

```bash
rm ~/.local/share/applications/file-organizer.desktop
rm ~/.local/share/icons/hicolor/scalable/apps/file-organizer.svg
```

## Categories

Files are sorted by extension:

| Category | Extensions |
|---|---|
| Images | jpg, png, gif, bmp, webp, svg, tiff, ico, heic, raw |
| Videos | mp4, mov, avi, mkv, webm, flv, wmv, m4v, mpg, mpeg |
| Audio | mp3, wav, flac, aac, ogg, m4a, wma, opus |
| Documents | pdf, doc, docx, odt, rtf, txt, md, tex, epub, pages |
| Spreadsheets | xls, xlsx, ods, csv, tsv, numbers |
| Presentations | ppt, pptx, odp, key |
| Archives | zip, tar, gz, bz2, xz, 7z, rar, tgz, tbz2 |
| Code | py, js, ts, jsx, tsx, java, c, cpp, h, hpp, cs, go, rs, rb, php, sh, html, css, scss, json, xml, yml, yaml, sql, toml |
| Executables | exe, msi, deb, rpm, dmg, pkg, appimage, apk |
| Fonts | ttf, otf, woff, woff2 |
| Torrents | torrent |
| Other | everything else |

## Notes

- Subdirectories and hidden files (starting with `.`) are skipped — existing category folders aren't touched.
- Name collisions are handled automatically by appending ` (1)`, ` (2)`, etc.
- The backend binds to `127.0.0.1:5174` (localhost only — not exposed to your network).
