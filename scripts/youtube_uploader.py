import os
import json
import pickle
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

YOUTUBE_CREDENTIALS = os.environ["YOUTUBE_CREDENTIALS"]
CHANNEL_ID = os.environ.get("YOUTUBE_CHANNEL_ID", "")

DESCRIPTIONS = {
    1: "ChatGPT hit 100 million users in just 60 days 🤯 That's faster than ANY app in history. Here's why this changed everything.\n\n#AIHistory #ChatGPT #SparkOfAI #Shorts",
    2: "It all started in 1956. A group of scientists made a bet that would birth Artificial Intelligence. Nobody talks about this meeting. 🧠\n\n#AIHistory #Dartmouth #SparkOfAI #Shorts",
    3: "AI almost died. TWICE. Billions in funding vanished. Labs shut down. Here's the story nobody tells. 🥶\n\n#AIHistory #AIWinter #SparkOfAI #Shorts",
    4: "In 2012, one neural network looked at a million images and deep learning finally WORKED. This changed science forever. ⚡\n\n#AIHistory #AlexNet #DeepLearning #SparkOfAI #Shorts",
    5: "8 Google engineers wrote a paper in 2017. It now powers ChatGPT, Gemini, and almost every AI you use. 📄\n\n#AIHistory #Transformer #SparkOfAI #Shorts",
    6: "In 2020, OpenAI released an AI so good at writing, people thought it was human. GPT-3 changed everything. ✍️\n\n#AIHistory #GPT3 #SparkOfAI #Shorts",
    7: "In 2022, AI taught itself to paint. Artists panicked. The internet went insane. 🎨\n\n#AIHistory #DALLE #StableDiffusion #SparkOfAI #Shorts",
    8: "Two of the biggest companies on Earth went to war over AI. Here's how the arms race started. ⚔️\n\n#AIHistory #Google #OpenAI #SparkOfAI #Shorts"
}

def upload_video(script_id, title, video_file, thumbnail_file):
    creds_data = json.loads(YOUTUBE_CREDENTIALS)
    creds = Credentials.from_authorized_user_info(creds_data)
    youtube = build("youtube", "v3", credentials=creds)
    
    body = {
        "snippet": {
            "title": f"{title} #Shorts",
            "description": DESCRIPTIONS.get(script_id, f"Spark of AI — {title}\n\n#SparkOfAI #AIHistory #Shorts"),
            "tags": ["AI", "AIHistory", "SparkOfAI", "Shorts", "ArtificialIntelligence"],
            "categoryId": "28",
            "defaultLanguage": "en"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }
    
    media = MediaFileUpload(video_file, mimetype="video/mp4", resumable=True, chunksize=1024*1024)
    
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"⏳ Uploading script {script_id}: {int(status.progress() * 100)}%")
    
    video_id = response.get("id")
    print(f"✅ YouTube upload complete: https://youtube.com/shorts/{video_id}")
    
    if thumbnail_file and os.path.exists(thumbnail_file):
        youtube.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(thumbnail_file)).execute()
        print(f"✅ Thumbnail set for video {video_id}")
    
    return {"id": script_id, "youtube_id": video_id, "url": f"https://youtube.com/shorts/{video_id}", "status": "uploaded"}

def main():
    with open("output/final_videos/final_metadata.json") as f:
        finals = json.load(f)
    
    with open("output/scripts.json") as f:
        scripts = {str(s["id"]): s for s in json.load(f)}
    
    results = []
    for item in finals:
        if item.get("final_video") and os.path.exists(item["final_video"]):
            result = upload_video(item["id"], item["title"], item["final_video"], item.get("thumbnail"))
            results.append(result)
        else:
            print(f"⚠️  No final video for script {item['id']} — skipping")
            results.append({"id": item["id"], "status": "skipped"})
    
    with open("output/youtube_upload_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("✅ YouTube upload results saved")

if __name__ == "__main__":
    main()
