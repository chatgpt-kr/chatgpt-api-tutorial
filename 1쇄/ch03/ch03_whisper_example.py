import openai

#API 키 입력
openai.api_key = "API Key"
# 녹음파일 열기
audio_file = open("output.mp3", "rb")
# whisper 모델에 음원파일 전달하기
transcript = openai.Audio.transcribe("whisper-1", audio_file)
#결과 보기
print(transcript["text"])