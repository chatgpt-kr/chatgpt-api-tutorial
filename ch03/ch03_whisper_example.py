import openai

#API 키 입력
openai.api_key = “api_key”
# 녹음파일 열기
audio_file = open("음원파일 이름", "rb")
# whisper 모델에 음원파일 넣기
transcript = openai.Audio.transcribe("whisper-1", audio_file)
#결과 보기
print(transcript)