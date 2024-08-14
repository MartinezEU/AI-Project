import datetime

def get_today_date():
    return datetime.datetime.now().strftime("%A, %B %d, %Y")

def get_current_time():
    return datetime.datetime.now().strftime("%H:%M:%S")

def get_current_version():
    return "Version 0.2 - BETA"

def get_useful_info():
    info = {
        "date": get_today_date(),
        "time": get_current_time(),
        "creator": "Robert",
        "version": get_current_version()
    }
    return info
