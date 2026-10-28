# FaceFusion macOS Launcher

A native macOS menu-bar app that wraps FaceFusion — no terminal required.

## What It Does

- Lives in your **menu bar** as a 🎭 icon
- **Auto-starts** the FaceFusion Gradio server when you open the app
- **Opens your browser** automatically once the server is ready
- Lets you **stop / restart / open** the server from the menu
- Shows status: ⏳ starting · 🎭 running · ⚠️ error

## Build Requirements

On your Mac, inside the `facefusion` conda environment:

```bash
conda activate facefusion
pip install rumps pyinstaller Pillow
```

## Build the .app

```bash
cd facefusion/launcher
bash build.sh
```

The finished app appears at `launcher/dist/FaceFusion.app`.  
Drag it to your **Applications** folder.

## First Run

1. Double-click **FaceFusion.app**
2. macOS may ask for permission (right-click → Open the first time if Gatekeeper blocks it)
3. The ⏳ icon appears in your menu bar while the server starts
4. Your browser opens automatically to `http://127.0.0.1:7860`

## Menu Items

| Item | Description |
|---|---|
| **Open FaceFusion** | Opens the web UI in your default browser |
| **Status** | Shows current server state |
| **Start Server** | Starts the FaceFusion server (if stopped) |
| **Stop Server** | Stops the server gracefully |
| **Quit** | Stops the server and exits the app |

## Troubleshooting

**App shows ⚠️ on start**  
The `facefusion` conda environment may not be found. Make sure you built FaceFusion using conda (`conda activate facefusion && python install.py default`) before building the launcher.

**Browser doesn't open**  
Click **Open FaceFusion** in the menu bar, or navigate to `http://127.0.0.1:7860` manually.

**Port already in use**  
Edit `SERVER_PORT` at the top of `launcher/app.py`, then rebuild.
