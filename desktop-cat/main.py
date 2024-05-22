import pyautogui
import random
import tkinter as tk
import os
from tkinter import messagebox
from PIL import Image, ImageTk
import pystray
from pystray import MenuItem as item
import threading

animation_running = True
x = 1400 # +-200
cycle = 0
position = 0
# current_event_cycle = 20
current_event_cycle = random.choice([0,8,1,9,5,13,20])
current_event_cycle_index = 0

"""
0: L_goosebumps.gif,  len 16
1: L_idle.gif,  len 10
2: L_idle2.gif,  len 11
3: L_jump.gif,  len 10
4: L_licking.gif,  len 13
5: L_licking2.gif,  len 14
6: L_sleep.gif,  len 11
7: L_touch.gif,  len 11
8: L_walk.gif,  len 10
9: L_walk2.gif,  len 11
"""

EVENTS = { # eventNumber: [[actionOrderToBeCompleted], [PossibleNextEventNumbers]]
    # Left events
    0: [[1,1,1,1,2,2,2,2,1,1,4,4,4,4,1,1,1,1,2,2], [0,1,2,3,5,8,9,10,11,13,16,17,18]], # idle 1
    1: [[2,2,2,2,2,2,1,1,1,1,5,5,5,5,5,5,5,1,1,1], [0,1,2,3,5,8,9,10,11,13,16,17,18]], # idle 2
    2: [[8,8,8], [0,1,2,3,4,7,8,9,10,11,12,15,16,17,18]], # walk 1
    3: [[9,9,9], [0,1,2,3,4,7,8,9,10,11,12,15,16,17,18]], # walk 2
    4: [[3], [0,1,2,3,8,9]], # jump
    5: [[6,6,6], [0,1,5,7,8,9,13,15,16,17,5,5,5,5,18,20]], # sleep
    6: [[7], [0,1,4,7,7,7,7,8,9,12]], # touch
    7: [[0], [0,1,4,5,6,8,9,12,13,14]], # goosebumps
    # Right events
    8: [[11,11,11,11,12,12,12,12,11,11,14,14,14,14,11,11,11,11,12,12], [0,1,2,3,5,8,9,10,11,13,16,17,18]], # idle 1 R
    9: [[12,12,12,12,12,12,11,11,11,11,15,15,15,15,15,15,15,11,11,11], [0,1,2,3,5,8,9,10,11,13,16,17,18]], # idle 2 R 
    10: [[18,18,18], [0,1,2,3,4,7,8,9,10,11,12,15,16,17,18]], # walk 1 R
    11: [[19,19,19], [0,1,2,3,4,7,8,9,10,11,12,15,16,17,18]], # walk 2 R
    12: [[13], [0,1,10,11,8,9]], # jump R
    13: [[16,16,16], [0,1,5,7,8,9,13,15,16,17,5,5,5,5,18,20]], # sleep R
    14: [[17], [0,1,4,8,9,12,15,15,15,15]], # touch R
    15: [[10], [0,1,4,5,6,8,9,12,13,14]], # goosebumps R
    # Extra events
    16: [[1,1,1,1,1,2,2,2,1,1,1,2,2,1,1,14,14,14,14,14,15,15,15,15,15,15,1,1,1,1,11,11,11,11,12,12,12,12,12], [0,1,8,9,5,17,18,19,20]], # idle 3
    17: [[2,2,2,2,2,12,12,12,12,12,12,12,12,12,12,12,11,11,11,11,11,11,14,14,14,14,14,14,14,12,12,11,11,11], [0,1,8,9,5,16,18,19,20]], # idle 4
    18: [[12,12,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16,16], [0,1,8,9]], # sleep long
    19: [[8,8,19,19,9,9,18,18], [0,1,8,9,16,17,18,20]], # walk there
    20: [[3,0,10], [16,17,18,19]], # jump and goosebumps
}

event_number = EVENTS[current_event_cycle][0][0]
impath = 'C:\\Users\\orhun\\OneDrive\\Belgeler\\GitHub\\desktop-cat\\desktop-cat\\Cats\\greyCat-160x160-10\\gifs\\'
tray_path = 'C:\\Users\\orhun\\OneDrive\\Belgeler\\GitHub\\desktop-cat\\desktop-cat\\Cats\\greyCat-160x160-10\\tray-icon.png'
#call buddy's action gif
imageGif = {}
images = []

def event(cycle,event_number,x):
    times = [600, 1200, 1200, 1050, 900]
    if event_number in [1, 2, 4, 5] or event_number-10 in [1, 2, 4, 5]:
        window.after(200,update,cycle,event_number,x)
        
    elif event_number in [8, 9, 0] or event_number-10 in [8, 9, 0]:
        window.after(150,update,cycle,event_number,x)
        
    elif event_number in [6,16]:
        window.after(1000,update,cycle,event_number,x)
        
    elif event_number in [3, 13]:
        window.after(160,update,cycle,event_number,x)
    
    elif event_number in [7,17]:
        window.after(160,update,cycle,event_number,x)
        
#making gif work 
def gif_work(cycle,frames,event_number):
    if cycle < len(frames) -1:
        cycle+=1
    else:
        cycle = 0
        event_number = chooseEventChange()
    return cycle,event_number

def update(cycle,event_number,x):
    if not animation_running:
        return    
    frame = imageGif[images[event_number]][cycle]
    global position
    if event_number in[8, 9, 3]:
        x -= 8
        position = x
    elif event_number in[18, 19, 13]:
        x += 8
        position = x
        
    cycle ,event_number = gif_work(cycle,imageGif[images[event_number]],event_number)

    window.geometry('160x160+'+str(x)+'+922')
    label.configure(image=frame)
    window.after(1,event,cycle,event_number,x)
    
def chooseEventChange():
    global current_event_cycle, current_event_cycle_index, position
    if current_event_cycle_index < len(EVENTS[current_event_cycle][0])-1:
        current_event_cycle_index+=1
    else:
        next_event_cycle = random.choice(EVENTS[current_event_cycle][1])
        while position > 1600 and (next_event_cycle == 2 or next_event_cycle == 3 or next_event_cycle == 4):
            next_event_cycle = random.choice(EVENTS[current_event_cycle][1])
        while position < 1200 and (next_event_cycle == 10 or next_event_cycle == 11 or next_event_cycle == 12):
            next_event_cycle = random.choice(EVENTS[current_event_cycle][1])            
        current_event_cycle = next_event_cycle
        current_event_cycle_index = 0
    return EVENTS[current_event_cycle][0][current_event_cycle_index]

def show_window():
    global animation_running
    animation_running = True    
    window.after(0, window.deiconify)
    icon.stop()

# Function to hide the Tkinter window
def hide_window(event=None):
    global animation_running
    animation_running = False    
    window.withdraw()
    create_tray_icon()

# Function to exit the application
def exit_application(icon, item):
    icon.stop()
    window.quit()

# Define the function to create the system tray icon
def create_tray_icon():
    # Load an icon image
    icon_image = Image.open(tray_path)

    # Define the menu items
    menu = (
        item('Show', lambda: show_window()),
        item('Exit', exit_application)
    )

    # Create and run the system tray icon
    global icon
    icon = pystray.Icon("name", icon_image, "Tkinter App", menu)
    icon.run()

if __name__ == '__main__':
    window = tk.Tk()
    imageGif = {}
    images = os.listdir(impath)
    for image in images:
        try:
            defrange = 4
            if 'walk' in image or 'goosebumps' in image:
                defrange = 8
            elif 'touch' in image:
                defrange = 6
            elif 'jump' in image:
                defrange = 7
            imageGif[image] = [tk.PhotoImage(file=os.path.join(impath, image), format=f'gif -index {i}') for i in range(defrange)]
        except tk.TclError as e:
            print(f"\nError loading {os.path.join(impath, image)  } : {e}")#window configuration
    window.config(highlightbackground='black')
    label = tk.Label(window,bd=0,bg='black')
    window.overrideredirect(True)
    window.wm_attributes('-transparentcolor','black')
    window.wm_attributes('-topmost', 1)
    window.bind("<Double-Button-1>", hide_window)
    label.pack()
    #loop the program
    window.after(1,update,cycle,event_number,x)
    window.mainloop()