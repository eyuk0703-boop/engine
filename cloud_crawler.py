import json
import os
import urllib.parse
import requests
from bs4 import BeautifulSoup

# スタート地点（ここからリンクをたどって無限に広がります）
START_URL = "https://yahoo.co.jp"
MAX_PAGES = 15  # 1回の巡回で集めるページ数（最初は安全のため15ページに制限）
JSON_FILE = "search-index.json"

def run_crawler():
    # 既存のデータを読み込む（これまでに集めたデータと合流させる）
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            try:
                database = json.load(f)
            except:
                database = []
    else:
        database = []

    # すでに保存済みのURLをリスト化して重複を防ぐ
    saved_urls = {page["url"] for page in database}
    
    crawl_queue = [START_URL]
    visited_urls = set()
    new_pages = []

    print("🕸️ クラウドクローラー起動。インターネットの巡回を開始します...")

    while crawl_queue and len(new_pages) < MAX_PAGES:
        url = crawl_queue.pop(0)
        if url in visited_urls or url in saved_urls:
            continue

        visited_urls.add(url)

        try:
            headers = {"User-Agent": "MyCloudSearchBot/1.0"}
            response = requests.get(url, headers=headers, timeout=5)
            if "text/html" not in response.headers.get("Content-Type", ""):
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.string.strip() if soup.title and soup.title.string else "No Title"
            
            # 不要なノイズをカット
            for script in soup(["script", "style"]):
                script.decompose()
            body_text = soup.get_text(separator=" ", strip=True)[:300] # 文字数を300文字に抑えて節約

            # 新しいデータとして追加
            new_pages.append({
                "title": title,
                "url": url,
                "text": body_text
            })
            saved_urls.add(url)

            # 次のリンクを見つける
            for a_tag in soup.find_all("a", href=True):
                full_url = urllib.parse.urljoin(url, a_tag["href"])
                if full_url.startswith("http") and full_url not in saved_urls:
                    crawl_queue.append(full_url)

        except Exception as e:
            print(f"スキップ: {url} | 原因: {e}")

    # データを合体して保存
    database.extend(new_pages)
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(database, f, ensure_ascii=False, indent=2)
        
    print(f"✨ 完了！新しく {len(new_pages)} 件のサイトをデータベースに追加しました。")

if __name__ == "__main__":
    run_crawler()
