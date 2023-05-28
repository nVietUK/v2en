import speech_recognition as sr

def listen():
    recognizer = sr.Recognizer();

    with sr.Microphone() as source:
        recognizer.pause_threshold = 1
        audio = recognizer.listen(source)
    
    try:
        output = recognizer.recognize_google(audio, language="vi-vn")
    except Exception as error:
        print(error)
        return "Error"

    return output

def main():
    sentence = listen()
    print(sentence)

    return 0

main()