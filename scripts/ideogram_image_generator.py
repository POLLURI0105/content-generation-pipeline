import os
import json
import requests

IDEOGRAM_API_KEY = os.environ["IDEOGRAM_API_KEY"]

IMAGE_PROMPTS = {
    1: "Bold text '100 MILLION' in neon pink on dark background, AI neural network aesthetic, vertical 9:16",
    2: "Vintage 1956 academic setting with AI text overlay, sepia tone meets digital future, vertical 9:16",
    3: "Dark dramatic scene with 'AI WINTER' text, frozen circuits, deep blue and black, vertical 9:16",
    4: "Neural network exploding with light, 'ALEXNET 2012' bold text, breakthrough visualization, vertical 9:16",
    5: "Mathematical attention diagram with 'ATTENTION IS ALL YOU NEED' title text, golden glow, vertical 9:16",
    6: "AI typing text on glowing screen, 'GPT-3' large bold text, futuristic terminal aesthetic, vertical 9:16",
    7: "Split canvas — blank left, AI painting right, 'DALL-E' text, artistic explosion of color, vertical 9:16",
    8: "Google G vs OpenAI logo face-off with lightning bolt between, 'THE AI ARMS RACE' text, vertical 9:16"
}

def generate_image(script_id, prompt):
    url = "https://api.ideogram.ai/generate"
    headers = {
        "Api-Key": IDEOGRAM_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "image_request": {
            "prompt": prompt,
            "aspect_ratio": "ASPECT_9_16",
            "model": "V_3",
            "style_type": "DESIGN",
            "magic_prompt_option": "AUTO"
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        image_url = data.get("data", [{}])[0].get("url")
        if image_url:
            os.makedirs("output/images", exist_ok=True)
            filename = f"output/images/ideogram_script_{script_id}.png"
            img_data = requests.get(image_url).content
            with open(filename, "wb") as f:
                f.write(img_data)
            print(f"✅ Ideogram image saved: {filename}")
            return {"id": script_id, "file": filename, "status": "success"}
    
    print(f"❌ Ideogram failed for script {script_id}: {response.text}")
    return {"id": script_id, "file": None, "status": "failed"}

def main():
    with open("output/scripts.json") as f:
        scripts = json.load(f)
    
    metadata = []
    for s in scripts:
        prompt = IMAGE_PROMPTS.get(s["id"], f"Bold AI history visual for: {s['title']}, vertical 9:16 format")
        result = generate_image(s["id"], prompt)
        metadata.append(result)
    
    with open("output/ideogram_images_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    print("✅ Ideogram images metadata saved")

if __name__ == "__main__":
    main()
