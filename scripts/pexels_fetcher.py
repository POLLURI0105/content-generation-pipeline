import os
import json
import requests

PEXELS_API_KEY = os.environ["PEXELS_API_KEY"]

SEARCH_QUERIES = {
    1: "artificial intelligence technology viral growth",
    2: "university conference meeting 1950s vintage",
    3: "empty laboratory dark abandoned research",
    4: "neural network deep learning visualization",
    5: "mathematics equations data science",
    6: "typing keyboard screen writing technology",
    7: "painting art digital creation artist",
    8: "technology competition race innovation"
}

def fetch_pexels_videos(script_id, query, per_page=3):
    url = "https://api.pexels.com/videos/search"
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": per_page, "orientation": "portrait", "size": "medium"}
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"❌ Pexels failed for script {script_id}: {response.text}")
        return {"id": script_id, "videos": [], "status": "failed"}
    
    videos = response.json().get("videos", [])
    results = []
    os.makedirs("output/broll", exist_ok=True)
    
    for i, video in enumerate(videos):
        video_files = video.get("video_files", [])
        hd_file = next((v for v in video_files if v.get("quality") == "hd"), video_files[0] if video_files else None)
        if hd_file:
            video_url = hd_file.get("link")
            filename = f"output/broll/pexels_script_{script_id}_{i+1}.mp4"
            with open(filename, "wb") as f:
                f.write(requests.get(video_url).content)
            results.append({"file": filename, "url": video_url, "duration": video.get("duration")})
            print(f"✅ Pexels clip {i+1} saved for script {script_id}")
    
    return {"id": script_id, "videos": results, "status": "success"}

def main():
    with open("output/scripts.json") as f:
        scripts = json.load(f)
    
    metadata = []
    for s in scripts:
        query = SEARCH_QUERIES.get(s["id"], s["title"])
        result = fetch_pexels_videos(s["id"], query)
        metadata.append(result)
    
    with open("output/pexels_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    print("✅ Pexels metadata saved")

if __name__ == "__main__":
    main()
