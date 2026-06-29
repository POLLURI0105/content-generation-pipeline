import os
import json
import requests

CANVA_API_KEY = os.environ.get("CANVA_API_KEY", "")

SPARK_AI_COLORS = {
    "wine": "#411D2B",
    "hot_pink": "#FF2D6C",
    "crimson": "#E11D48",
    "white": "#FFFFFF",
    "near_black": "#110E15"
}

def create_canva_thumbnail(script_id, title):
    if not CANVA_API_KEY:
        print(f"⚠️  No Canva API key — skipping script {script_id}")
        return {"id": script_id, "file": None, "status": "skipped"}
    
    url = "https://api.canva.com/rest/v1/designs"
    headers = {
        "Authorization": f"Bearer {CANVA_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "design_type": {"type": "preset", "name": "YouTubeThumbnail"},
        "title": f"Spark of AI - {title}"
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code in [200, 201]:
        design = response.json()
        design_url = design.get("urls", {}).get("edit_url")
        design_id = design.get("id")
        print(f"✅ Canva design created for script {script_id}: {design_id}")
        return {"id": script_id, "design_id": design_id, "edit_url": design_url, "status": "success"}
    
    print(f"❌ Canva failed for script {script_id}: {response.text}")
    return {"id": script_id, "file": None, "status": "failed"}

def main():
    with open("output/scripts.json") as f:
        scripts = json.load(f)
    
    metadata = []
    for s in scripts:
        result = create_canva_thumbnail(s["id"], s["title"])
        metadata.append(result)
    
    with open("output/canva_thumbnails_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    print("✅ Canva thumbnails metadata saved")

if __name__ == "__main__":
    main()
