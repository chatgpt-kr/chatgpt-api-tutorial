import urllib3
import json
import openai
import os

BOT_TOKEN = os.environ['TELE_TOKEN']
openai.api_key = os.environ['OPENAI_API']

def lambda_handler(event, context):
    
    result = json.loads(event['body'])
    
    if not result['message']['from']['is_bot']:
                    
        # �޼����� ���� ����� chat ID 
        chat_id = str(result['message']['chat']['id'])

        # �ش� �޼����� ID
        msg_id = str(int(result['message']['message_id']))
                
        # ���� �׸� ������ ��û�ϸ�
        if '/img' in result['message']['text']:
            prompt = result['message']['text'].replace("/img", "")
            # DALL.E 2�κ��� ������ �̹��� URL �ޱ�
            bot_response = getImageURLFromDALLE(prompt)
            # �̹��� �ڷ��׷� �濡 ������
            print(send_Photo(chat_id,bot_response, msg_id))
        # ���� chatGPT�� �亯�� ��û�ϸ�
        if '/ask' in result['message']['text']:
            prompt = result['message']['text'].replace("/ask", "")
            # ChatGPT�κ��� �亯 �ޱ�
            bot_response = getTextFromGPT(prompt)
            # �亯 �ڷ��׷� �濡 ������
            print(send_message(chat_id, bot_response,msg_id))
    
    return 0

###### ��� �Լ� ���� �ܰ� ######

# �޼��� ����
def send_message(chat_id, text,msg_id):
    data = {
        'chat_id': chat_id,
        'text': text,
        'reply_to_message_id': msg_id
    }
    http = urllib3.PoolManager()
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    response = http.request('POST',url ,fields=data)
    return json.loads(response.data.decode('utf-8'))

# ���� ����
def send_Photo(chat_id, image_url,msg_id):
    data = {
        'chat_id': chat_id,
        'photo': image_url,
        'reply_to_message_id': msg_id
    }
    http = urllib3.PoolManager()
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    response = http.request('POST',url ,fields=data)
    return json.loads(response.data.decode('utf-8'))

# ä�ù� ���� Ȯ��/ ä�� �ޱ�
def get_updates(last_update):
    http = urllib3.PoolManager()
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={last_update}"
    response = http.request('GET', url)
    return json.loads(response.data.decode('utf-8'))

# ChatGPT���� ����/�亯�ޱ�
def getTextFromGPT(messages):
    messages_prompt = [{"role": "system", "content": 'You are a thoughtful assistant. Respond to all input in 25 words and answer in korea'}]
    messages_prompt += [{"role": "system", "content": messages}]
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages_prompt)

    system_message = response["choices"][0]["message"]

    return system_message["content"]

# DALLE.2���� ����/�׸� URL �ޱ�
def getImageURLFromDALLE(messages):
    
    response = openai.Image.create(prompt=messages,n=1,size="512x512")

    image_url = response['data'][0]['url']

    return image_url
