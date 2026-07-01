import os
import json

# CapCut does not have a public API — this script assembles a project manifest
# that describes the video edit, which can be imported into CapCut or used with ffmpeg.

# Artifact paths (download-artifact@v3 with no name, path: artifacts/)
SCRIPTS_PATH     = "artifacts/generated-scripts/scripts.json"
VOICE_PATH       = "artifacts/generated-voice/voice_metadata.json"
VIDEO_PATH       = "artifacts/generated-videos/kling_videos_metadata.json"
SFX_PATH         = "artifacts/sfx-captions/elevenlabs_sfx_metadata.json"
CAPTIONS_PATH    = "artifacts/sfx-captions/captions_metadata.json"
THUMBNAILS_PATH  = "artifacts/thumbnails/ideogram_thumbnails_metadata.json"
PEXELS_PATH      = "artifacts/stock-footage/pexels_metadata.json"

def build_edit_manifest(script_id, title, voice_file, video_file, broll_files, sfx_file, caption_file, thumbnail_file):
    return {
        "project_name": f"spark_of_ai_{script_id}_{title.lower().replace(' ', '_')}",
        "duration": 60,
        "aspect_ratio": "9:16",
        "resolution": "1080x1920",
        "tracks": {
            "video": {
                "primary": video_file,
                "broll": broll_files,
                "transition": "cut"
            },
            "audio": {
                "voiceover": voice_file,
                "sfx": sfx_file,
                "music": None
            },
            "captions": caption_file,
            "thumbnail": thumbnail_file
        },
        "export_settings": {
            "format": "mp4",
            "quality": "1080p",
            "fps": 30,
            "bitrate": "8000k"
        }
    }

def assemble_with_ffmpeg(manifest, output_path):
    """Fallback: use ffmpeg to assemble video if CapCut API unavailable."""
    import subprocess

    voice = manifest["tracks"]["audio"]["voiceover"]
    video = manifest["tracks"]["video"]["primary"]

    if not voice or not video:
        print(f"⚠️  Missing voice or video for {manifest['project_name']} — skipping assembly")
        return None

    if not os.path.exists(voice):
        print(f"⚠️  Voice file not found: {voice} — skipping assembly")
        return None

    if not os.path.exists(video):
        print(f"⚠️  Video file not found: {video} — skipping assembly")
        return None

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-i", video,
        "-i", voice,
        "-c:v", "libx264",
        "-c:a", "aac",
        "-shortest",
        "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ Video assembled: {output_path}")
        return output_path
    else:
        print(f"❌ ffmpeg failed: {result.stderr[-500:]}")
        return None

def main():
    try:
        with open(SCRIPTS_PATH) as f:
            scripts = json.load(f)
        print(f"✅ Loaded {len(scripts)} scripts from {SCRIPTS_PATH}")
    except FileNotFoundError:
        print(f"❌ Scripts file not found at {SCRIPTS_PATH}")
        print("Available files in artifacts/:")
        for root, dirs, files in os.walk("artifacts"):
            for fname in files:
                print(f"  {os.path.join(root, fname)}")
        exit(1)

    def load_meta(path, key="file"):
        try:
            with open(path) as f:
                data = json.load(f)
            print(f"✅ Loaded metadata from {path}")
            return {str(item.get("id")): item.get(key) for item in data}
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
            pexels_data = {str(item["id"]): [v["file"] for v in item.get("videos", [])] for item in json.load(f)}
        print(f"✅ Loaded pexels metadata from {PEXELS_PATH}")
    except Exception as e:
        print(f"⚠️  Could not load pexels metadata: {e}")
        pexels_data = {}

    os.makedirs("output/final_videos", exist_ok=True)
    final_metadata = []

    for s in scripts:
        sid = str(s["id"])
        manifest = build_edit_manifest(
            s["id"], s["title"],
            voice_map.get(sid), video_map.get(sid),
            pexels_data.get(sid, []),
            sfx_map.get(sid), caption_map.get(sid),
            thumb_map.get(sid)
        )

        manifest_file = f"output/final_videos/manifest_script_{s['id']}.json"
        with open(manifest_file, "w") as f:
            json.dump(manifest, f, indent=2)

        output_path = f"output/final_videos/spark_of_ai_{s['id']}.mp4"
        assembled = assemble_with_ffmpeg(manifest, output_path)

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
    print(f"✅ Final edit manifests saved. {sum(1 for m in final_metadata if m['status'] == 'assembled')} videos assembled.")

if __name__ == "__main__":
    main()
