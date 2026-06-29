import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_EMAIL = os.environ.get("SMTP_EMAIL", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
NOTIFICATION_EMAIL = os.environ.get("EMAIL_NOTIFICATION", SMTP_EMAIL)
SLACK_WEBHOOK = os.environ.get("SLACK_WEBHOOK", "")

def send_email(subject, body_html):
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        print("⚠️  No SMTP credentials — skipping email")
        return
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = SMTP_EMAIL
        msg["To"] = NOTIFICATION_EMAIL
        msg.attach(MIMEText(body_html, "html"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, NOTIFICATION_EMAIL, msg.as_string())
        print(f"✅ Email sent to {NOTIFICATION_EMAIL}")
    except Exception as e:
        print(f"❌ Email failed: {e}")

def send_slack(message):
    if not SLACK_WEBHOOK:
        return
    import requests
    requests.post(SLACK_WEBHOOK, json={"text": message})
    print("✅ Slack notification sent")

def main():
    # Load results
    yt_results, ig_results = [], []
    try:
        with open("output/youtube_upload_results.json") as f:
            yt_results = json.load(f)
    except: pass
    try:
        with open("output/instagram_upload_results.json") as f:
            ig_results = json.load(f)
    except: pass
    
    yt_success = [r for r in yt_results if r.get("status") == "uploaded"]
    ig_success = [r for r in ig_results if r.get("status") == "published"]
    
    status_emoji = "✅" if (yt_success or ig_success) else "❌"
    subject = f"{status_emoji} Spark of AI Pipeline — {len(yt_success)} YouTube + {len(ig_success)} Instagram videos deployed"
    
    yt_links = "".join([f"<li><a href='{r.get('url', '#')}'>{r.get('id', '')} — {r.get('url', 'N/A')}</a></li>" for r in yt_success])
    
    body = f"""
    <html><body style="font-family: Arial; background: #110E15; color: #fff; padding: 20px;">
    <h2 style="color: #FF2D6C;">⚡ Spark of AI — Pipeline Complete</h2>
    <p><strong>YouTube Shorts:</strong> {len(yt_success)}/{len(yt_results)} uploaded</p>
    <p><strong>Instagram Reels:</strong> {len(ig_success)}/{len(ig_results)} published</p>
    {"<h3>YouTube Links:</h3><ul>" + yt_links + "</ul>" if yt_links else ""}
    <p style="color: #888; font-size: 12px;">Spark of AI automated pipeline — @spark_of_ai</p>
    </body></html>
    """
    
    send_email(subject, body)
    send_slack(f"⚡ Spark of AI pipeline done: {len(yt_success)} YouTube + {len(ig_success)} Instagram videos live!")
    print("✅ Notifications sent")

if __name__ == "__main__":
    main()
