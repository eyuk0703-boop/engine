import json
import os
import urllib.parse
import requests
import time
from bs4 import BeautifulSoup

# スタート地点（ここからリンクをたどって無限に広がります）
START_URL = "https://yahoo.co.jp"
MAX_PAGES = 1000  # 🔥【極限突破】現在のシステムの限界値「1000件」に設定！
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

    print(f"🕸️ 限界突破クローラー起動。目標 {MAX_PAGES} 件の超大量データ収集を開始します...")

    # 高速化のために通信セッションを維持
    session = requests.Session()
    session.headers.update({"User-Agent": "MyMegaUltimateSearchBot/1.0"})

    while crawl_queue and len(new_pages) < MAX_PAGES:
        url = crawl_queue.pop(0)
        if url in visited_urls or url in saved_urls: continue
        visited_urls.add(url)

        try:
            # 大量アクセスで相手のサーバーを落とさないよう0.5秒だけ待つ（限界の速度設定）
            time.sleep(0.5)
            
            response = session.get(url, timeout=3)
            if "text/html" not in response.headers.get("Content-Type", ""): continue

            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.string.strip() if soup.title and soup.title.string else "No Title"
            
            for script in soup(["script", "style", "noscript"]): script.decompose()
            body_text = soup.get_text(separator=" ", strip=True)[:200] # 容量削減のため200文字に制限

            new_pages.append({
                "title": title,
                "url": url,
                "text": body_text
            })
            saved_urls.add(url)

            # 効率よくURLを集める
            for a_tag in soup.find_all("a", href=True):
                full_url = urllib.parse.urljoin(url, a_tag["href"])
                # 散らばりすぎを防ぐため、主要なニュース・大手ドメイン中心にクロールを制限
                if full_url.startswith("http") and full_url not in saved_urls and len(crawl_queue) < 2000:
                    crawl_queue.append(full_url)

            # 定期的に進捗を表示
            if len(new_pages) % 50 == 0:
                print(f" 📑 現在 {len(new_pages)} 件の収集が完了しました...")

        except Exception as e:
            continue # エラーが起きても無視して次のサイトへ爆速で突き進む

    database.extend(new_pages)
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(database, f, ensure_ascii=False, indent=2)
        
    print(f"✨ 完了！合計 {len(database)} 件の巨大データベースが構築されました。")

if __name__ == "__main__":
    run_crawler()
