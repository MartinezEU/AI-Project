import os
import datetime
import json
import requests

ARCHIVES_FOLDER = 'archives'

def create_ai_conversation_log(ai_name):
    log_file = get_conversation_file(ai_name)
    if not os.path.exists(log_file):
        os.makedirs(ARCHIVES_FOLDER, exist_ok=True)
        with open(log_file, 'w'):
            pass  # Create an empty file

def get_conversation_file(ai_name):
    return os.path.join(ARCHIVES_FOLDER, f'{ai_name}_conversation_log.acm')

def load_conversation(ai_name):
    conversation_file = get_conversation_file(ai_name)
    if os.path.exists(conversation_file):
        with open(conversation_file, 'r') as f:
            return f.read()
    return ""

def save_conversation(ai_name, user_input, response):
    conversation_file = get_conversation_file(ai_name)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(conversation_file, 'a') as f:
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"User: {user_input}\n")
        f.write(f"AI: {response}\n")
        f.write("-"*30 + "\n")

def delete_conversation(ai_name):
    conversation_file = get_conversation_file(ai_name)
    if os.path.exists(conversation_file):
        os.remove(conversation_file)

def verify_code(code):
    return code == '1234'  # You can customize the delete code as per your preference

def load_ai_config(file_path):
    with open(file_path, 'r') as f:
        config = json.load(f)
    return config

# Get weather updates
def get_weather(location="Prague"):
    api_key = "3df88748e5d0ddcbd967144544ce3ecb"
    base_url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}"
    response = requests.get(base_url).json()

    if response["cod"] != "404":
        main = response["main"]
        weather_desc = response["weather"][0]["description"]
        temp = round(main["temp"] - 273.15, 2)
        humidity = main["humidity"]
        wind_speed = response["wind"]["speed"]

        weather_info = (f"Weather in {location}: {weather_desc}, "
                        f"Temperature: {temp}°C, Humidity: {humidity}%, Wind Speed: {wind_speed} meters per second")
        return weather_info
    else:
        return "City not found."

