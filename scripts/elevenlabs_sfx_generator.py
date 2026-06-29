import os
import json
import requests

ELEVENLABS_API_KEY = os.environ["ELEVENLABS_API_KEY"]

SFX_PROMPTS = {
    1: "Dramatic whoosh with digital notification sounds, ascending energy",
    2: "Old typewriter clicking, conference room ambience, historical atmosphere",
    3: "Power down hum, electrical shutdown, eerie silence",
    4: "Electrical surge, data processing beeps, breakthrough energy burst",
    5: "Mathematical data stream, digital transformation sound, ethereal tone",
    6: "Typing sounds accelerating, AI synthesizer hum, futuristic beeps",
    7: "Paintbrush swipe, digital glitch, artistic creation whoosh",
    8: "Epic battle orchestral sting, tech clash, competitive tension"
}

def generate_sfx(script_id, prompt):
    url = "https://api.elevenlabs.io/v1/sound-generation"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": prompt,
        "duration_seconds": 5.0,
        "prompt_influence": 0.4
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        os.makedirs("output/sfx", exist_ok=True)
        filename = f"output/sfx/sfx_script_{script_id}.mp3"
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"✅ SFX saved: {filename}")
        return {"id": script_id, "file": filename, "status": "success"}
    
    print(f"❌ SFX failed for script {script_id}: {response.text}")
    return {"id": script_id, "file": None, "status": "failed"}

def main():
    with open("output/scripts.json") as f:
        scripts = json.load(f)
    
    metadata = []
    for s in scripts:
        prompt = SFX_PROMPTS.get(s["id"], "High energy dramatic sound effect for AI video")
        result = generate_sfx(s["id"], prompt)
        metadata.append(result)
    
    with open("output/elevenlabs_sfx_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    print("✅ ElevenLabs SFX metadata saved")

if __name__ == "__main__":
    main()
