import os
import json
import requests

PIXABAY_API_KEY = os.environ["PIXABAY_API_KEY"]

SEARCH_QUERIES = {
    1: "technology network global connection",
    2: "science research history academic",
    3: "dark winter cold freeze",
    4: "computer learning machine data",
    5: "mathematics formula algorithm",
    6: "writing text screen digital",
    7: "art painting creative colorful",
    8: "competition race technology future"
}

def fetch_pixabay_videos(script_id, query, per_page=3):
    url = "https://pixabay.com/api/videos/"
    params = {
        "key": PIXABAY_API_KEY,
        "q": query,
        "per_page": per_page,
        "video_type": "film",
        "safesearch": "true"
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"❌ Pixabay failed for script {script_id}: {response.text}")
        return {"id": script_id, "videos": [], "status": "failed"}
    
    hits = response.json().get("hits", [])
    results = []
    os.makedirs("output/broll", exist_ok=True)
    
    for i, video in enumerate(hits):
        video_url = video.get("videos", {}).get("medium", {}).get("url")
        if video_url:
            filename = f"output/broll/pixabay_script_{script_id}_{i+1}.mp4"
            with open(filename, "wb") as f:
                f.write(requests.get(video_url).content)
            results.append({"file": filename, "url": video_url})
            print(f"✅ Pixabay clip {i+1} saved for script {script_id}")
    
    return {"id": script_id, "videos": results, "status": "success"}

def main():
    with open("output/scripts.json") as f:
        scripts = json.load(f)
    
    metadata = []
    for s in scripts:
        query = SEARCH_QUERIES.get(s["id"], s["title"])
        result = fetch_pixabay_videos(s["id"], query)
        metadata.append(result)
    
    with open("output/pixabay_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    print("✅ Pixabay metadata saved")

if __name__ == "__main__":
    main()
