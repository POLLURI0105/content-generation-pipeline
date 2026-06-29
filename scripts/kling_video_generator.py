import os
import json
import requests
import time

KLING_API_KEY = os.environ["KLING_API_KEY"]
BASE_URL = "https://api.klingai.com/v1"

VIDEO_PROMPTS = {
    1: "Futuristic AI interface with exponential growth graph, glowing blue neural networks, high-energy tech visualization",
    2: "1950s scientists in a conference room with chalkboards, vintage academic setting, black and white to color transition",
    3: "Dark empty research lab, power being cut off, dramatic shadows, abandoned computer terminals",
    4: "Neural network visualization processing millions of images, data streams, breakthrough moment with bright flash",
    5: "Pages of mathematical equations transforming into flowing attention mechanism diagrams, golden light",
    6: "Text appearing on screens as if typed by itself, AI writing poetry and code simultaneously",
    7: "Blank canvas filling with AI-generated paintings in real time, artists watching in awe",
    8: "Split screen Google vs OpenAI headquarters, data racing between them, epic battle visualization"
}

def generate_clip(script_id, prompt):
    headers = {
        "Authorization": f"Bearer {KLING_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "kling-v3",
        "prompt": prompt,
        "duration": 5,
        "aspect_ratio": "9:16",
        "cfg_scale": 0.5
    }
    
    response = requests.post(f"{BASE_URL}/videos/text2video", headers=headers, json=payload)
    if response.status_code != 200:
        print(f"❌ Kling failed for script {script_id}: {response.text}")
        return {"id": script_id, "file": None, "status": "failed"}
    
    task_id = response.json().get("data", {}).get("task_id")
    print(f"⏳ Kling task {task_id} queued for script {script_id}")
    
    # Poll for completion
    for _ in range(30):
        time.sleep(10)
        status_resp = requests.get(f"{BASE_URL}/videos/text2video/{task_id}", headers=headers)
        status_data = status_resp.json().get("data", {})
        task_status = status_data.get("task_status")
        
        if task_status == "succeed":
            video_url = status_data.get("task_result", {}).get("videos", [{}])[0].get("url")
            os.makedirs("output/videos", exist_ok=True)
            filename = f"output/videos/kling_script_{script_id}.mp4"
            video_data = requests.get(video_url).content
            with open(filename, "wb") as f:
                f.write(video_data)
            print(f"✅ Kling video saved: {filename}")
            return {"id": script_id, "file": filename, "status": "success"}
        elif task_status == "failed":
            print(f"❌ Kling task failed for script {script_id}")
            return {"id": script_id, "file": None, "status": "failed"}
    
    return {"id": script_id, "file": None, "status": "timeout"}

def main():
    with open("output/scripts.json") as f:
        scripts = json.load(f)
    
    metadata = []
    for s in scripts:
        prompt = VIDEO_PROMPTS.get(s["id"], f"Cinematic AI visualization for: {s['title']}, 9:16 vertical format")
        result = generate_clip(s["id"], prompt)
        metadata.append(result)
    
    with open("output/kling_videos_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    print("✅ Kling video metadata saved")

if __name__ == "__main__":
    main()
