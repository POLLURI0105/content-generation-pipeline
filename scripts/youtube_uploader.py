import os
import json
import sys

print("=== YouTube Uploader Starting ===")

YOUTUBE_CREDENTIALS = os.environ.get("YOUTUBE_CREDENTIALS", "")

if not YOUTUBE_CREDENTIALS:
    print("ERROR: YOUTUBE_CREDENTIALS secret is empty or not set.")
    sys.exit(1)

# Fix common issue: extra data after closing brace (truncate at last })
def parse_credentials_json(s):
    s = s.strip()
    last_brace = s.rfind('}')
    if last_brace != -1:
        s = s[:last_brace + 1]
    return json.loads(s)

try:
    creds_data = parse_credentials_json(YOUTUBE_CREDENTIALS)
    print(f"Credentials parsed OK. Keys: {list(creds_data.keys())}")
    print(f"client_id: {creds_data.get('client_id', 'MISSING')[:30]}...")
    print(f"refresh_token: {'present' if creds_data.get('refresh_token') else 'MISSING'}")
    print(f"token_uri: {creds_data.get('token_uri', 'MISSING')}")
except json.JSONDecodeError as e:
    print(f"ERROR: YOUTUBE_CREDENTIALS is not valid JSON even after cleanup: {e}")
    print(f"First 200 chars: {YOUTUBE_CREDENTIALS[:200]}")
    sys.exit(1)

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

CHANNEL_ID = os.environ.get("YOUTUBE_CHANNEL_ID", "")
FINAL_METADATA_PATH = "output/final_metadata.json"

print(f"\nChecking output directory...")
if os.path.exists("output"):
    files = [f for f in os.listdir("output")]
    print(f"Files in output/: {files[:20]}")
else:
    print("ERROR: output/ directory does not exist!")
    sys.exit(1)

if not os.path.exists(FINAL_METADATA_PATH):
    print(f"ERROR: {FINAL_METADATA_PATH} not found")
    sys.exit(1)

with open(FINAL_METADATA_PATH) as f:
    finals = json.load(f)

print(f"Loaded {len(finals)} video entries")

DESCRIPTIONS = {
    1: "ChatGPT hit 100 million users in just 60 days. That's faster than ANY app in history.\n\n#AIHistory #ChatGPT #SparkOfAI #Shorts",
    2: "It all started in 1956. A group of scientists made a bet that would birth Artificial Intelligence.\n\n#AIHistory #Dartmouth #SparkOfAI #Shorts",
    3: "AI almost died. TWICE. Billions in funding vanished. Labs shut down.\n\n#AIHistory #AIWinter #SparkOfAI #Shorts",
    4: "A team of 8 researchers changed EVERYTHING in 2017 with one paper: Attention Is All You Need.\n\n#AIHistory #Transformers #SparkOfAI #Shorts",
    5: "GPT-1 had 117M parameters. GPT-4 has over 1 TRILLION. Here's how we got here.\n\n#AIHistory #GPT #SparkOfAI #Shorts",
    6: "AI can now write better than most humans. Here's the moment that proved it.\n\n#AIHistory #LLM #SparkOfAI #Shorts",
    7: "DALL-E changed art forever. The story behind AI's first viral image generator.\n\n#AIHistory #DALLE #SparkOfAI #Shorts",
    8: "Google vs OpenAI. The greatest AI race of our generation.\n\n#AIHistory #Google #OpenAI #SparkOfAI #Shorts",
}

def upload_video(script_id, title, video_file):
    print(f"\nUploading script {script_id}: {title}")
    size_kb = os.path.getsize(video_file) // 1024
    print(f"  File: {video_file} ({size_kb} KB)")

    creds = Credentials.from_authorized_user_info(creds_data)
    youtube = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": f"{title} #Shorts",
            "description": DESCRIPTIONS.get(script_id, f"Spark of AI -- {title}\n\n#SparkOfAI #AIHistory #Shorts"),
            "tags": ["AI", "AIHistory", "SparkOfAI", "Shorts"],
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
            print(f"  Progress: {int(status.progress() * 100)}%")

    video_id = response.get("id", "unknown")
    print(f"  Uploaded: https://youtube.com/shorts/{video_id}")
    return video_id

def main():
    results = []
    uploaded = 0

    for item in finals:
        script_id = item.get("id")
        title = item.get("title", f"Script {script_id}")
        video_file = item.get("final_video")
        status = item.get("status")

        print(f"\nScript {script_id}: status={status}, file={video_file}")

        if not video_file:
            print(f"  Skipping - no video file")
            results.append({"id": script_id, "status": "skipped"})
            continue

        # Resolve path after artifact download
        if not os.path.exists(video_file):
            basename = os.path.basename(video_file)
            for candidate in [os.path.join("output", basename), basename]:
                if os.path.exists(candidate):
                    video_file = candidate
                    break

        if not os.path.exists(video_file):
            print(f"  Skipping - file not found: {video_file}")
            results.append({"id": script_id, "status": "missing"})
            continue

        try:
            vid_id = upload_video(script_id, title, video_file)
            results.append({"id": script_id, "title": title, "youtube_id": vid_id, "status": "uploaded"})
            uploaded += 1
        except Exception as e:
            print(f"  Upload FAILED: {e}")
            import traceback
            traceback.print_exc()
            results.append({"id": script_id, "status": "failed", "error": str(e)})

    print(f"\n=== Done: {uploaded}/{len(finals)} uploaded ===")
    with open("output/youtube_results.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
