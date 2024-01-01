from gtts import gTTS

tts = gTTS(text="안녕하세요 음성비서 프로그램 실습중입니다.",lang="ko")
tts.save("output.mp3")
