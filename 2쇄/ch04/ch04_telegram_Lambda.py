import urllib3
import json
import openai
import os

#OpenAI API 키 입력 및 클라이언트 생성
client = openai.OpenAI(api_key = os.environ['OPENAI_API'])

# 텔레그램 봇 토큰
BOT_TOKEN = os.environ['TELE_TOKEN']

###### 메인함수 구현 단계 ######
def lambda_handler(event, context):
    
    result = json.loads(event['body'])
    
    if not result['message']['from']['is_bot']:
                    
        # 메세지를 보낸 사람의 chat ID 
        chat_id = str(result['message']['chat']['id'])

        # 해당 메세지의 ID
        msg_id = str(int(result['message']['message_id']))
                
        # 만약 그림 생성을 요청하면
        if '/img' in result['message']['text']:
            prompt = result['message']['text'].replace("/img", "")
            # DALL.E로부터 생성한 이미지 URL 받기
            bot_response = getImageURLFromDALLE(prompt)
            # 이미지 텔레그램 방에 보내기
            print(sendPhoto(chat_id,bot_response, msg_id))
        # 만약 chatGPT의 답변을 요청하면
        if '/ask' in result['message']['text']:
            prompt = result['message']['text'].replace("/ask", "")
            # ChatGPT로부터 답변 받기
            bot_response = getTextFromGPT(prompt)
            # 답변 텔레그램 방에 보내기
            print(sendMessage(chat_id, bot_response,msg_id))
    
    return 0

###### 기능 함수 구현 단계 ######

# 메세지 전송
def sendMessage(chat_id, text,msg_id):
    data = {
        'chat_id': chat_id,
        'text': text,
        'reply_to_message_id': msg_id
    }
    http = urllib3.PoolManager()
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    response = http.request('POST',url ,fields=data)
    return json.loads(response.data.decode('utf-8'))

# 사진 전송
def sendPhoto(chat_id, image_url,msg_id):
    data = {
        'chat_id': chat_id,
        'photo': image_url,
        'reply_to_message_id': msg_id
    }
    http = urllib3.PoolManager()
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    response = http.request('POST',url ,fields=data)
    return json.loads(response.data.decode('utf-8'))

# ChatGPT에게 질문/답변받기
def getTextFromGPT(messages):
    messages_prompt = [{"role": "system", "content": 'You are a thoughtful assistant. Respond to all input in 25 words and answer in korea'}]
    messages_prompt += [{"role": "user", "content": messages}]
    response = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages_prompt)
    system_message = response.choices[0].message.content
    return system_message

# DALLE 에게 질문/그림 URL 받기
def getImageURLFromDALLE(messages):   
    response = client.images.generate(
    model="dall-e-3",
    prompt=messages,
    size="1024x1024",
    quality="standard",
    n=1)
    image_url = response.data[0].url
    return image_url
