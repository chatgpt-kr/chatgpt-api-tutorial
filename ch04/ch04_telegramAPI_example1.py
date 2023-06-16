import urllib3
import json

BOT_TOKEN = 'Bot Token'

def get_updates():
    http = urllib3.PoolManager()
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    response = http.request('GET', url)
    return json.loads(response.data.decode('utf-8'))

# Get the latest updates
updates = get_updates()

print(updates)