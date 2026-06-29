import os
import json
import requests
import time

MIDJOURNEY_API_KEY = os.environ.get("MIDJOURNEY_API_KEY", "")

MJ_PROMPTS = {
    1: "100 million glowing dots forming a neural network globe, cyberpunk aesthetic --ar 9:16 --v 7",
    2: "Vintage 1956 scientists meeting, sepia photograph style, dramatic lighting --ar 9:16 --v 7",
    3: "Frozen computer lab in winter, blue ice, abandoned screens, dramatic --ar 9:16 --v 7",
    4: "Explosion of light from a GPU chip, neural pathways, breakthrough moment --ar 9:16 --v 7",
    5: "Flowing mathematical attention diagram, golden geometric patterns, ethereal --ar 9:16 --v 7",
    6: "Typewriter merging with a glowing screen, words materializing, futuristic --ar 9:16 --v 7",
    7: "AI painting a masterpiece in real time, brush strokes becoming pixels --ar 9:16 --v 7",
    8: "Epic battle between two tech giants, skyscrapers, lightning, cinematic --ar 9:16 --v 7"
}

def generate_mj_image(script_id, prompt):
    if not MIDJOURNEY_API_KEY:
        print(f"⚠️  No Midjourney key — skipping script {script_id}")
        return {"id": script_id, "file": None, "status": "skipped"}
    
    url = "https://api.midjourney.com/v1/imagine"
    headers = {"Authorization": f"Bearer {MIDJOURNEY_API_KEY}", "Content-Type": "application/json"}
    payload = {"prompt": prompt}
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"❌ Midjourney failed for script {script_id}: {response.text}")
        return {"id": script_id, "file": None, "status": "failed"}
    
    task_id = response.json().get("task_id")
    for _ in range(20):
        time.sleep(15)
        status_resp = requests.get(f"https://api.midjourney.com/v1/tasks/{task_id}", headers=headers)
        status_data = status_resp.json()
        if status_data.get("status") == "completed":
            image_url = status_data.get("image_url")
            os.makedirs("output/mj_images", exist_ok=True)
            filename = f"output/mj_images/mj_script_{script_id}.png"
            with open(filename, "wb") as f:
                f.write(requests.get(image_url).content)
            print(f"✅ Midjourney image saved: {filename}")
            return {"id": script_id, "file": filename, "status": "success"}
    
    return {"id": script_id, "file": None, "status": "timeout"}

def main():
    with open("output/scripts.json") as f:
        scripts = json.load(f)
    
    metadata = []
    for s in scripts:
        prompt = MJ_PROMPTS.get(s["id"], f"Cinematic AI visualization, {s['title']} --ar 9:16 --v 7")
        result = generate_mj_image(s["id"], prompt)
        metadata.append(result)
    
    with open("output/mj_images_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    print("✅ Midjourney metadata saved")

if __name__ == "__main__":
    main()
