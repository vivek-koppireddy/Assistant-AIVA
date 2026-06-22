"""AIVA launcher module.

This file runs the desktop assistant when executed normally.
This project is configured to run as a Windows/desktop assistant.
"""
import speech_recognition as sr
import pyttsx3
import datetime
from commands import process_command

print("Starting AIVA (desktop)...")

engine = pyttsx3.init()

def speak(text):
    print("AIVA:", text)
    engine.say(text)
    engine.runAndWait()

def greet():
    hour = datetime.datetime.now().hour

    if hour < 12:
        speak("Good Morning. I am AIVA")
    elif hour < 18:
        speak("Good Afternoon. I am AIVA")
    else:
        speak("Good Evening. I am AIVA")

    speak("How can I help you?")

def listen():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        recognizer.pause_threshold = 1
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio)
        print("You said:", command)
        return command.lower()

    except sr.RequestError as e:
        print("RequestError:", e)
        try:
            command = recognizer.recognize_sphinx(audio)
            print("You said (offline):", command)
            return command.lower()
        except Exception as fallback_error:
            print("Offline recognition failed:", fallback_error)
            speak("I couldn't connect to the speech service and offline recognition is unavailable.")
            return ""

    except sr.UnknownValueError:
        print("Could not understand audio")
        speak("I didn't catch that. Please say it again.")
        return ""

    except Exception as e:
        print("Error:", e)
        speak("I am sorry, something went wrong while listening.")
        return ""

def main():
    greet()

    while True:
        command = listen()

        if not command:
            continue

        if "stop aiva" in command or "stop" in command or "quit" in command or "exit" in command:
            speak("Goodbye")
            break

        process_command(command, speak)

if __name__ == "__main__":
    main()
