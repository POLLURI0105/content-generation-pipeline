import os
import json
import requests

INSTAGRAM_ACCESS_TOKEN = os.environ["INSTAGRAM_ACCESS_TOKEN"]
INSTAGRAM_USER_ID = os.environ.get("INSTAGRAM_USER_ID", "")

CAPTIONS = {
    1: "ChatGPT hit 100M users in 60 days 🤯 No app EVER grew this fast. Here's why it changed everything ⬇️\n\n#SparkOfAI #ChatGPT #AIHistory #Reels #ArtificialIntelligence",
    2: "In 1956, a group of scientists coined the term 'Artificial Intelligence' 🧠 This is the origin story nobody talks about.\n\n#SparkOfAI #AIHistory #Dartmouth #Reels",
    3: "AI almost died TWICE 🥶 Billions vanished. Labs shut down. The AI winters are the most dramatic story in tech.\n\n#SparkOfAI #AIWinter #AIHistory #Reels",
    4: "One neural network + 1 million images = deep learning finally works ⚡ AlexNet 2012 changed EVERYTHING.\n\n#SparkOfAI #AlexNet #DeepLearning #Reels",
    5: "8 engineers. One paper. Now powers every AI you use 📄 'Attention Is All You Need' — the most important paper ever written.\n\n#SparkOfAI #Transformer #AIHistory #Reels",
    6: "GPT-3 could write like a human. People thought it was sentient 😱 2020 changed AI forever.\n\n#SparkOfAI #GPT3 #OpenAI #Reels",
    7: "2022: AI taught itself to paint 🎨 Artists panicked. The internet lost its mind. Here's what happened.\n\n#SparkOfAI #DALLE #StableDiffusion #Reels",
    8: "Google vs OpenAI. The biggest tech war in history ⚔️ Bard vs ChatGPT — how the AI arms race started.\n\n#SparkOfAI #Google #OpenAI #AIRace #Reels"
}

def upload_reel(script_id, title, video_file):
    # Step 1: Upload video container
    container_url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_USER_ID}/media"
    
    # For Instagram Reels, video must be publicly accessible URL
    # In production, upload to S3/Cloudinary first, then pass the URL
    video_url = os.environ.get(f"VIDEO_URL_{script_id}", "")
    
    if not video_url:
        print(f"⚠️  No public video URL for script {script_id}. Upload to cloud storage first.")
        return {"id": script_id, "status": "needs_cloud_url"}
    
    container_payload = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": CAPTIONS.get(script_id, f"Spark of AI — {title} #SparkOfAI #Reels"),
        "share_to_feed": True,
        "access_token": INSTAGRAM_ACCESS_TOKEN
    }
    
    container_resp = requests.post(container_url, data=container_payload)
    if container_resp.status_code != 200:
        print(f"❌ Instagram container failed for script {script_id}: {container_resp.text}")
        return {"id": script_id, "status": "failed"}
    
    container_id = container_resp.json().get("id")
    print(f"⏳ Instagram container created: {container_id}")
    
    import time
    time.sleep(30)  # Wait for video processing
    
    # Step 2: Publish
    publish_url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_USER_ID}/media_publish"
    publish_payload = {"creation_id": container_id, "access_token": INSTAGRAM_ACCESS_TOKEN}
    
    publish_resp = requests.post(publish_url, data=publish_payload)
    if publish_resp.status_code == 200:
        media_id = publish_resp.json().get("id")
        print(f"✅ Instagram Reel published: {media_id}")
        return {"id": script_id, "instagram_id": media_id, "status": "published"}
    
    print(f"❌ Instagram publish failed: {publish_resp.text}")
    return {"id": script_id, "status": "publish_failed"}

def main():
    with open("output/final_videos/final_metadata.json") as f:
        finals = json.load(f)
    
    results = []
    for item in finals:
        result = upload_reel(item["id"], item["title"], item.get("final_video"))
        results.append(result)
    
    with open("output/instagram_upload_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("✅ Instagram upload results saved")

if __name__ == "__main__":
    main()
