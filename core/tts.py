import pyttsx3
import threading

def init_engine(language_keywords=None, rate=150, volume=1.0):
    e = pyttsx3.init()
    e.setProperty('rate', rate)
    e.setProperty('volume', volume)

    if language_keywords:
        voices = e.getProperty('voices')
        matched_voice = None
        for v in voices:
            vid_lower = v.id.lower()
            if any(keyword in vid_lower for keyword in language_keywords):
                matched_voice = v
                break
        if matched_voice:
            e.setProperty('voice', matched_voice.id)
            print(f"[INFO] 已切换到语音: {matched_voice.id}")
        else:
            print("[WARN] 系统中未找到匹配的日语语音，将使用默认语音。")
    return e

engine = init_engine(language_keywords=["ja", "jpn"], rate=150, volume=1.0)

def _speak(text):
    engine.say(text)
    engine.runAndWait()

def speak(text):
    t = threading.Thread(target=_speak, args=(text,))
    t.start()
