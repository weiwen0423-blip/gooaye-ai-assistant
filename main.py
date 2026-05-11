import requests
import whisper
import os
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

def get_latest_gooaye_episode():
    # 🌟 秘訣：使用 rss2json 代理服務來繞過 Firstory 的機房阻擋
    api_url = "https://api.rss2json.com/v1/api.json?rss_url=https://open.firstory.me/rss/user/ckinqg0o0f9y30855nzzg4c3v" 
    print("🔍 透過代理服務檢查最新集數...")
    
    try:
        response = requests.get(api_url)
        data = response.json()
    except Exception as e:
        print(f"❌ 讀取 API 失敗：{e}")
        return None, None
    
    if data.get('status') != 'ok' or not data.get('items'):
        print("❌ 抓取失敗，找不到集數（代理伺服器可能出錯）！")
        return None, None
        
    latest = data['items'][0]
    title = latest.get('title')
    
    # --- 記憶功能：檢查是否已經處理過 ---
    memory_file = "last_episode.txt"
    last_title = ""
    if os.path.exists(memory_file):
        with open(memory_file, "r", encoding="utf-8") as f:
            last_title = f.read().strip()
            
    if title == last_title:
        print(f"💤 最新集數【{title}】已經處理過了，繼續休眠。")
        return None, None
        
    print(f"✨ 發現新集數！準備處理：{title}")
    
    # 從 JSON 資料中直接抽出 mp3 網址
    mp3_link = latest.get('enclosure', {}).get('link')
    
    if mp3_link:
        return mp3_link, title
        
    print("❌ 找不到音檔連結。")
    return None, title

def download_and_transcribe(mp3_url):
    audio_file = "podcast.mp3"
    print("📥 下載音檔中...")
    response = requests.get(mp3_url, stream=True)
    with open(audio_file, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024*1024):
            if chunk:
                f.write(chunk)
    
    print("🧠 Whisper 努力聽寫中 (約需 15-30 分鐘)...")
    model = whisper.load_model("base")
    result = model.transcribe(audio_file)
    os.remove(audio_file)
    
    transcript_text = result["text"]
    with open("transcript.txt", "w", encoding="utf-8") as f:
        f.write(transcript_text)
        
    return transcript_text

def analyze_with_gemini(transcript, title):
    print("🤖 Gemini 產業分析中...")
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
    print("📧 寄送分析報告與逐字稿...")
    gmail_user = os.environ.get("GMAIL_USER")
    gmail_password = os.environ.get("GMAIL_PASSWORD")
    
    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = gmail_user
    msg['Subject'] = f"【股癌 AI 助理】{subject}"
    
    msg.attach(MIMEText(content, 'plain', 'utf-8'))
    
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
        print("✅ 寄送成功！")
        return True
    except Exception as e:
        print(f"❌ 寄信失敗：{e}")
        return False

if __name__ == "__main__":
    mp3_link, episode_title = get_latest_gooaye_episode()
    if mp3_link:
        transcript = download_and_transcribe(mp3_link)
        analysis_result = analyze_with_gemini(transcript, episode_title)
        success = send_email(episode_title, analysis_result, "transcript.txt")
        
        # --- 如果成功寄出，就把這集記進小本子裡 ---
        if success:
            with open("last_episode.txt", "w", encoding="utf-8") as f:
                f.write(episode_title)
            print("💾 已更新記憶本，下次不會重複處理這集。")
