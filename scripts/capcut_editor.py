import os
import json

# With @v4 bulk download to artifacts/, each artifact is in artifacts/<name>/
# The upload was from output/, so files are at artifacts/<name>/<relative-to-output>
SCRIPTS_PATH     = "artifacts/generated-scripts/scripts.json"
VOICE_PATH       = "artifacts/generated-voice/voice_metadata.json"
VIDEO_PATH       = "artifacts/generated-videos/kling_videos_metadata.json"
SFX_PATH         = "artifacts/sfx-captions/elevenlabs_sfx_metadata.json"
CAPTIONS_PATH    = "artifacts/sfx-captions/captions_metadata.json"
THUMBNAILS_PATH  = "artifacts/thumbnails/ideogram_thumbnails_metadata.json"
PEXELS_PATH      = "artifacts/stock-footage/pexels_metadata.json"

def find_file(original_path):
    """
    Media files are saved by generators as output/X/filename.
    After uploading output/ as an artifact and @v4 bulk downloading to artifacts/,
    the file lives at artifacts/<artifact-name>/X/filename.
    We search artifacts/ for the file if it's not at the original path.
    """
    if not original_path:
        return None
    if os.path.exists(original_path):
        return original_path
    # Strip output/ prefix and search across artifact directories
    if original_path.startswith("output/"):
        rel = original_path[len("output/"):]
        if os.path.exists("artifacts"):
            for artifact_dir in os.listdir("artifacts"):
                candidate = os.path.join("artifacts", artifact_dir, rel)
                if os.path.exists(candidate):
                    return candidate
    return None  # File genuinely not found

def build_edit_manifest(script_id, title, voice_file, video_file, broll_files, sfx_file, caption_file, thumbnail_file):
    return {
        "project_name": f"spark_of_ai_{script_id}_{title.lower().replace(' ', '_')}",
        "duration": 60,
        "aspect_ratio": "9:16",
        "resolution": "1080x1920",
        "tracks": {
            "video": {"primary": video_file, "broll": broll_files, "transition": "cut"},
            "audio": {"voiceover": voice_file, "sfx": sfx_file, "music": None},
            "captions": caption_file,
            "thumbnail": thumbnail_file
        },
        "export_settings": {"format": "mp4", "quality": "1080p", "fps": 30, "bitrate": "8000k"}
    }

def assemble_with_ffmpeg(manifest, output_path):
    import subprocess

    voice = manifest["tracks"]["audio"]["voiceover"]
    video = manifest["tracks"]["video"]["primary"]

    if not voice or not video:
        print(f"⚠️  Missing voice or video for {manifest['project_name']} — skipping")
        return None

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-i", video, "-i", voice,
        "-c:v", "libx264", "-c:a", "aac", "-shortest",
        "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ Assembled: {output_path}")
        return output_path
    else:
        print(f"❌ ffmpeg failed: {result.stderr[-300:]}")
        return None

def main():
    print("=== Files in artifacts/ ===")
    for root, dirs, files in os.walk("artifacts"):
        for fname in files:
            print(f"  {os.path.join(root, fname)}")
    print()

    try:
        with open(SCRIPTS_PATH) as f:
            scripts = json.load(f)
        print(f"✅ Loaded {len(scripts)} scripts")
    except FileNotFoundError:
        print(f"❌ Scripts not found at {SCRIPTS_PATH}")
        exit(1)

    def load_meta(path, key="file"):
        try:
            with open(path) as f:
                data = json.load(f)
            result = {}
            for item in data:
                raw = item.get(key)
                resolved = find_file(raw) if raw else None
                result[str(item.get("id"))] = resolved
                if raw and resolved != raw:
                    print(f"  Remapped: {raw} → {resolved}")
            print(f"✅ Loaded {path} ({len(result)} entries, {sum(1 for v in result.values() if v)} files found)")
            return result
        except Exception as e:
            print(f"⚠️  Could not load {path}: {e}")
            return {}

    voice_map    = load_meta(VOICE_PATH)
    video_map    = load_meta(VIDEO_PATH)
    sfx_map      = load_meta(SFX_PATH)
    caption_map  = load_meta(CAPTIONS_PATH)
    thumb_map    = load_meta(THUMBNAILS_PATH)

    try:
        with open(PEXELS_PATH) as f:
            pexels_raw = json.load(f)
        pexels_data = {}
        for item in pexels_raw:
            vids = [find_file(v["file"]) for v in item.get("videos", []) if v.get("file")]
            pexels_data[str(item["id"])] = [v for v in vids if v]
        print(f"✅ Loaded pexels metadata")
    except Exception as e:
        print(f"⚠️  Could not load pexels: {e}")
        pexels_data = {}

    os.makedirs("output/final_videos", exist_ok=True)
    final_metadata = []
    assembled_count = 0

    for s in scripts:
        sid = str(s["id"])
        voice_file = voice_map.get(sid)
        video_file = video_map.get(sid)

        manifest = build_edit_manifest(
            s["id"], s["title"],
            voice_file, video_file,
            pexels_data.get(sid, []),
            sfx_map.get(sid), caption_map.get(sid), thumb_map.get(sid)
        )

        manifest_file = f"output/final_videos/manifest_script_{s['id']}.json"
        with open(manifest_file, "w") as f:
            json.dump(manifest, f, indent=2)

        output_path = f"output/final_videos/spark_of_ai_{s['id']}.mp4"
        assembled = assemble_with_ffmpeg(manifest, output_path)
        if assembled:
            assembled_count += 1

        final_metadata.append({
            "id": s["id"],
            "title": s["title"],
            "manifest": manifest_file,
            "final_video": assembled,
            "thumbnail": thumb_map.get(sid),
            "status": "assembled" if assembled else "manifest_only"
        })

    with open("output/final_videos/final_metadata.json", "w") as f:
        json.dump(final_metadata, f, indent=2)
    print(f"\n✅ Done. {assembled_count}/{len(scripts)} videos assembled.")

if __name__ == "__main__":
    main()
