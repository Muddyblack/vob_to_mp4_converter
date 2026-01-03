# VOB_to_MP4_converter

This project helps converting your old DVD's into MP4 to preserve your treasures.

## Usage

### Simple Usage
1. Run the script (or the executable):
   ```bash
   python vob_converter.py
   ```
2. **Drag and drop** your file or folder into the window when prompted.
   - Separate VOB files will be converted individually.
   - DVD segments (e.g., `VTS_01_1.VOB`, `VTS_01_2.VOB`) will be automatically merged.

### Advanced (Command Line)
You can passing arguments directly for automation:
```bash
python vob_converter.py "C:\Movies\DVD_Rip" --nvidia
```
*   `--nvidia`: Use GPU acceleration (faster).
*   `--cpu`: Force CPU encoding (better compatibility).

### Features
*   **Auto-Setup**: Automatically downloads the correct FFmpeg (Windows/Linux/MacOS) if missing (~100MB).
*   **Smart Merging**: Auto-detects and joins DVD chapters.
*   **Settings**: Remembers your GPU preference in `settings.json`.

### Requirements
*   Python 3.x (if running from source)
*   *Or* just the standalone executable.
*   Internet connection (only for the first run to download FFmpeg).
