import os
import json
import requests
import re

ELEVENLABS_API_KEY = os.environ["ELEVENLABS_API_KEY"]
VOICE_ID = os.environ["ELEVENLABS_VOICE_ID"]
MODEL_ID = os.environ.get("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")

def extract_emotion_tags(script):
    emotions = re.findall(r'<!--\s*emotion:\s*(\w+)\s*-->', script)
    return emotions[0] if emotions else "fluent"

def clean_script(script):
    return re.sub(r'<!--.*?-->', '', script).strip()

def generate_voice(script_id, title, script_text):
    emotion = extract_emotion_tags(script_text)
    clean_text = clean_script(script_text)
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": clean_text,
        "model_id": MODEL_ID,
        "voice_settings": {
            "stability": 0.4,
            "similarity_boost": 0.85,
            "style": 0.6,
            "use_speaker_boost": True
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        os.makedirs("output/voice", exist_ok=True)
        filename = f"output/voice/script_{script_id}.mp3"
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"✅ Voice generated: {filename}")
        return {"id": script_id, "title": title, "file": filename, "emotion": emotion, "status": "success"}
    else:
        print(f"❌ Voice failed for script {script_id}: {response.text}")
        return {"id": script_id, "title": title, "file": None, "emotion": emotion, "status": "failed", "error": response.text}

def main():
    with open("output/scripts.json") as f:
        scripts = json.load(f)
    
    metadata = []
    for s in scripts:
        result = generate_voice(s["id"], s["title"], s["script"])
        metadata.append(result)
    
    with open("output/voice_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"✅ Voice metadata saved")

if __name__ == "__main__":
    main()
