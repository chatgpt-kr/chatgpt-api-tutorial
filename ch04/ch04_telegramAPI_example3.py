import urllib3
import json

BOT_TOKEN = 'Bot Token'

def send_Photo(chat_id, image_url):
    data = {
        'chat_id': chat_id,
        'photo': image_url,
    }
    http = urllib3.PoolManager()
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    response = http.request('POST',url ,fields=data)
    return json.loads(response.data.decode('utf-8'))

result = send_Photo(1613810898,"https://wikibook.co.kr/images/cover/s/9791158394264.jpg")

print(result)