import os
import json
import subprocess
from datetime import datetime

def main():
    # スクリプトがあるディレクトリを基準にする
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    history_file = "history.json"
    
    if not os.path.exists(history_file):
        print(f"エラー: {history_file} が見つかりません。")
        return
        
    with open(history_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # status が "queued" になっている最初の投稿（最古のもの）を探す
    target_post = None
    target_index = -1
    
    for i, post in enumerate(data.get("posts_queue", [])):
        if post.get("status") == "queued":
            target_post = post
            target_index = i
            break
            
    if not target_post:
        print("未投稿のストック（queued）がありません。すべての投稿が完了しています。")
        return
        
    day_num = target_post["day"]
    filename = f"post_day{day_num}.md"
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Day {day_num}の自動投稿を開始します: {filename}")
    
    # auto_post.py を自動実行する
    try:
        # ターミナルで実行するのと同じようにコマンドを呼び出す
        result = subprocess.run(["python", "auto_post.py", filename], check=True, capture_output=True, text=True)
        print("--- 実行結果 ---")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"自動投稿中にエラーが発生しました:\n{e.stderr}\n{e.stdout}")
        return # 失敗した場合は history.json を更新しない
        
    # 完全に成功したらステータスを "posted" に更新する
    data["posts_queue"][target_index]["status"] = "posted"
    data["posts_queue"][target_index]["posted_date"] = datetime.now().isoformat()
    
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"\nDay {day_num} の投稿が完了し、完了マークをつけました！")

if __name__ == "__main__":
    main()
