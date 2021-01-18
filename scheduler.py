from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler

import pyautogui
import logging
import datetime
import time
import json
import sys
import os

if not os.path.isdir('data'):
    os.mkdir('data')


def find_zoom_exe():
    # "C:\\Users\\David Teather\\AppData\\Roaming\\Zoom\\bin\\Zoom.exe"
    # "C:\Users\David Teather\AppData\Roaming\Zoom\bin\Zoom.exe"
    if sys.platform == "linux" or sys.platform == "linux2":
        # linux
        pass
    elif sys.platform == "darwin":
        # OS X
        pass
    elif sys.platform == "win32":
        # Windows...

        # Requirements to find for this section
        #  * Script is somewhere under a /users directory like documents or desktop
        #  * Zoom @ Default Installation Location
        path_attributes = os.path.abspath(os.getcwd()).split("\\")
        if path_attributes[1] == 'Users':
            path = path_attributes[0] + "\\" + path_attributes[1] + "\\" + \
                path_attributes[2] + "\\AppData\\Roaming\\Zoom\\bin\\Zoom.exe"
            if os.path.exists(path):
                return path

        # Requirements to find
        #  * Python environment is installed under a /users directory
        #  * Zoom @ Default Installation
        path_attributes = sys.executable.split("\\")
        if path_attributes[1] == 'Users':
            path = path_attributes[0] + "\\" + path_attributes[1] + "\\" + \
                path_attributes[2] + "\\AppData\\Roaming\\Zoom\\bin\\Zoom.exe"
            if os.path.exists(path):
                return path


ZOOM_PATH = find_zoom_exe()
if ZOOM_PATH == None:
    # Attempts to load from settings
    try:
        with open('data/settings.json', 'r', encoding='utf-8') as f:
            ZOOM_PATH = json.loads(f.read())['ZOOM_PATH']
    except (FileNotFoundError, ValueError):
        pass

    # Could not load from settings :(
    if ZOOM_PATH == None:
        print("Could not auto-locate zoom executable. Please enter it now.")
        print("EX: C:\\Users\\Your Name\\AppData\\Roaming\\Zoom\\bin\\Zoom.exe")

        ZOOM_PATH = input()

        while not os.path.exists(ZOOM_PATH):
            ZOOM_PATH = input(
                "That file path does not exist. Please enter a valid zoom.exe location")

        # Save zoom_path for future launches so user only has to enter it once
        with open('data/settings.json', 'w+', encoding='utf-8') as f:
            json.dump({'ZOOM_PATH': ZOOM_PATH}, f,
                      ensure_ascii=False, indent=4)


def join_meeting(meeting):
    if meeting['end_date'] < datetime.datetime.now().timestamp():
        # remove meeting because it has passed
        with open("data/meetings.json", 'r') as i:
            current = json.loads(i.read())['meetings']
            for m in current:
                if m == meeting:
                    current.remove(m)
                    break

        with open('data/meetings.json', 'w+', encoding='utf-8') as f:
            json.dump({'meetings': current}, f, ensure_ascii=False, indent=4)

        return

    room_id = meeting['room_id']
    password = meeting['password']

    # start zoom exe
    os.startfile(ZOOM_PATH)
    time.sleep(2)

    # find join a meeting button
    join_button = pyautogui.locateOnScreen("images/join-a-meeting.png")
    pyautogui.moveTo(join_button)
    pyautogui.click()
    time.sleep(1)

    # Join a meeting
    pyautogui.write(str(room_id))
    pyautogui.press('enter')

    # Handle Required Login
    warning = pyautogui.locateOnScreen("images/warning.png")
    if warning == None:
        # Authorization is not needed
        pyautogui.write(str(password))
        pyautogui.press('enter')
        time.sleep(1)
    else:
        raise Exception(
            "Authorization is required for this zoom call. Please login.")

    join_no_video = pyautogui.locateOnScreen("images/no-video.png")
    if join_no_video != None:
        pyautogui.moveTo(join_no_video)
        pyautogui.click()


class FileChange(LoggingEventHandler):
    def on_modified(self, event):
        # triggers twice per modification but 🤷
        logging.info("File change detected")

        global scheduler
        scheduler.shutdown()
        queue_scheduler()
        scheduler.start()


def queue_scheduler():
    # Loading Meetings
    with open("data/meetings.json", 'r') as i:
        meetings = json.loads(i.read())['meetings']

    # Scheduler
    global scheduler
    scheduler = BackgroundScheduler()

    # Add a job for each meeting
    for m in meetings:
        scheduler.add_job(
            join_meeting, CronTrigger.from_crontab(m['crontab']), args=[m])


if __name__ == '__main__':
    global scheduler

    queue_scheduler()
    scheduler.start()

    # File change observer
    event_handler = FileChange()
    observer = Observer()
    observer.schedule(event_handler, './data', recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(0.1)
    except (KeyboardInterrupt, SystemExit):
        observer.stop()
        scheduler.shutdown()

    observer.join()
