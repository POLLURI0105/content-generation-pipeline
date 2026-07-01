import os
import json
import asyncio
import edge_tts

# edge-tts: free Microsoft TTS, no API key needed
# Voice: en-US-GuyNeural (natural male voice)
VOICE = "en-US-GuyNeural"

async def generate_voice(script_id, text, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(output_path)
    size = os.path.getsize(output_path)
    print(f"  Voice saved: {output_path} ({size//1024} KB)")
    return output_path

def main():
    with open("output/scripts.json") as f:
        scripts = json.load(f)

    print(f"Generating voice for {len(scripts)} scripts using edge-tts ({VOICE})...")
    results = []

    for s in scripts:
        script_id = s["id"]
        text = s.get("narration") or s.get("content") or s.get("script") or str(s)
        output_path = f"output/voice/voice_script_{script_id}.mp3"
        try:
            asyncio.run(generate_voice(script_id, text, output_path))
            results.append({"id": script_id, "file": output_path, "status": "success"})
            print(f"  Script {script_id}: OK")
        except Exception as e:
            print(f"  Script {script_id} FAILED: {e}")
            results.append({"id": script_id, "file": None, "status": "failed", "error": str(e)})

    with open("output/voice_metadata.json", "w") as f:
        json.dump(results, f, indent=2)

    success = sum(1 for r in results if r["status"] == "success")
    print(f"Done. {success}/{len(scripts)} voice files generated.")

if __name__ == "__main__":
    main()
