import json
import os
import urllib.parse
import requests
import time
from bs4 import BeautifulSoup

START_URL = "https://www.google.co.jp/"
MAX_PAGES = 1000  # 🚀 インターネットから1,000件の本物のサイトを自動収集！
JSON_FILE = "search-index.json"

def run_crawler():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            try: database = json.load(f)
            except: database = []
    else: database = []

    saved_urls = {page["url"] for page in database}
    crawl_queue = [START_URL]
    visited_urls = set()
    new_pages = []

    print(f"🚀 ネット全体から {MAX_PAGES} 件のリアルデータを集めます...")

    session = requests.Session()
    session.headers.update({"User-Agent": "MyUltimateSearchBot/2.0"})

    while crawl_queue and len(new_pages) < MAX_PAGES:
        url = crawl_queue.pop(0)
        if url in visited_urls or url in saved_urls: continue
        visited_urls.add(url)

        try:
            time.sleep(0.5) # 相手のサイトに迷惑をかけないマナー
            response = session.get(url, timeout=3)
            if "text/html" not in response.headers.get("Content-Type", ""): continue

            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.string.strip() if soup.title and soup.title.string else ""
            if not title or "エラー" in title or "404" in title: continue
            
            for script in soup(["script", "style", "noscript"]): script.decompose()
            body_text = soup.get_text(separator=" ", strip=True)[:200]

            # 本物のデータを格納！
            new_pages.append({
                "title": title,
                "url": url,
                "text": body_text
            })
            saved_urls.add(url)

            # ページ内のリンクを見つけて次の巡回先にする（これで無限に広がります）
            for a_tag in soup.find_all("a", href=True):
                full_url = urllib.parse.urljoin(url, a_tag["href"])
                if full_url.startswith("http") and full_url not in saved_urls and len(crawl_queue) < 1500:
                    crawl_queue.append(full_url)

            if len(new_pages) % 50 == 0:
                print(f" 📑 現在 {len(new_pages)} 件のサイトをインデックス化しました...")

        except: continue

    database.extend(new_pages)
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(database, f, ensure_ascii=False, indent=2)
    print(f"✨ 完了！ データベースに本物のサイトが蓄積されました。")

if __name__ == "__main__":
    run_crawler()
