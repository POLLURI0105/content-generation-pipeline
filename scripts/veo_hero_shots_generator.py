import os
import json
import requests
import time

VEO_API_KEY = os.environ.get("VEO_API_KEY", "")
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "")

HERO_PROMPTS = {
    1: "Cinematic shot of a smartphone screen showing 100 million users connecting globally, neon lights",
    2: "Cinematic aerial view of Dartmouth College in 1956, scientists walking to a historic meeting",
    3: "Cinematic dark laboratory, screens going black one by one, dramatic silence",
    4: "Cinematic close-up of a GPU processing images at lightning speed, heat shimmer effect",
    5: "Cinematic birds-eye view of mathematical equations floating in 3D space, transforming into AI",
    6: "Cinematic typewriter keys moving by themselves, words appearing on a glowing screen",
    7: "Cinematic paint splashing in slow motion, forming a digital portrait, AI aesthetic",
    8: "Cinematic two skyscrapers facing each other at night, lightning between them, tech battle"
}

def generate_hero_shot(script_id, prompt):
    if not VEO_API_KEY and not PROJECT_ID:
        print(f"⚠️  No Veo credentials — skipping hero shot for script {script_id}")
        return {"id": script_id, "file": None, "status": "skipped"}
    
    # Google Veo 3.1 via Vertex AI
    url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/us-central1/publishers/google/models/veo-3.1:generateVideo"
    headers = {
        "Authorization": f"Bearer {VEO_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "aspectRatio": "9:16",
            "durationSeconds": 6,
            "sampleCount": 1
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"❌ Veo failed for script {script_id}: {response.text}")
        return {"id": script_id, "file": None, "status": "failed"}
    
    operation_name = response.json().get("name")
    print(f"⏳ Veo operation {operation_name} started")
    
    for _ in range(20):
        time.sleep(15)
        op_url = f"https://us-central1-aiplatform.googleapis.com/v1/{operation_name}"
        op_resp = requests.get(op_url, headers=headers).json()
        if op_resp.get("done"):
            video_b64 = op_resp.get("response", {}).get("predictions", [{}])[0].get("bytesBase64Encoded")
            if video_b64:
                import base64
                os.makedirs("output/hero_shots", exist_ok=True)
                filename = f"output/hero_shots/veo_script_{script_id}.mp4"
                with open(filename, "wb") as f:
                    f.write(base64.b64decode(video_b64))
                print(f"✅ Veo hero shot saved: {filename}")
                return {"id": script_id, "file": filename, "status": "success"}
    
    return {"id": script_id, "file": None, "status": "timeout"}

def main():
    with open("output/scripts.json") as f:
        scripts = json.load(f)
    
    metadata = []
    for s in scripts:
        prompt = HERO_PROMPTS.get(s["id"], f"Cinematic hero shot for AI history video: {s['title']}")
        result = generate_hero_shot(s["id"], prompt)
        metadata.append(result)
    
    with open("output/veo_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    print("✅ Veo hero shots metadata saved")

if __name__ == "__main__":
    main()
