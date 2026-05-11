import feedparser
import requests
import whisper
import os
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

def get_latest_gooaye_episode():
    rss_url = "https://open.firstory.me/rss/user/ckinqg0o0f9y30855nzzg4c3v" 
    feed = feedparser.parse(rss_url)
    if not feed.entries:
        return None, None
    latest = feed.entries[0]
    title = latest.title
    for link in latest.links:
        if link.type == 'audio/mpeg':
            return link.href, title
    return None, title

def download_and_transcribe(mp3_url):
    audio_file = "podcast.mp3"
    print("📥 開始下載音檔...")
    response = requests.get(mp3_url, stream=True)
    with open(audio_file, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024*1024):
            if chunk:
                f.write(chunk)
    
    print("🧠 開始 Whisper 轉譯 (約 15-30 分鐘)...")
    model = whisper.load_model("base")
    result = model.transcribe(audio_file)
    os.remove(audio_file)
    
    # 將逐字稿存成 txt 檔案
    transcript_text = result["text"]
    with open("transcript.txt", "w", encoding="utf-8") as f:
        f.write(transcript_text)
        
    return transcript_text

def analyze_with_gemini(transcript, title):
    print("🤖 呼叫 Gemini 進行產業分析...")
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    你是一位專業的投資顧問助理。以下是知名財經 Podcast「股癌」最新一集【{title}】的逐字稿。
    請幫我進行深度摘要與產業分析，特別關注以下幾點：
    1. 重點美台股標的：列出節目中提到的公司或股票代號，並簡述其看法。
    2. 半導體與科技產業動態：特別幫我留意是否有提到 CPO、CoWoS、ABF 載板、低軌衛星等技術或相關供應鏈的觀點。
    3. 總經與市場看法：大盤趨勢或重要數據解讀。
    4. 格式要求：排除生活閒聊，直接條列重點，排版要清晰易讀。
    
    逐字稿內容：
    {transcript}
    """
    response = model.generate_content(prompt)
    return response.text

def send_email(subject, content, transcript_file_path):
    print("📧 準備寄送電子報與逐字稿附件...")
    gmail_user = os.environ.get("GMAIL_USER")
    gmail_password = os.environ.get("GMAIL_PASSWORD")
    
    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = gmail_user
    msg['Subject'] = f"【股癌 AI 助理】{subject} - 分析報告與逐字稿"
    
    # 郵件正文 (AI 分析結果)
    msg.attach(MIMEText(content, 'plain', 'utf-8'))
    
    # 添加附件 (完整逐字稿)
    if os.path.exists(transcript_file_path):
        with open(transcript_file_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(transcript_file_path))
        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(transcript_file_path)}"'
        msg.attach(part)
    
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(gmail_user, gmail_password)
        server.send_message(msg)
        server.quit()
        print("✅ 電子報與逐字稿寄送成功！")
    except Exception as e:
        print(f"❌ 寄信失敗：{e}")

if __name__ == "__main__":
    mp3_link, episode_title = get_latest_gooaye_episode()
    if mp3_link:
        print(f"📌 處理集數：{episode_title}")
        transcript = download_and_transcribe(mp3_link)
        analysis_result = analyze_with_gemini(transcript, episode_title)
        # 傳入生成的逐字稿路徑
        send_email(episode_title, analysis_result, "transcript.txt")
