from functools import partial
import tkinter as tk

import datetime
import json
import os

# Check if an exe is running
if ".py" in __file__:
    run_with_exe = False
else: 
    run_with_exe = True

# Start Scheduler
if run_with_exe:
    os.startfile('src/scheduler.exe')

labels = []
window = tk.Tk()
window.title("Zoom Scheduler")

# Title
title = tk.Label(window, text="Zoom Scheduler", font=("Arial", 60))
title.grid(row=0, column=2)
labels.append([None, title, None])

# Read meetings
if run_with_exe:
    data_path = "src/data/meetings.json"
else:
    data_path = "data/meetings.json"

with open(data_path, 'r') as i:
    meetings = json.loads(i.read())['meetings']

def delete_meeting(meeting_index):
    global offset
    remove_row = labels[meeting_index]
    for l in remove_row:
        l.grid_forget()

    meetings.remove(meetings[meeting_index-2])

    with open(data_path, 'w+', encoding='utf-8') as f:
        json.dump({'meetings': meetings}, f, ensure_ascii=False, indent=4)

# Key Header
sub_arr = []
headers = ['Class Name', 'Class Time', 'Class Days', 'End Date','Remove Class']
for t in range(len(headers)):
    l = tk.Label(window, text=headers[t], font=("Arial", 30))
    l.grid(row=1, column=t)
    sub_arr.append(l)
labels.append(sub_arr.copy())

def add_meeting_to_grid(m):
    sub_arr = []
    hour = m['crontab'].split(" ")[0]
    minute = m['crontab'].split(" ")[1]
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


# Add existing meetings
for x in range(len(meetings)):
    m = meetings[x]
    add_meeting_to_grid(m)
    

# Add new meeting section



# Tkinter run loop
window.mainloop()