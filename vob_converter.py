import os, sys, shutil, subprocess, json, urllib.request, zipfile, re, platform
from pathlib import Path

# Configuration
BASE_DIR = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent
FFMPEG_BIN = BASE_DIR / "ffmpeg" / "ffmpeg.exe"
SETTINGS_FILE = BASE_DIR / "settings.json"

def get_ffmpeg():
    """Finds or downloads FFmpeg (Cross-Platform)."""
    system = platform.system().lower()
    
    # 1. Check local/system
    if shutil.which("ffmpeg"): return "ffmpeg"
    
    local_bin = BASE_DIR / "ffmpeg" / ("ffmpeg.exe" if system == "windows" else "ffmpeg")
    if local_bin.exists(): return str(local_bin)
    
    # 2. Download correct version
    print(f"FFmpeg not found. Downloading for {system.capitalize()}...")
    local_bin.parent.mkdir(parents=True, exist_ok=True)
    
    urls = {
        "windows": ("https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip", "zip"),
        "linux": ("https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz", "tar"),
        "darwin": ("https://evermeet.cx/ffmpeg/getrelease/zip", "zip") # MacOS
    }
    
    if system not in urls: 
        return print(f"Error: Auto-download not supported for {system}. Install FFmpeg manually.") or "ffmpeg"

    url, mode = urls[system]
    dl_path = BASE_DIR / "ffmpeg_dl"
    
    try:
        # Note: ~100MB is normal for a static binary containing all codecs (NVENC, x264, AAC, etc.)
        urllib.request.urlretrieve(url, dl_path, 
            lambda b, s, t: print(f"\rDownloading: {b*s*100/t:.1f}%", end="") if t else None)
        print("\nExtracting...")

        if mode == "zip":
            with zipfile.ZipFile(dl_path) as z:
                # Find the executable inside the zip (it varies by repo)
                exe = next(n for n in z.namelist() if n.lower().endswith("ffmpeg.exe") or n.lower().endswith("ffmpeg"))
                with z.open(exe) as f_in, open(local_bin, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
        elif mode == "tar":
            import tarfile
            with tarfile.open(dl_path, "r:xz") as t:
                # Find member with name ending in 'ffmpeg'
                mem = next(m for m in t.getmembers() if m.name.endswith("/ffmpeg"))
                f_in = t.extractfile(mem)
                with open(local_bin, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)

        # Make executable on Unix
        if system != "windows": 
            os.chmod(local_bin, 0o755)

    except Exception as e:
        print(f"\nError installing FFmpeg: {e}")
        return "ffmpeg"
    finally:
        if dl_path.exists(): os.remove(dl_path)
            
    return str(local_bin)

def convert(path_str, use_nvidia):
    """Main conversion logic."""
    target = Path(path_str)
    if not target.exists(): return print(f"Error: {target} does not exist.")
    
    ffmpeg_cmd = get_ffmpeg()
    hw_args = ["-hwaccel", "cuda"] if use_nvidia else []
    vid_args = ["-c:v", "h264_nvenc", "-vf", "yadif_cuda=1"] if use_nvidia else ["-c:v", "libx264", "-vf", "yadif=1"]
    
    # Gather files
    files = [target] if target.is_file() else [f for f in target.iterdir() if f.suffix.lower() == '.vob']
    files = [f for f in files if "VIDEO_TS" not in f.name.upper()]
    if not files: return print("No valid VOB files found.")

    # Group by Title Set (e.g. VTS_01_1.VOB -> VTS_01)
    groups = {}
    for f in files:
        match = re.match(r"(VTS_\d+)_", f.name, re.IGNORECASE)
        key = match.group(1) if match else "SINGLE"
        groups.setdefault(key, []).append(f)

    # Process Groups
    for key, vobs in groups.items():
        vobs.sort()
        out_name = f"{vobs[0].parent.name}_{key}.mp4" if key != "SINGLE" else f"{vobs[0].stem}.mp4"
        input_str = f"concat:{'|'.join(f.name for f in vobs)}"
        
        print(f"Converting Group {key} ({len(vobs)} files) -> {out_name}")
        cmd = [ffmpeg_cmd] + hw_args + ["-i", input_str] + vid_args + ["-c:a", "copy", out_name]
        subprocess.run(cmd, cwd=vobs[0].parent)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Minimalist VOB to MP4 Converter")
    parser.add_argument("path", nargs="?", help="File or Folder path")
    parser.add_argument("--nvidia", action="store_true", help="Use Nvidia NVENC")
    parser.add_argument("--cpu", action="store_true", help="Force CPU")
    args = parser.parse_args()

    # Load Settings
    settings = {"nvidia": False}
    if SETTINGS_FILE.exists(): settings.update(json.loads(SETTINGS_FILE.read_text()))
    
    if args.nvidia: settings["nvidia"] = True
    if args.cpu: settings["nvidia"] = False
    SETTINGS_FILE.write_text(json.dumps(settings))

    # Interactive Fallback
    final_path = args.path
    if not final_path:
        print(f"--- Simple VOB Converter (GPU: {'ON' if settings['nvidia'] else 'OFF'}) ---")
        final_path = input("Enter Path (or drag folder here): ").strip('"')
    
    if final_path:
        convert(final_path, settings["nvidia"])
