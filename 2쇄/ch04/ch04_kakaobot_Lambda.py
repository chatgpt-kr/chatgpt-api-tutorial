###### 기본 정보 설정 단계 #######
import json
import openai
import threading
import time
import queue as q
import os

# OpenAI API KEY
client = openai.OpenAI(api_key = os.environ['OPENAI_API'])

###### 메인 함수 단계 #######

# 메인 함수
def lambda_handler(event, context):

    run_flag = False
    start_time = time.time()
    # 카카오 정보 저장
    kakaorequest = json.loads(event['body'])
    # 응답 결과를 저장하기 위한 텍스트 파일 생성

    filename ="/tmp/botlog.txt"
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            f.write("")
    else:
        print("File Exists")    

    # 답변 생성 함수 실행
    response_queue = q.Queue()
    request_respond = threading.Thread(target=responseOpenAI,
                                        args=(kakaorequest, response_queue,filename))
    request_respond.start()

    # 답변 생성 시간 체크
    while (time.time() - start_time < 3.5):
        if not response_queue.empty():
            # 3.5초 안에 답변이 완성되면 바로 값 리턴
            response = response_queue.get()
            run_flag= True
            break
        # 안정적인 구동을 위한 딜레이 타임 설정
        time.sleep(0.01)

    # 3.5초 내 답변이 생성되지 않을 경우
    if run_flag== False:     
        response = timeover()

    return{
        'statusCode':200,
        'body': json.dumps(response),
        'headers': {
            'Access-Control-Allow-Origin': '*',
        }
    }

# 답변/사진 요청 및 응답 확인 함수
def responseOpenAI(request,response_queue,filename):
    # 사용자다 버튼을 클릭하여 답변 완성 여부를 다시 봤을 시
    if '생각 다 끝났나요?' in request["userRequest"]["utterance"]:
        # 텍스트 파일 열기
        with open(filename) as f:
            last_update = f.read()
        # 텍스트 파일 내 저장된 정보가 있을 경우
        if len(last_update.split())>1:
            kind = last_update.split()[0]  
            if kind == "img":
                bot_res, prompt = last_update.split()[1],last_update.split()[2]
                response_queue.put(imageResponseFormat(bot_res,prompt))
            else:
                bot_res = last_update[4:]
                response_queue.put(textResponseFormat(bot_res))
            dbReset(filename)

    # 이미지 생성을 요청한 경우
    elif '/img' in request["userRequest"]["utterance"]:
        dbReset(filename)
        prompt = request["userRequest"]["utterance"].replace("/img", "")
        bot_res = getImageURLFromDALLE(prompt)
        response_queue.put(imageResponseFormat(bot_res,prompt))
        save_log = "img"+ " " + str(bot_res) + " " + str(prompt)
        with open(filename, 'w') as f:
            f.write(save_log)

    # ChatGPT 답변을 요청한 경우
    elif '/ask' in request["userRequest"]["utterance"]:
        dbReset(filename)
        prompt = request["userRequest"]["utterance"].replace("/ask", "")
        bot_res = getTextFromGPT(prompt)
        response_queue.put(textResponseFormat(bot_res))

        save_log = "ask"+ " " + str(bot_res)
        with open(filename, 'w') as f:
            f.write(save_log)
            
    #아무 답변 요청이 없는 채팅일 경우
    else:
        # 기본 response 값
        base_response = {'version': '2.0', 'template': {'outputs': [], 'quickReplies': []}}
        response_queue.put(base_response)

###### 기능 구현 단계 #######

# 메세지 전송
def textResponseFormat(bot_response):
    response = {'version': '2.0', 'template': {
    'outputs': [{"simpleText": {"text": bot_response}}], 'quickReplies': []}}
    return response

# 사진 전송
def imageResponseFormat(bot_response,prompt):
    output_text = prompt+"내용에 관한 이미지 입니다"
    response = {'version': '2.0', 'template': {
    'outputs': [{"simpleImage": {"imageUrl": bot_response,"altText":output_text}}], 'quickReplies': []}}
    return response

# 응답 초과시 답변
def timeover():
    response = {"version":"2.0","template":{
      "outputs":[
         {
            "simpleText":{
               "text":"아직 제가 생각이 끝나지 않았어요??\n잠시후 아래 말풍선을 눌러주세요?"
            }
         }
      ],
      "quickReplies":[
         {
            "action":"message",
            "label":"생각 다 끝났나요??",
            "messageText":"생각 다 끝났나요?"
         }]}}
    return response

# ChatGPT에게 질문/답변 받기
def getTextFromGPT(messages):
    messages_prompt = [{"role": "system", "content": 'You are a thoughtful assistant. Respond to all input in 25 words and answer in korea'}]
    messages_prompt += [{"role": "user", "content": messages}]
    response = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages_prompt)
    message = response.choices[0].message.content
    return message

# DALLE 에게 질문/그림 URL 받기
def getImageURLFromDALLE(messages):   
    response = client.images.generate(
    model="dall-e-2",
    prompt=messages,
    size="512x512",
    quality="standard",
    n=1)
    image_url = response.data[0].url
    return image_url

# 텍스트파일 초기화
def dbReset(filename):
    with open(filename, 'w') as f:
        f.write("")

