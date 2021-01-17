from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

import pyautogui
import datetime
import time
import json
import os

def join_meeting(meeting):
    if meeting['end_date'] < datetime.datetime.now().timestamp():
        # remove meeting because it has passed
        with open("meetings.json", 'r') as i:
            current = json.loads(i.read())['meetings']
            for m in current:
                if m == meeting:
                    current.remove(m)
                    break

        with open('meetings.json', 'w+', encoding='utf-8') as f:
            json.dump({'meetings': current}, f, ensure_ascii=False, indent=4)
        
        return
    
    room_id = meeting['room_id']
    password = meeting['password']

    # start zoom exe
    os.startfile("C:\\Users\\Nick\\AppData\\Roaming\\Zoom\\bin\\Zoom.exe")
    time.sleep(2)

    # find join a meeting button
    join_button = pyautogui.locateOnScreen("images/join-a-meeting.png")
    pyautogui.moveTo(join_button)
    pyautogui.click()
    time.sleep(1)

    # Join a meeting
    pyautogui.write(str(room_id))
    pyautogui.press('enter')
    time.sleep(1)

    # Handle Required Login
    warning = pyautogui.locateOnScreen("images/warning.png")
    if warning == None:
        # Authorization is not needed
        pyautogui.write(str(password))
        pyautogui.press('enter')
        time.sleep(1)
    else:
        raise Exception("Authorization is required for this zoom call. Please login.")

    time.sleep(1)
    join_no_video = pyautogui.locateOnScreen("images/no-video.png")
    if join_no_video != None:
        pyautogui.moveTo(join_no_video)
        pyautogui.click()


if __name__ == '__main__':
    # Loading Meetings
    with open("meetings.json", 'r') as i:
        meetings = json.loads(i.read())['meetings']

    # Scheduler 
    scheduler = BackgroundScheduler()

    # Add a job for each meeting
    for m in meetings:
        scheduler.add_job(join_meeting, CronTrigger.from_crontab(m['crontab']), args=[m])

    scheduler.start()

    try:
        while True:
            time.sleep(0.1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()