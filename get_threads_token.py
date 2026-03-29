import urllib.parse
import requests
import sys

def main():
    print("="*50)
    print("=== Threads API アクセストークン取得ツール ===")
    print("="*50)
    
    app_id = input("\n1. アプリID を入力してください: ").strip()
    app_secret = input("2. app secret（アプリシークレット）を入力してください: ").strip()
    
    if not app_id or not app_secret:
        print("エラー: アプリIDとapp secretは必須です。")
        sys.exit(1)
        
    redirect_uri = "https://localhost/"
    
    # 1. 認証URLの生成
    auth_url = (
        f"https://threads.net/oauth/authorize"
        f"?client_id={app_id}"
        f"&redirect_uri={urllib.parse.quote(redirect_uri, safe='')}"
        f"&scope=threads_basic,threads_content_publish,threads_manage_replies"
        f"&response_type=code"
    )
    
    print("\n" + "-"*50)
    print("【アクションが必要です】")
    print("以下のURLをコピーして、ご自身のブラウザのURLバーに貼り付けてアクセスしてください。")
    print("-"*50)
    print(auth_url)
    print("-"*50)
    print("\n※アクセス後、「[アプリ名]が情報へのアクセスを求めています」と出るので「アクセスを許可」をクリックします。")
    print("※すると、「このサイトにアクセスできません」というエラー画面（https://localhost/...）に飛びますが、それが正常です。")
    print("※そのエラー画面の【一番上のURL（アドレスバーの文字列全体）】をすべてコピーして、以下に貼り付けてください。\n")
    
    redirected_url = input("ここにリダイレクト後のURLを貼り付け（Enterで確定）: ").strip()
    
    # URLから「code=...」を抽出
    try:
        parsed_url = urllib.parse.urlparse(redirected_url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        code = query_params.get("code", [None])[0]
        
        # Meta特有のゴミ（#_）が末尾につく場合があるので除去
        if code and code.endswith("#_"):
            code = code[:-2]
            
        if not code:
            raise ValueError("URLの中から 'code=' が見つかりませんでした。入力されたURLを確認してください。")
    except Exception as e:
        print(f"\nエラー: {e}")
        sys.exit(1)
        
    print("\n✓ 認証コードを取得しました。アクセストークンと交換・通信中...")
    
    # 2. 短期アクセストークンの取得
    token_url = "https://graph.threads.net/oauth/access_token"
    payload = {
        "client_id": app_id,
        "client_secret": app_secret,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
        "code": code
    }
    
    response = requests.post(token_url, data=payload)
    if response.status_code != 200:
        print(f"\nエラーが発生しました。取得に失敗しました:\n{response.text}")
        sys.exit(1)
        
    token_data = response.json()
    short_token = token_data.get("access_token")
    user_id = token_data.get("user_id")
    
    print(f"✓ 短期アクセストークンを取得しました。(ユーザーID: {user_id})")
    print("続いて運用に必須な【長期トークン（60日有効）】へ自動変換します...")
    
    # 3. 長期アクセストークンの取得
    long_token_url = "https://graph.threads.net/access_token"
    long_payload = {
        "grant_type": "th_exchange_token",
        "client_secret": app_secret,
        "access_token": short_token
    }
    
    long_response = requests.get(long_token_url, params=long_payload)
    if long_response.status_code != 200:
        print(f"\n長期トークンの取得に失敗しました:\n{long_response.text}")
        print(f"とりあえず短期トークンを表示します:\n{short_token}")
        sys.exit(1)
        
    long_token_data = long_response.json()
    long_token = long_token_data.get("access_token")
    
    print("\n" + "="*50)
    print("🎉 アクセストークン（長期）の取得に完全成功しました！")
    print("="*50)
    print(f"\n{long_token}\n")
    print("="*50)
    print("※この長〜い文字列が「自動投稿」に必須となる鍵（トークン）です。")
    print("パスワードと同じくらい大事なものなので、誰にも教えず、安全な場所にコピーして保存してください。")

if __name__ == "__main__":
    main()
