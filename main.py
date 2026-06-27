import os
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import psycopg2 # クラウドデータベース（PostgreSQL）に接続するための道具

app = FastAPI()

# GitHub Pagesからのアクセスを許可する魔法の鍵（CORS解除）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# クラウドデータベースへの接続URL（後でSupabaseから取得してセットします）
DATABASE_URL = os.environ.get("DATABASE_URL")

@app.get("/search")
def search_backend(q: str = Query(..., min_length=1)):
    """世界中からの検索リクエストを受け取り、クラウドの1億件データから一瞬で探す窓口"""
    if not DATABASE_URL:
        return {"results": [{"title": "エラー", "url": "#", "text": "データベースの設定が完了していません。"}], "count": 0}

    try:
        # クラウドの巨大データベースに接続
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # 1億件をフリーズさせずに一瞬で検索するSQL文（インデックス付き部分一致検索）
        search_query = f"%{q}%"
        cursor.execute("""
            SELECT url, title, body FROM pages 
            WHERE title ILIKE %s OR body ILIKE %s 
            LIMIT 30
        """, (search_query, search_query))
        
        rows = cursor.fetchall()
        conn.close()
        
        # 検索画面（JavaScript）にデータをきれいに整えて返す
        results = [{"url": r[0], "title": r[1], "text": r[2][:150]} for r in rows]
        return {"results": results, "count": len(results)}

    except Exception as e:
        return {"results": [], "count": 0, "error": str(e)}
