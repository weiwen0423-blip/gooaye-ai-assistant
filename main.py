import feedparser
import requests
import whisper
import os

def get_latest_gooaye_episode():
    rss_url = "https://open.firstory.me/rss/user/ckinqg0o0f9y30855nzzg4c3v" 
    print("正在抓取股癌最新節目...")
    feed = feedparser.parse(rss_url)
    
    if not feed.entries:
        print("抓取失敗！")
        return None
        
    latest = feed.entries[0]
    print(f"📌 找到最新集數：{latest.title}")
    
    for link in latest.links:
        if link.type == 'audio/mpeg':
            return link.href
    return None

def download_and_transcribe(mp3_url):
    audio_file = "podcast.mp3"
    
    print("📥 開始下載音檔...")
    response = requests.get(mp3_url, stream=True)
    with open(audio_file, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024*1024):
            if chunk:
                f.write(chunk)
    print("✅ 下載完成！")

    print("🧠 開始使用 Whisper 轉譯逐字稿 (請耐心等待，這步大約需要 15-30 分鐘)...")
    # 使用 base 模型，在速度與辨識度取得平衡
    model = whisper.load_model("base")
    result = model.transcribe(audio_file)
    
    transcript = result["text"]
    
    # 將逐字稿存成 txt 檔案，方便下一步讓 AI 讀取
    with open("transcript.txt", "w", encoding="utf-8") as f:
        f.write(transcript)
        
    print("\n✅ 轉譯完成！以下是開頭前 300 字預覽：")
    print(transcript[:300] + "...\n")
    
    # 刪除音檔，避免佔用 GitHub 伺服器空間
    os.remove(audio_file)
    print("🗑️ 音檔已刪除，釋放空間。")

if __name__ == "__main__":
    mp3_link = get_latest_gooaye_episode()
    if mp3_link:
        download_and_transcribe(mp3_link)
