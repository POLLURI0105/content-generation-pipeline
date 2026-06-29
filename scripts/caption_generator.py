import os
import json
import requests
import re

ELEVENLABS_API_KEY = os.environ["ELEVENLABS_API_KEY"]

def generate_captions(script_id, script_text):
    # Clean script of emotion tags
    clean_text = re.sub(r'<!--.*?-->', '', script_text).strip()
    
    # Split into caption chunks (~5 words each for punchy short-form style)
    words = clean_text.split()
    chunks = []
    for i in range(0, len(words), 5):
        chunk = ' '.join(words[i:i+5])
        chunks.append(chunk)
    
    os.makedirs("output/captions", exist_ok=True)
    srt_lines = []
    time_per_chunk = 1.5  # seconds per 5-word chunk
    
    for i, chunk in enumerate(chunks):
        start = i * time_per_chunk
        end = start + time_per_chunk
        start_str = f"{int(start//3600):02}:{int((start%3600)//60):02}:{start%60:06.3f}".replace('.', ',')
        end_str = f"{int(end//3600):02}:{int((end%3600)//60):02}:{end%60:06.3f}".replace('.', ',')
        srt_lines.append(f"{i+1}\n{start_str} --> {end_str}\n{chunk.upper()}\n")
    
    srt_content = "\n".join(srt_lines)
    filename = f"output/captions/captions_script_{script_id}.srt"
    with open(filename, "w") as f:
        f.write(srt_content)
    
    print(f"✅ Captions saved: {filename}")
    return {"id": script_id, "file": filename, "chunks": len(chunks), "status": "success"}

def main():
    with open("output/scripts.json") as f:
        scripts = json.load(f)
    
    metadata = []
    for s in scripts:
        result = generate_captions(s["id"], s["script"])
        metadata.append(result)
    
    with open("output/captions_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    print("✅ Captions metadata saved")

if __name__ == "__main__":
    main()
