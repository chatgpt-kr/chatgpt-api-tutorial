import urllib3
import json

BOT_TOKEN = 'Bot Token'

def sendMessage(chat_id, text):
    data = {
        'chat_id': chat_id,
        'text': text,
    }
    http = urllib3.PoolManager()
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    response = http.request('POST',url ,fields=data)
    return json.loads(response.data.decode('utf-8'))

result = sendMessage(1613810898,"반갑습니다 저는 텔레그램 봇 입니다!")

print(result)