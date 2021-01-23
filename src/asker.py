import dateparser
import json
import os

if not os.path.isdir('data'):
    os.mkdir('data')

data_path = "data/meetings.json"
images_path = "images/"

def ask():
    name = input("What is the name of your class? (e.g. CS 101): ")

    time = input("What time is your class? (e.g. 14:30): ")
    hour = time.split(":")[0]
    minute = time.split(":")[1]

    print("\nDay options: Sun, Mon, Tue, Wed, Thu, Fri, Sat")
    days = input("What days are your classes? (e.g. Mon,Wed,Fri): ")

    room_id = input("Zoom ID: (e.g. 01234567890): ")
    password = input("Zoom Password: (e.g. 123456): ")

    end = input("When do these meetings end? (e.g. 5/15/2021): ")
    end_epoch = dateparser.parse(
        end, settings={"PREFER_DATES_FROM": "future"}).timestamp()

    new_meeting = {
        "class_name": name,
        "crontab": f"{minute} {hour} * * {days}",
        "room_id": room_id,
        "password": password,
        "end_date": end_epoch
    }

    try:
        with open(data_path, "r") as i:
            current_data = json.loads(i.read())['meetings']
            current_data.append(new_meeting)
    except (FileNotFoundError, ValueError):
        current_data = [new_meeting]

    with open(data_path, 'w+', encoding='utf-8') as f:
        json.dump({'meetings': current_data}, f, ensure_ascii=False, indent=4)


inp = 'y'
while inp.lower() != 'n':
    ask()
    inp = input("Add more classes y/n: ")
