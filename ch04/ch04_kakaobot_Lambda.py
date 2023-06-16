###### �⺻ ���� ���� �ܰ� #######
import json
import openai
import threading
import time
import queue as q
import os

# OpenAI API KEY
openai.api_key = os.environ['OPENAI_API']

###### ���� �Լ� �ܰ� #######

# ���� �Լ�
def lambda_handler(event, context):

    run_flag = False
    start_time = time.time()
    # īī�� ���� ����
    kakaorequest = json.loads(event['body'])
    # ���� ����� �����ϱ� ���� �ؽ�Ʈ ���� ����
    cwd = os.getcwd()
    filename = cwd + "/tmp/botlog.txt"
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            f.write("")
    else:
        print("File Exists")    

    # �亯 ���� �Լ� ����
    response_queue = q.Queue()
    request_respond = threading.Thread(target=responseOpenAI,
                                        args=(kakaorequest, response_queue,filename))
    request_respond.start()

    # �亯 ���� �ð� üũ
    while (time.time() - start_time < 3.5):
        if not response_queue.empty():
            # 3.5�� �ȿ� �亯�� �ϼ��Ǹ� �ٷ� �� ����
            response = response_queue.get()
            run_flag= True
            break
        # �������� ������ ���� ������ Ÿ�� ����
        time.sleep(0.01)

    # 3.5�� �� �亯�� �������� ���� ���
    if run_flag== False:     
        response = timeover()

    return{
        'statusCode':200,
        'body': json.dumps(response),
        'headers': {
            'Access-Control-Allow-Origin': '*',
        }
    }

# �亯/���� ��û �� ���� Ȯ�� �Լ�
def responseOpenAI(request,response_queue,filename):
    # ����ڴ� ��ư�� Ŭ���Ͽ� �亯 �ϼ� ���θ� �ٽ� ���� ��
    if '���� �� ��������?' in request["userRequest"]["utterance"]:
        # �ؽ�Ʈ ���� ����
        with open(filename) as f:
            last_update = f.read()
        # �ؽ�Ʈ ���� �� ����� ������ ���� ���
        if len(last_update.split())>1:
            kind, bot_res, prompt = last_update.split()[0],last_update.split()[1],last_update.split()[2]  
            if kind == "img":
                response_queue.put(imageResponseFormat(bot_res,prompt))
            else:
                response_queue.put(textResponseFormat(bot_res))
            dbReset(filename)

    # �̹��� ������ ��û�� ���
    elif '/img' in request["userRequest"]["utterance"]:
        dbReset(filename)
        prompt = request["userRequest"]["utterance"].replace("/img", "")
        bot_res = getImageURLFromDALLE(prompt)
        response_queue.put(imageResponseFormat(bot_res,prompt))
        save_log = "img"+ " " + str(bot_res) + " " + str(prompt)
        with open(filename, 'w') as f:
            f.write(save_log)

    # ChatGPT �亯�� ��û�� ���
    elif '/ask' in request["userRequest"]["utterance"]:
        dbReset(filename)
        prompt = request["userRequest"]["utterance"].replace("/ask", "")
        bot_res = getTextFromGPT(prompt)
        response_queue.put(textResponseFormat(bot_res))

        save_log = "ask"+ " " + str(bot_res) + " " + str(prompt)
        with open(filename, 'w') as f:
            f.write(save_log)
            
    #�ƹ� �亯 ��û�� ���� ä���� ���
    else:
        # �⺻ response ��
        base_response = {'version': '2.0', 'template': {'outputs': [], 'quickReplies': []}}
        response_queue.put(base_response)

###### ��� ���� �ܰ� #######

# �޼��� ����
def textResponseFormat(bot_response):
    response = {'version': '2.0', 'template': {
    'outputs': [{"simpleText": {"text": bot_response}}], 'quickReplies': []}}
    return response

# ���� ����
def imageResponseFormat(bot_response,prompt):
    output_text = prompt+"���뿡 ���� �̹��� �Դϴ�"
    response = {'version': '2.0', 'template': {
    'outputs': [{"simpleImage": {"imageUrl": bot_response,"altText":output_text}}], 'quickReplies': []}}
    return response

# ���� �ʰ��� �亯
def timeover():
    response = {"version":"2.0","template":{
      "outputs":[
         {
            "simpleText":{
               "text":"���� ���� ������ ������ �ʾҾ��??\n����� �Ʒ� ��ǳ���� �����ּ���?"
            }
         }
      ],
      "quickReplies":[
         {
            "action":"message",
            "label":"���� �� ��������??",
            "messageText":"���� �� ��������?"
         }]}}
    return response

# ChatGPT���� ����/�亯 �ޱ�
def getTextFromGPT(prompt):
    messages_prompt = [{"role": "system", "content": 'You are a thoughtful assistant. Respond to all input in 25 words and answer in korea'}]
    messages_prompt += [{"role": "system", "content": prompt}]
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages_prompt)
    message = response["choices"][0]["message"]["content"]
    return message

# DALLE.2���� ����/�׸� URL �ޱ�
def getImageURLFromDALLE(prompt):
    response = openai.Image.create(prompt=prompt,n=1,size="512x512")
    image_url = response['data'][0]['url']
    return image_url

# �ؽ�Ʈ���� �ʱ�ȭ
def dbReset(filename):
    with open(filename, 'w') as f:
        f.write("")

