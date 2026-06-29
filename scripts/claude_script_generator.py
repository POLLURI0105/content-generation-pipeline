import os
import json
import anthropic

def generate_scripts():
    client = anthropic.Anthropic(api_key=os.environ["CLAUDE_API_KEY"])
    
    with open("ideas/weekly_ideas.json") as f:
        ideas = json.load(f)
    
    scripts = []
    for idea in ideas:
        print(f"Generating script for: {idea['title']}")
        message = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": f"""Write a 60-second YouTube Shorts / Instagram Reels script for Spark of AI channel.

Topic: {idea['topic']}
Hook: {idea['hook']}
Style: {idea['style']}
Tags: {', '.join(idea['tags'])}

Format rules:
- Open with the hook (shocking stat or fact)
- Use HIGH-ENERGY punchy sentences — MrBeast style
- Caps for emphasis words
- Ellipses ... for dramatic pauses
- Em-dashes — for sharp transitions
- End with a mind-blown payoff + CTA to follow @spark_of_ai
- Max 150 words (60 seconds at normal pace)
- Add ElevenLabs emotion tags as HTML comments: <!-- emotion: surprised --> for hooks, <!-- emotion: fluent --> for exposition, <!-- emotion: fearful --> for tension, <!-- emotion: happy --> for payoffs

Output ONLY the script text with emotion tags. No titles, no metadata."""
            }]
        )
        script_text = message.content[0].text
        scripts.append({
            "id": idea["id"],
            "title": idea["title"],
            "topic": idea["topic"],
            "script": script_text,
            "tags": idea["tags"],
            "duration": idea["duration"]
        })
        print(f"✅ Script {idea['id']} done")
    
    os.makedirs("output", exist_ok=True)
    with open("output/scripts.json", "w") as f:
        json.dump(scripts, f, indent=2)
    print(f"✅ All {len(scripts)} scripts saved to output/scripts.json")

if __name__ == "__main__":
    generate_scripts()
