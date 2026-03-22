#conda activate scraping_env
#which python

import requests
from bs4 import BeautifulSoup
import csv
import datetime
import time

#現在日時を取得し、定時に自動でシステムを起動し処理を行う関数
def auto_job (hour,minute,second):
    target_time = datetime.time(hour=hour,minute=minute,second=second)
    last_run_date = None

    while True:
        now = datetime.datetime.now()
        #combineで指定した時間とnowの日付を結合してdatetimeの形に整形
        target_date_time = datetime.datetime.combine(now.date(),target_time)
        
        if now >= target_date_time and last_run_date != now.date():
            print(f"システム実行中:{now}")
            main()
            #実行したらフラグ建てて、同日には実行しない
            last_run_date = now.date()

        #target_timeが当日の過去の時間になってしまうとdiffが常にマイナスになるので、日付を+1して回避する
        if now > target_date_time:
            target_date_time += datetime.timedelta(days=1)

        #.total_secondsで秒数換算での差を求める
        diff = (target_date_time - now).total_seconds()

        #target_timeの1時間前までは3600秒(60分)、1時間前からは60秒ごと、1分以内では5秒ごとにシステム試行
        if diff > 3600 : 
            sleep_time = 3600
        elif diff > 60 :
            sleep_time = 60
        else :
            sleep_time = 5

        print(f"待機中...{sleep_time}秒スリープ")
        print(f"次回実行予定:{target_date_time}")
        time.sleep(sleep_time)
    

#User-Agentを指定し、サーバーからのブロックを防ぐ
#User-Agent--> Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36

#サイト内情報リクエスト＆responseに取得内容を格納
#エラーが出たらエラー内容を表示して終了という関数
#url,headersそれぞれ調べたいサイトのurlとUseer-Agentを貼り付ける
def get_data(url,headers):
    try:
        response = requests.get(url,headers=headers)
        response.raise_for_status()
        return response
    #エラーが出たらeに格納-->出力
    except Exception as e :
        print("取得エラー:",e)
        return None
    #呼び出し側で必ず
    # if response is None:
    #   return
    #を忘れるな


#空のリストを用意して収集したデータを格納する関数
def parse_html(req,start=0,end=20) : 
    #set()を用いて重複データ除外
    seen = set()
    data = []
    soup = BeautifulSoup(req.text,"html.parser")

    for a in soup.find_all("a") :
        try:
            #.text.stripでtextを取り出して、空白を除去
            link = a.get("href")
            if link and "news.yahoo.co.jp" in link:
                title = a.text.strip()
                key = (title, link)
            
            #title,link,keyがseenになければ==データが重複していなければ実行
                if title and link and key not in seen:
             #データを重複確認用リストseenにも追加
                    seen.add(key)
                    data.append({"title":title,"url":link})
        except Exception as e :
            print("取得エラー:",e)
            continue
    return data[start:end]

def save_csv (collected_data,file_name):
    #file_nameの部分に指定するファイル名を代入
    with open(file_name,"w",newline="",encoding="utf-8") as f:
        writer = csv.DictWriter(f,fieldnames=["title","url"])
        writer.writeheader()
        writer.writerows(collected_data)


#実際に実行する関数
def main():
    url = "https://news.yahoo.co.jp/topics/top-picks"
    headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"}

    res = get_data(url,headers)
    if res is None:
        return
    
    data = parse_html(res,2,22)
    print(f"{len(data)}件取得しました")

    file_name = f"news_{datetime.date.today()}.csv"
    save_csv(data,file_name)
   

#毎日午前7:00に自動で実行
auto_job(7,00,00)