import feedparser

    def get_latest_gooaye_episode():
        rss_url = "https://open.firstory.me/rss/user/ckinqg0o0f9y30855nzzg4c3v" 
        print("正在抓取股癌的最新節目資訊...")
        feed = feedparser.parse(rss_url)
        
        if not feed.entries:
            print("抓取失敗，找不到任何集數！")
            return
            
        latest_episode = feed.entries[0]
        title = latest_episode.title
        published = latest_episode.published
        
        mp3_link = None
        for link in latest_episode.links:
            if link.type == 'audio/mpeg':
                mp3_link = link.href
                break
                
        if mp3_link:
            print("\n✅ 抓取成功！")
            print(f"📌 最新集數：{title}")
            print(f"🕒 上架時間：{published}")
            print(f"🔗 音檔連結：{mp3_link}")
        else:
            print("找不到這集的音檔連結。")

    if __name__ == "__main__":
        get_latest_gooaye_episode()
    ```
*   點擊 **「Commit changes...」** 存檔。

#### 3. 建立 GitHub Actions 腳本 (雲端自動化機器人的說明書)
*   再次點擊 **「Add file」** ➔ **「Create new file」**。
*   **檔名輸入** (這很重要，資料夾路徑必須打對)：`.github/workflows/daily_task.yml`
    *(只要打出斜線 `/`，GitHub 就會自動幫你變出資料夾)*
*   **內容貼上**：
    
```yaml
    name: 股癌 Podcast 自動抓取

    on:
      workflow_dispatch: # 這個設定讓我們可以隨時手動點擊按鈕來測試

    jobs:
      run-scraper:
        runs-on: ubuntu-latest

        steps:
        - name: 把程式碼抓到虛擬機器
          uses: actions/checkout@v3

        - name: 安裝 Python 環境
          uses: actions/setup-python@v4
          with:
            python-version: '3.10'

        - name: 安裝必備套件
          run: pip install -r requirements.txt

        - name: 執行 Python 腳本
          run: python main.py
    ```
*   點擊 **「Commit changes...」** 存檔。

---

### 第三步：手動觸發測試！

檔案都建好後，我們來驗收成果：
1. 點擊你 GitHub 專案上方的 **「Actions」** 頁籤。
2. 在左側選單點擊你剛剛設定的工作名稱 **「股癌 Podcast 自動抓取」**。
3. 右邊會出現一個 **「Run workflow」** 的下拉選單，點擊下去，然後按下綠色的 **「Run workflow」** 按鈕。
4. 等個大概 10 秒鐘，你會看到下方出現一個黃色圈圈正在跑的任務，點進去。
5. 再點擊 **「run-scraper」**，展開 **「執行 Python 腳本」** 那個步驟的黑色框框（終端機畫面）。

去看看那個黑色框框裡面，是不是成功印出了股癌最新一集的標題和 `.mp3` 結尾的網址？確認有抓到後跟我說，我們就準備進入最核心的「轉逐字稿」環節！
