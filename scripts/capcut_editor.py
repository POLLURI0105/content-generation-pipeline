import os
import json

# CapCut does not have a public API — this script assembles a project manifest
# that describes the video edit, which can be imported into CapCut or used with ffmpeg.

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
        print(f"❌ ffmpeg failed: {result.stderr}")
        return None

def main():
    with open("output/scripts.json") as f:
        scripts = json.load(f)
    
    def load_meta(path, key="file"):
        try:
            with open(path) as f:
                return {str(item.get("id")): item.get(key) for item in json.load(f)}
        except:
            return {}
    
    voice_map = load_meta("output/voice_metadata.json")
    video_map = load_meta("output/kling_videos_metadata.json")
    sfx_map = load_meta("output/elevenlabs_sfx_metadata.json")
    caption_map = load_meta("output/captions_metadata.json")
    thumb_map = load_meta("output/ideogram_thumbnails_metadata.json")
    
    try:
        with open("output/pexels_metadata.json") as f:
            pexels_data = {str(item["id"]): [v["file"] for v in item.get("videos", [])] for item in json.load(f)}
    except:
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
    print("✅ Final edit manifests and videos saved")

if __name__ == "__main__":
    main()
