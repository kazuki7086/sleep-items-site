import os
import time
import requests
import argparse
import re

# ==========================================
# 🛑 ここに取得した長期アクセストークンを貼り付ける 🛑
# ==========================================
ACCESS_TOKEN = "THAA89mR1IWoBBUVJfUFJrWXcxeEpsZAzV4LVM0a0dqOXFJSEx0NTFzNkR6WnRRR25fZAFhyanNBN09wZAVJUcHk1Q0pFaXZA2ZAThWUml0V1hGVmU1ZAWN1dlhQa3U4VUFZATVlXRWhtOEtscFdZAT2FEZAHZAfYzF4cUlSTDhRZA1hhS3BMTEN5QQZDZD"


def create_container(text, reply_to_id=None):
    """
    Threadsに投稿データ（コンテナ）を作成する
    ※ まだこの段階では公開されません
    """
    url = "https://graph.threads.net/v1.0/me/threads"
    payload = {
        "media_type": "TEXT",
        "text": text,
        "access_token": ACCESS_TOKEN
    }
    
    # スレッド（返信）の場合
    if reply_to_id:
        payload["reply_to_id"] = reply_to_id
        
    print("  ... コンテナ（投稿データ）を作成中")
    response = requests.post(url, data=payload)
    
    if response.status_code != 200:
        print(f"  ❌ コンテナ作成エラー: {response.text}")
        return None
        
    return response.json().get("id")

def publish_container(container_id):
    """
    作成したコンテナを公開（実際にタイムラインに投稿）する
    """
    url = "https://graph.threads.net/v1.0/me/threads_publish"
    payload = {
        "creation_id": container_id,
        "access_token": ACCESS_TOKEN
    }
    print("  ... 投稿（公開）を実行中")
    response = requests.post(url, data=payload)
    
    if response.status_code != 200:
        print(f"  ❌ 公開エラー: {response.text}")
        return None
        
    return response.json().get("id")

def parse_markdown(filepath):
    """
    マークダウンファイルを読み込み、5つの投稿に分割する
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    # 「### O投目」を目印にして文章を分割
    parts = re.split(r'###\s*\d+投目', content)
    
    # 最初の部分はヘッダー（タイトルなど）なので除外して1投目以降を取得
    posts = []
    for part in parts[1:]:
        text = part.strip()
        if text:
            posts.append(text)
            
    return posts

def main():
    parser = argparse.ArgumentParser(description="Threads自動連続投稿スクリプト")
    parser.add_argument("filename", help="投稿するマークダウンファイルのパス (例: post_day1.md)")
    args = parser.parse_args()
    
    if ACCESS_TOKEN == "ここにトークンを貼り付ける" or not ACCESS_TOKEN:
        print("🛑 エラー: auto_post.py の 10行目 にアクセストークンを貼り付けてください！")
        return
        
    filepath = args.filename
    if not os.path.exists(filepath):
        print(f"🛑 ファイルが見つかりません: {filepath}")
        return
        
    posts = parse_markdown(filepath)
    if not posts:
        print("🛑 投稿内容が見つかりませんでした。「### 1投目」等の見出しになっているか確認してください。")
        return
        
    print(f"==================================================")
    print(f" 🚀 {filepath} から {len(posts)} 件の連続スレッド投稿を開始します")
    print(f"==================================================")
    
    previous_post_id = None
    
    for i, post_text in enumerate(posts):
        print(f"\n【{i+1}投目】を処理しています...")
        
        # 1. コンテナの作成（2投目以降は previous_post_id にぶら下げる）
        container_id = create_container(post_text, reply_to_id=previous_post_id)
        if not container_id:
            print(f"⚠️ {i+1}投目で失敗したため、処理を完全に中断します。")
            break
            
        # 2. コンテナの公開（実際に投稿される）
        # ※APIの処理安定化のために少し待機します
        time.sleep(2) 
        published_id = publish_container(container_id)
        
        if not published_id:
            print(f"⚠️ {i+1}投目の公開に失敗したため、処理を完全に中断します。")
            break
            
        print(f"  ✅ 成功！ (Post ID: {published_id})")
        # 次の投稿をぶら下げるためにIDを記憶
        previous_post_id = published_id 
        
        # 一気に投稿するとスパム判定される可能性があるため、少し待機
        if i < len(posts) - 1:
            time.sleep(10)  # 次の投稿が前回の投稿を認識できるよう、長めに待機
            
    print("\n🎉 すべての投稿プロセスが完了しました！ Threadsアプリを開いて確認してください🚀")

if __name__ == "__main__":
    main()
