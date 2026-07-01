import os
import json

SCRIPTS_PATH     = "artifacts/generated-scripts/scripts.json"
VOICE_PATH       = "artifacts/generated-voice/voice_metadata.json"
VIDEO_PATH       = "artifacts/generated-videos/kling_videos_metadata.json"
SFX_PATH         = "artifacts/sfx-captions/elevenlabs_sfx_metadata.json"
CAPTIONS_PATH    = "artifacts/sfx-captions/captions_metadata.json"
THUMBNAILS_PATH  = "artifacts/thumbnails/ideogram_thumbnails_metadata.json"
PEXELS_PATH      = "artifacts/stock-footage/pexels_metadata.json"

def find_file(original_path):
    if not original_path:
        return None
    if os.path.exists(original_path):
        return original_path
    if original_path.startswith("output/"):
        rel = original_path[len("output/"):]
        if os.path.exists("artifacts"):
            for artifact_dir in os.listdir("artifacts"):
                candidate = os.path.join("artifacts", artifact_dir, rel)
                if os.path.exists(candidate):
                    return candidate
    return None

def assemble_with_ffmpeg(script_id, title, voice_file, video_file, broll_files, output_path):
    import subprocess

    # Use Pexels b-roll as primary video if Kling video is unavailable
    primary_video = video_file
    if not primary_video and broll_files:
        primary_video = broll_files[0]
        print(f"  No Kling video — using Pexels stock footage as primary: {primary_video}")

    if not voice_file or not primary_video:
        print(f"  Skipping script {script_id}: missing voice={voice_file}, video={primary_video}")
        return None

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-i", primary_video, "-i", voice_file,
        "-c:v", "libx264", "-c:a", "aac", "-shortest",
        "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        size_mb = os.path.getsize(output_path) / 1024 / 1024
        print(f"  Assembled: {output_path} ({size_mb:.1f} MB)")
        return output_path
    else:
        print(f"  ffmpeg failed for script {script_id}:")
        print(f"  {result.stderr[-500:]}")
        return None

def main():
    print("=== Files in artifacts/ ===")
    for root, dirs, files in os.walk("artifacts"):
        for fname in files:
            fpath = os.path.join(root, fname)
            size_kb = os.path.getsize(fpath) / 1024
            print(f"  {fpath} ({size_kb:.0f} KB)")
    print()

    try:
        with open(SCRIPTS_PATH) as f:
            scripts = json.load(f)
        print(f"Loaded {len(scripts)} scripts")
    except FileNotFoundError:
        print(f"Scripts not found at {SCRIPTS_PATH}")
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
            found = sum(1 for v in result.values() if v)
            print(f"  {path}: {found}/{len(result)} files found")
            return result
        except Exception as e:
            print(f"  Could not load {path}: {e}")
            return {}

    voice_map   = load_meta(VOICE_PATH)
    video_map   = load_meta(VIDEO_PATH)
    sfx_map     = load_meta(SFX_PATH)
    thumb_map   = load_meta(THUMBNAILS_PATH)

    # Load Pexels b-roll (actual video files — our primary fallback)
    pexels_data = {}
    try:
        with open(PEXELS_PATH) as f:
            pexels_raw = json.load(f)
        for item in pexels_raw:
            vids = [find_file(v["file"]) for v in item.get("videos", []) if v.get("file")]
            pexels_data[str(item["id"])] = [v for v in vids if v]
        total_pexels = sum(len(v) for v in pexels_data.values())
        print(f"  Pexels: {total_pexels} video files available across {len(pexels_data)} scripts")
    except Exception as e:
        print(f"  Could not load Pexels: {e}")

    os.makedirs("output/final_videos", exist_ok=True)
    final_metadata = []
    assembled_count = 0

    for s in scripts:
        sid = str(s["id"])
        voice_file = voice_map.get(sid)
        video_file = video_map.get(sid)
        broll = pexels_data.get(sid, [])

        print(f"\nScript {s['id']}: {s['title']}")
        print(f"  voice={voice_file}, kling_video={video_file}, pexels_clips={len(broll)}")

        output_path = f"output/final_videos/spark_of_ai_{s['id']}.mp4"
        assembled = assemble_with_ffmpeg(
            s["id"], s["title"],
            voice_file, video_file, broll,
            output_path
        )
        if assembled:
            assembled_count += 1

        final_metadata.append({
            "id": s["id"],
            "title": s["title"],
            "final_video": assembled,
            "thumbnail": thumb_map.get(sid),
            "status": "assembled" if assembled else "skipped"
        })

    with open("output/final_videos/final_metadata.json", "w") as f:
        json.dump(final_metadata, f, indent=2)

    print(f"\nDone. {assembled_count}/{len(scripts)} videos assembled.")
    if assembled_count == 0:
        print("No videos assembled — check voice and Pexels logs above.")

if __name__ == "__main__":
    main()
