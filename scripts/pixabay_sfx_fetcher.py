import os
import json
import requests

PIXABAY_API_KEY = os.environ["PIXABAY_API_KEY"]

SFX_QUERIES = {
    1: "technology whoosh",
    2: "typewriter office",
    3: "power down shutdown",
    4: "electricity surge",
    5: "digital data",
    6: "typing keyboard",
    7: "brush swoosh",
    8: "epic dramatic"
}

def fetch_sfx(script_id, query):
    url = "https://pixabay.com/api/"
    params = {
        "key": PIXABAY_API_KEY,
        "q": query,
        "media_type": "music",
        "per_page": 2
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return {"id": script_id, "files": [], "status": "failed"}
    
    hits = response.json().get("hits", [])
    results = []
    os.makedirs("output/sfx_stock", exist_ok=True)
    
    for i, hit in enumerate(hits):
        audio_url = hit.get("audio", {}).get("url") or hit.get("previewURL")
        if audio_url:
            filename = f"output/sfx_stock/pixabay_sfx_{script_id}_{i+1}.mp3"
            with open(filename, "wb") as f:
                f.write(requests.get(audio_url).content)
            results.append({"file": filename})
            print(f"✅ Pixabay SFX saved for script {script_id}")
    
    return {"id": script_id, "files": results, "status": "success"}

def main():
    with open("output/scripts.json") as f:
        scripts = json.load(f)
    
    metadata = []
    for s in scripts:
        query = SFX_QUERIES.get(s["id"], "technology")
        result = fetch_sfx(s["id"], query)
        metadata.append(result)
    
    with open("output/pixabay_sfx_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    print("✅ Pixabay SFX metadata saved")

if __name__ == "__main__":
    main()
