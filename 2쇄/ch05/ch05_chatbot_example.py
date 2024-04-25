import os
import pandas as pd
import numpy as np
from numpy import dot
from numpy.linalg import norm
import ast
import openai
import streamlit as st
from streamlit_chat import message

client = openai.OpenAI(api_key = "사용자의 OpenAI API Key 값")

def get_embedding(text):
    response = client.embeddings.create(
        input=text,
        model='text-embedding-ada-002'
    )
    return response.data[0].embedding

# folder_path와 file_name을 결합하여 file_path = './data/embedding.csv'
folder_path = './data'
file_name = 'embedding.csv'
file_path = os.path.join(folder_path, file_name)

# if: embedding.csv가 이미 존재한다면 데이터프레임 df로 로드한다.
if os.path.isfile(file_path):
    print(f"{file_name} 파일이 존재합니다.")
    df = pd.read_csv(file_path)
    df['embedding'] = df['embedding'].apply(ast.literal_eval)

# 그렇지 않다면 text열과 embedding열이 존재하는 df를 신규 생성해야한다.
else:
    # 57개의 서울 청년 정책 txt 파일명을 txt_files에 저장한다.
    txt_files = [file for file in os.listdir(folder_path) if file.endswith('.txt')]

    data = []
    # txt_files로부터 57개의 청년 정책 데이터를 로드하여 df를 신규 생성한다.
    for file in txt_files:
        file_path = os.path.join(folder_path, file)
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            data.append(text)

    df = pd.DataFrame(data, columns=['text'])

    # 데이터프레임의 text 열로부터 embedding열을 생성한다.
    df['embedding'] = df.apply(lambda row: get_embedding(
        row.text,
    ), axis=1)

    # 추후 사용을 위해 df를 'embedding.csv' 파일로 저장한다.
    # 이렇게 저장되면 추후 실행에서는 df를 새로 만드는 과정을 생략한다.
    df.to_csv(file_path, index=False, encoding='utf-8-sig')

# 주어진 질의로부터 유사한 문서 개를 반환하는 검색 시스템.
# 함수 return_answer_candidate내부에서 유사도 계산을 위해 cos_sim을 호출.
def cos_sim(A, B):
    return dot(A, B)/(norm(A)*norm(B))

def return_answer_candidate(df, query):
    query_embedding = get_embedding(query)
    df["similarity"] = df.embedding.apply(lambda x: cos_sim(np.array(x), np.array(query_embedding)))
    top_three_doc = df.sort_values("similarity", ascending=False).head(3)
    return top_three_doc

# 챗봇의 답변을 만들기 위해 사용될 프롬프트를 만드는 함수.
def create_prompt(df, query):
    result = return_answer_candidate(df, query)
    system_role = f"""You are an artificial intelligence language model named "정채기" that specializes in summarizing \
    and answering documents about Seoul's youth policy, developed by developers 유원준 and 안상준.
    You need to take a given document and return a very detailed summary of the document in the query language.
    Here are the document: 
            doc 1 :{str(result.iloc[0]['text'])}
            doc 2 :{str(result.iloc[1]['text'])}
            doc 3 :{str(result.iloc[2]['text'])}
    You must return in Korean. Return a accurate answer based on the document.
    """
    user_content = f"""User question: "{str(query)}". """

    messages = [
        {"role": "system", "content": system_role},
        {"role": "user", "content": user_content}
    ] 
    return messages

# 위의 create_prompt 함수가 생성한 프롬프트로부터 챗봇의 답변을 만드는 함수.
def generate_response(messages):
    result = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.4,
        max_tokens=500)
    return result.choices[0].message.content

st.image('images/ask_me_chatbot.png')

# 화면에 보여주기 위해 챗봇의 답변을 저장할 공간 할당
if 'generated' not in st.session_state:
    st.session_state['generated'] = []

# 화면에 보여주기 위해 사용자의 답변을 저장할 공간 할당
if 'past' not in st.session_state:
    st.session_state['past'] = []

# 사용자의 입력이 들어오면 user_input에 저장하고 Send 버튼을 클릭하면
# submitted의 값이 True로 변환.
with st.form('form', clear_on_submit=True):
    user_input = st.text_input('정책을 물어보세요!', '', key='input')
    submitted = st.form_submit_button('Send')

# submitted의 값이 True면 챗봇이 답변을 하기 시작
if submitted and user_input:
    # 프롬프트 생성
    prompt = create_prompt(df, user_input)
    # 생성한 프롬프트를 기반으로 챗봇 답변을 생성
    chatbot_response = generate_response(prompt)
    # 화면에 보여주기 위해 사용자의 질문과 챗봇의 답변을 각각 저장
    st.session_state['past'].append(user_input)
    st.session_state['generated'].append(chatbot_response)

# 사용자의 질문과 챗봇의 답변을 순차적으로 화면에 출력
if st.session_state['generated']:
    for i in reversed(range(len(st.session_state['generated']))):
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
        message(st.session_state['generated'][i], key=str(i))