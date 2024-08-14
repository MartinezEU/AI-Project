import threading
import random
import speech_recognition as sr
from datetime import datetime, timedelta
import functions
import sentences
import provider
import tkinter as tk
from tkinter import filedialog
import json
import os
from openai import OpenAI
import time
from pathlib import Path
import pygame
import traceback
import time

# Initialize OpenAI client
client = OpenAI(
    api_key=""
)

# Initialize microphone
recognizer = sr.Recognizer()

# AI configuration
ai_config = None
listening = True
# Set a reminder
reminders = []

def recognize_name():
    speak_text("I don't seem to have a name. Could you please tell me my name?")
    name = recognize_speech()
    if name:
        functions.create_ai_conversation_log(name)
        speak_text(f"My name is {name}.")
        ai_config['name'] = name
        return name
    else:
        speak_text("Sorry, I didn't catch your name. Could you please repeat?")
        return recognize_name()

def generate_response(user_input):
    useful_info = provider.get_useful_info()
    info_text = " ".join([f"{key.capitalize()}: {value}." for key, value in useful_info.items()])
    conversation = functions.load_conversation(ai_config['name'])

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": (
                f"You are {ai_config['name']}, {ai_config['description']} "
                f"Traits: {', '.join(ai_config['traits'])}. "
                f"Hobbies: {', '.join(ai_config['hobbies'])}. "
                f"Knowledge Base: {', '.join(ai_config['knowledge_base'])}. "
                f"Mood: {ai_config['mood']}. "
                f"Interaction Style: {ai_config['interaction_style']}. "
                f"Favorite Topics: {', '.join(ai_config['favorite_topics'])}. "
                f"Special Skills: {', '.join(ai_config['special_skills'])}. "
                f"User Relationship: {ai_config['user_relationship']}. "
                f"Here is some current information: {info_text} "
                f"Here is a ACM File, with our conversations from last sessions: {conversation}"
            )},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message.content.strip()

def recognize_speech():
    with sr.Microphone() as source:
        try:
            audio = recognizer.listen(source)
            user_input = recognizer.recognize_google(audio, language='en-US')
            print(f"YOU: {user_input}")
            return user_input
        except sr.UnknownValueError:
            speak_text("Sorry, I didn't catch that. Could you please repeat?")
            return None
        except sr.RequestError:
            speak_text("There was an error with the speech recognition service.")
            return None

def play_and_delete(file_path):
    global listening
    try:
        # Stop listening when audio starts playing
        listening = False

        pygame.mixer.init()
        pygame.mixer.music.load(str(file_path))
        pygame.mixer.music.play()

        # Wait until the audio is finished playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        # Stop the music and uninitialize the mixer
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        
        # Ensure the file is fully released before deletion
        time.sleep(1)
        os.remove(file_path)
        listening = True
    
    except Exception as e:
        print(f"Error during playback or file deletion: {e}")
        traceback.print_exc()


def speak_text(text):
    try:
        print(f"{ai_config['name']}: " + text)
        
        # Generate the TTS response
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        
        # Save the speech to a temporary file
        temp_speech_file_path = Path("voice.mp3")
        with open(temp_speech_file_path, 'wb') as f:
            f.write(response.content)
        
        # Play the speech file and delete it afterward using a separate thread
        playback_thread = threading.Thread(target=play_and_delete, args=(temp_speech_file_path,))
        playback_thread.start()

    except Exception as e:
        print(f"Error in TTS Module: {e}")
        traceback.print_exc()

def select_ai_config():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("AI Configuration", "*.ACF")])
    return file_path

def set_reminder():
    while True:
        speak_text("What is the reminder for?")
        reminder_text = recognize_speech()
        if reminder_text:
            while True:
                speak_text("In how many seconds should I remind you?")
                reminder_delay = recognize_speech()
                if reminder_delay and reminder_delay.isdigit():
                    reminder_time = datetime.now() + timedelta(seconds=int(reminder_delay))
                    reminders.append((reminder_time, reminder_text))
                    speak_text(f"Reminder set for {reminder_text} in {reminder_delay} seconds.")
                    return
                elif reminder_delay and reminder_delay.lower() == "cancel":
                    speak_text("Reminder setting cancelled.")
                    return
                else:
                    speak_text("Invalid time for reminder. Please provide the time in seconds or say 'cancel' to exit.")
        elif reminder_text.lower() == "cancel":
            speak_text("Reminder setting cancelled.")
            return
        else:
            speak_text("I didn't catch that. Please repeat the reminder details or say 'cancel' to exit.")

def check_reminders():
    while True:
        now = datetime.now()
        for reminder_time, text in reminders:
            if now >= reminder_time:
                speak_text(f"Reminder: {text}")
                reminders.remove((reminder_time, text))
        time.sleep(1)

def interact():
    global ai_config, listening

    config_file = select_ai_config()
    if config_file:
        ai_config = functions.load_ai_config(config_file)
        ai_name = ai_config['name']

        conversation_log = functions.load_conversation(ai_name)
        if not conversation_log:
            ai_name = recognize_name()
            if ai_name:
                ai_config['name'] = ai_name
                with open(config_file, 'w') as f:
                    json.dump(ai_config, f, indent=4)
        else:
            speak_text(f"Hello, I'm {ai_name}. I remember our previous conversations.")

        while True:
            if listening:
                user_input = recognize_speech()
                if user_input is None:
                    continue

                # Check for keywords in the user input
                if any(word in user_input.lower() for word in ['goodbye', 'shut down', 'shutdown', 'exit']):
                    goodbye_response = random.choice(sentences.GOODBYE_RESPONSES)
                    speak_text(goodbye_response + " Say WAKE UP to alert me")
                    listening = False
                elif 'delete conversation log' in user_input.lower():
                    speak_text("Please provide the delete code.")
                    delete_code = recognize_speech()
                    if delete_code and functions.verify_code(delete_code):
                        functions.delete_conversation(ai_name)
                        speak_text("Conversation log has been deleted.")
                    else:
                        speak_text("Incorrect code. Cannot delete conversation log.")
                elif 'weather' in user_input.lower():
                    weather_info = functions.get_weather()
                    speak_text(weather_info)
                elif 'set a reminder' in user_input.lower():
                    set_reminder()
                else:
                    try:
                        response = generate_response(user_input)
                        speak_text(response)
                        functions.save_conversation(ai_name, user_input, response)
                    except Exception as e:
                        speak_text("There was an error.")
            else:
                try:
                    with sr.Microphone() as source:
                        audio = recognizer.listen(source, timeout=5)
                        command = recognizer.recognize_google(audio, language='en-US')
                        if 'wake up' in command.lower():
                            speak_text(sentences.WAKE_UP_RESPONSE)
                            listening = True
                except sr.UnknownValueError:
                    continue
                except sr.RequestError:
                    speak_text("There was an error with the speech recognition service.")
                except sr.WaitTimeoutError:
                    continue

if __name__ == "__main__":
    interact()
