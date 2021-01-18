from functools import partial
import tkinter as tk

import dateparser
import datetime
import time
import json
import os

#os.startfile(os.path.abspath(os.path.dirname(os.path.abspath(__file__))) + '/src/scheduler.exe')

labels = []
window = tk.Tk()
window.title("Zoom Scheduler")

# Title
title = tk.Label(window, text="Zoom Scheduler", font=("Arial", 60))
title.grid(row=0, column=2)
labels.append([None, title, None])

# Read meetings
data_path = os.path.abspath(os.path.dirname(os.path.abspath(__file__))) + "/src/data/meetings.json"

with open(data_path, 'r') as i:
    meetings = json.loads(i.read())['meetings']

def delete_meeting(meeting_index):
    remove_row = labels[meeting_index]
    for l in remove_row:
        l.grid_forget()

    meetings.remove(meetings[meeting_index-2])

    with open(data_path, 'w+', encoding='utf-8') as f:
        json.dump({'meetings': meetings}, f, ensure_ascii=False, indent=4)

    redraw()

# Key Header
sub_arr = []
headers = ['Class Name', 'Class Time', 'Class Days', 'End Date','Remove Class']
for t in range(len(headers)):
    l = tk.Label(window, text=headers[t], font=("Arial", 30))
    l.grid(row=1, column=t)
    sub_arr.append(l)
labels.append(sub_arr.copy())


def add_meeting_to_grid(m,x):
    sub_arr = []
    minute = m['crontab'].split(" ")[0]
    hour = m['crontab'].split(" ")[1]
    values = [m['class_name'], f"{hour}:{minute}", m['crontab'].split(" ")[4], datetime.datetime.fromtimestamp(m['end_date']).strftime("%x")]
    for j in range(len(values)):
        l = tk.Label(window, text=values[j], font=("Arial", 20))
        l.grid(row=x+2, column=j)
        sub_arr.append(l)

    # Add Remove Button
    b = tk.Button(window,
                   text="X",
                   command=partial(delete_meeting, x+2))
    b.grid(row=x+2, column=len(values))
    sub_arr.append(b)
    labels.append(sub_arr.copy())

def redraw():
    global meetings
    for x in range(2,len(labels)):
        for l in labels[x]:
            l.grid_forget()

    with open(data_path, 'r') as i:
        meetings = json.loads(i.read())['meetings']

    # Add existing meetings
    for x in range(len(meetings)):
        m = meetings[x]
        add_meeting_to_grid(m,x)

redraw()

# New Meeting Class
class new_meeting_window():
    _tk_root = None
    redraw_func = None
    def __init__(self):
        self.root = tk.Toplevel(new_meeting_window._tk_root)
        self.root.bind('<Return>', (lambda: self.submit()))
        a = tk.Label(self.root ,text = "Class Name").grid(row = 0,column = 0)
        b = tk.Label(self.root ,text = "Days of week \n(Ex: Sun,Mon,Tue,Wed,Thu,Fri,Sat)").grid(row = 1,column = 0)
        c = tk.Label(self.root ,text = "Class Time (Ex: 16:20)").grid(row = 2,column = 0)
        d = tk.Label(self.root ,text = "Room ID").grid(row = 3,column = 0)
        e = tk.Label(self.root ,text = "Room Passcode").grid(row = 4,column = 0)
        f = tk.Label(self.root ,text = "End date (Ex: 5/21/2021)").grid(row = 5,column = 0)
        self.class_name = tk.Entry(self.root)
        self.class_name.grid(row = 0,column = 1)
        self.days_of_week = tk.Entry(self.root)
        self.days_of_week.grid(row = 1,column = 1)
        self.room_id = tk.Entry(self.root)
        self.room_id.grid(row = 3,column = 1)
        self.room_passcode = tk.Entry(self.root)
        self.room_passcode.grid(row = 4,column = 1)
        self.end_date = tk.Entry(self.root)
        self.end_date.grid(row=5, column=1)
        self.class_time = tk.Entry(self.root)
        self.class_time.grid(row=2, column=1)
        btn = tk.Button(self.root ,text="Submit", command=self.submit).grid(row=6,column=0)

    def submit(self):
        hour = self.class_time.get().split(":")[0]
        minute = self.class_time.get().split(":")[1]
        days = self.days_of_week.get()
        new_entry = {
            "class_name": self.class_name.get(),
            "crontab": f"{minute} {hour} * * {days}",
            "room_id": self.room_id.get(),
            "password": self.room_passcode.get(),
            "end_date": dateparser.parse(self.end_date.get(), settings={"PREFER_DATES_FROM": "future"}).timestamp()
        }
            
        data_path = os.path.abspath(os.path.dirname(os.path.abspath(__file__))) + "/src/data/meetings.json"

        with open(data_path, 'r') as i:
            meetings = json.loads(i.read())['meetings']

        meetings.append(new_entry)
        
        with open(data_path, 'w+', encoding='utf-8') as f:
            json.dump({'meetings': meetings}, f, ensure_ascii=False, indent=4)

        new_meeting_window.redraw_func()
        self.root.withdraw()
        

new_meeting_window._tk_root = window
new_meeting_window.redraw_func = redraw

b = tk.Button(window, text="Add New Meeting", command=new_meeting_window)
b.grid(row=0, column=4)

# Tkinter run loop
window.mainloop()