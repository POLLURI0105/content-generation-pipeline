import os
import json
import requests

IDEOGRAM_API_KEY = os.environ["IDEOGRAM_API_KEY"]

THUMBNAIL_PROMPTS = {
    1: "YouTube thumbnail: '100M IN 60 DAYS' in massive bold hot pink text, shocked face emoji, dark AI background, hyper-realistic",
    2: "YouTube thumbnail: 'AI WAS BORN HERE' bold white text, 1956 vintage photo style meets neon glow, mind-blowing",
    3: "YouTube thumbnail: 'AI ALMOST DIED' bold red text, dark dramatic background, frozen circuit board",
    4: "YouTube thumbnail: 'DEEP LEARNING WORKS!' bold neon text, neural network explosion, 2012 computer lab",
    5: "YouTube thumbnail: 'THIS PAPER CHANGED EVERYTHING' bold text, Google engineers, mathematical equations glowing",
    6: "YouTube thumbnail: 'AI WRITES LIKE A HUMAN' bold text, typing animation, GPT-3 era shocked reactions",
    7: "YouTube thumbnail: 'AI CAN PAINT NOW' bold text, split canvas human vs AI art, dramatic reveal",
    8: "YouTube thumbnail: 'GOOGLE vs OPENAI' bold text, epic battle visual, two logos clashing with lightning"
}

def generate_thumbnail(script_id, prompt):
    url = "https://api.ideogram.ai/generate"
    headers = {"Api-Key": IDEOGRAM_API_KEY, "Content-Type": "application/json"}
    payload = {
        "image_request": {
            "prompt": prompt,
            "aspect_ratio": "ASPECT_16_9",
            "model": "V_3",
            "style_type": "REALISTIC",
            "magic_prompt_option": "AUTO"
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        image_url = response.json().get("data", [{}])[0].get("url")
        if image_url:
            os.makedirs("output/thumbnails", exist_ok=True)
            filename = f"output/thumbnails/thumb_script_{script_id}.png"
            with open(filename, "wb") as f:
                f.write(requests.get(image_url).content)
            print(f"✅ Thumbnail saved: {filename}")
            return {"id": script_id, "file": filename, "status": "success"}
    
    print(f"❌ Thumbnail failed for script {script_id}: {response.text}")
    return {"id": script_id, "file": None, "status": "failed"}

def main():
    with open("output/scripts.json") as f:
        scripts = json.load(f)
    
    metadata = []
    for s in scripts:
        prompt = THUMBNAIL_PROMPTS.get(s["id"], f"YouTube thumbnail for: {s['title']}, bold text, high contrast")
        result = generate_thumbnail(s["id"], prompt)
        metadata.append(result)
    
    with open("output/ideogram_thumbnails_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    print("✅ Thumbnail metadata saved")

if __name__ == "__main__":
    main()
