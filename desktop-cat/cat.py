import pyautogui
import random
import tkinter as tk
import os
from tkinter import messagebox
from PIL import Image, ImageTk
import pystray
from pystray import MenuItem as item
import threading
from menu import PixelArtMessageBoxApp
import time

EVENTS = { # eventNumber: [[actionOrderToBeCompleted], [PossibleNextEventNumbers]]
    # Left events
    0: [[1, 1, 1, 1, 2, 2, 2, 2, 1, 1, 4, 4, 4, 4, 1, 1, 1, 1, 2, 2], [0, 1, 2, 3, 5, 8, 9, 10, 11, 13, 16, 17, 18]], # idle 1
    1: [[2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 5, 5, 5, 5, 5, 5, 5, 1, 1, 1], [0, 1, 2, 3, 5, 8, 9, 10, 11, 13, 16, 17, 18]], # idle 2
    2: [[8, 8, 8], [0, 1, 2, 3, 4, 7, 8, 9, 10, 11, 12, 15, 16, 17, 18]], # walk 1
    3: [[9, 9, 9], [0, 1, 2, 3, 4, 7, 8, 9, 10, 11, 12, 15, 16, 17, 18]], # walk 2
    4: [[3], [0, 1, 2, 3, 8, 9]], # jump
    5: [[6, 6, 6], [0, 1, 5, 7, 8, 9, 13, 15, 16, 17, 5, 5, 5, 5, 18, 20]], # sleep
    6: [[7], [0, 1, 4, 7, 7, 7, 7, 8, 9, 12]], # touch
    7: [[0], [0, 1, 4, 5, 6, 8, 9, 12, 13, 14,0, 1,0, 1]], # goosebumps
    # Right events
    8: [[11, 11, 11, 11, 12, 12, 12, 12, 11, 11, 14, 14, 14, 14, 11, 11, 11, 11, 12, 12], [0, 1, 2, 3, 5, 8, 9, 10, 11, 13, 16, 17, 18]], # idle 1 R
    9: [[12, 12, 12, 12, 12, 12, 11, 11, 11, 11, 15, 15, 15, 15, 15, 15, 15, 11, 11, 11], [0, 1, 2, 3, 5, 8, 9, 10, 11, 13, 16, 17, 18]], # idle 2 R 
    10: [[18, 18, 18], [0, 1, 2, 3, 4, 7, 8, 9, 10, 11, 12, 15, 16, 17, 18]], # walk 1 R
    11: [[19, 19, 19], [0, 1, 2, 3, 4, 7, 8, 9, 10, 11, 12, 15, 16, 17, 18]], # walk 2 R
    12: [[13], [0, 1, 10, 11, 8, 9]], # jump R
    13: [[16, 16, 16], [0, 1, 5, 7, 8, 9, 13, 15, 16, 17, 5, 5, 5, 5, 18, 20]], # sleep R
    14: [[17], [0, 1, 4, 8, 9, 12, 15, 15, 15, 15]], # touch R
    15: [[10], [0, 1, 4, 5, 6, 8, 9, 12, 13, 14]], # goosebumps R
    # Extra events
    16: [[1, 1, 1, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 1, 1, 14, 14, 14, 14, 14, 15, 15, 15, 15, 15, 15, 1, 1, 1, 1, 11, 11, 11, 11, 12, 12, 12, 12, 12], [0, 1, 8, 9, 5, 17, 18, 19, 20]], # idle 3
    17: [[2, 2, 2, 2, 2, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 11, 11, 11, 11, 11, 11, 14, 14, 14, 14, 14, 14, 14, 12, 12, 11, 11, 11], [0, 1, 8, 9, 5, 16, 18, 19, 20]], # idle 4
    18: [[12, 12, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16], [0, 1, 8, 9]], # sleep long
    19: [[8, 8, 19, 19, 9, 9, 18, 18], [0, 1, 8, 9, 16, 17, 18, 20]], # walk there
    20: [[3, 0, 10], [16, 17, 18, 19]], # jump and goosebumps
    21: [[20], [21]], # falling
    22: [[2], [22]] # stay put
}

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


class DesktopCat(PixelArtMessageBoxApp):
    def __init__(self):
        self.animation_running = True
        self.falling = False
        self.x = 1400
        self.y = 922
        self.initial_x = 1400
        self.initial_y = 922
        self.cycle = 0
        self.current_event_cycle = random.choice([0, 8, 1, 9, 5, 13])
        self.current_event_cycle_index = 0
        self.EVENTS = EVENTS
        self.event_number = self.EVENTS[self.current_event_cycle][0][0]
        self.impath = 'C:\\Users\\orhun\\OneDrive\\Belgeler\\GitHub\\desktop-cat\\desktop-cat\\Cats\\greyCat-160x160-10\\gifs\\'
        self.fallingPath = 'C:\\Users\\orhun\\OneDrive\\Belgeler\\GitHub\\desktop-cat\\desktop-cat\\Cats\\greyCat-160x160-10\\gifs_others\\falling.gif'
        self.menu_bg_image_path = "C:\\Users\\orhun\\OneDrive\\Belgeler\\GitHub\\desktop-cat\\desktop-cat\\Cats\\greyCat-160x160-10\\messagebox4.png"
        self.fallingGif = []
        self.tray_path = 'C:\\Users\\orhun\\OneDrive\\Belgeler\\GitHub\\desktop-cat\\desktop-cat\\Cats\\greyCat-160x160-10\\tray-icon.png'
        self.flyPNG = []
        self.imageGif = {}
        self.images = []
        self.position = 0
        self.before_ms = 0
        self.icon = None
        self.icon_created = False
        self.command_created = False
        self.message = None
        self.window = tk.Tk()
        self.label = tk.Label(self.window, bd=0, bg='black')
        self.error = self.load_images()
        if self.error == 0:
            self.setup_window()
            self.start_animation()
            
    def get_message(self):
        new_message = self.message.on_enter_pressed(None)  # Pass a dummy event
        print("Message received:", new_message)
        self.analyzeMessage(new_message)
        # You can add more processing here
        
    def analyzeMessage(self, message):
        if message == '-r':
            print('Restarting...')
        else:
            print('Message Error')

    def load_images(self):
        self.images = os.listdir(self.impath)
        error = 0
        i = 0
        for image in self.images:
            i+=1
            try:
                defrange = 4
                if 'walk' in image or 'goosebumps' in image:
                    defrange = 8
                elif 'touch' in image:
                    defrange = 6
                elif 'jump' in image:
                    defrange = 7
                self.imageGif[image] = [tk.PhotoImage(file=os.path.join(self.impath, image), format=f'gif -index {i}') for i in range(defrange)]
            except tk.TclError as e:
                print(f"Error loading {os.path.join(self.impath, image)} : {e}")
                error = 1
        self.imageGif['falling'] = [tk.PhotoImage(file=self.fallingPath, format=f'gif -index {i}') for i in range(4)]
        self.images.append('falling')
        return error
    
    def on_drag_start(self, event):
        print('on_drag_start')
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root
        self.initial_window_x = self.window.winfo_x()
        self.initial_window_y = self.window.winfo_y()

    def on_drag_motion(self, event):
        print('on_drag_motion')
        if not self.command_created:
            self.animation_running = False
            deltax = event.x_root - self.drag_start_x
            new_x = self.initial_window_x + deltax
            new_x = max(min(new_x, 1600), 1200)
            deltay = event.y_root - self.drag_start_y
            new_y = self.initial_window_y + deltay
            new_y = max(min(new_y, 922), 400)
            self.window.geometry(f"+{new_x}+{new_y}")
            self.x = new_x
            self.y = new_y

    def on_drag_stop(self, event):
        print('on_drag_stop')
        if not self.animation_running:
            self.animation_running = True
            self.window.after(200, self.update)

    def setup_window(self):
        self.window.config(highlightbackground='black')
        self.label.pack()
        self.window.overrideredirect(True)
        self.window.wm_attributes('-transparentcolor', 'black')
        self.window.wm_attributes('-topmost', 1)
        self.window.bind("<Double-Button-1>", self.openMenu)
        self.window.bind("<ButtonPress-1>", self.on_drag_start)
        self.window.bind("<ButtonPress-3>", self.hide_window)
        self.window.bind("<B1-Motion>", self.on_drag_motion)
        self.window.bind("<ButtonRelease-1>", self.on_drag_stop)

    def start_animation(self):
        self.window.after(1, self.update)
        self.window.mainloop()

    def event(self):
        if self.event_number in [1, 2, 4, 5] or self.event_number - 10 in [1, 2, 4, 5]:
            self.window.after(200, self.update)
        elif self.event_number in [8, 9, 0] or self.event_number - 10 in [8, 9, 0]:
            self.window.after(150, self.update)
        elif self.event_number in [6, 16]:
            self.window.after(1000, self.update)
        elif self.event_number in [3, 13]:
            self.window.after(160, self.update)
        elif self.event_number in [7, 17]:
            self.window.after(160, self.update)
        elif self.event_number == 20:
            self.window.after(120, self.update)

    def gif_work(self):
        if self.cycle < len(self.imageGif[self.images[self.event_number]]) - 1:
            self.cycle += 1
        else:
            self.cycle = 0
            self.event_number = self.choose_event_change()

    def update(self):
        current_milliseconds = int(time.time() * 1000)
        # print('update ', current_milliseconds-self.before_ms)
        self.before_ms = current_milliseconds
        
        if not self.animation_running:
            return
        
        if self.y < self.initial_y:
            if not self.falling:
                self.falling = True
                self.current_event_cycle = 21
                self.current_event_cycle_index = 0
                self.cycle = 0
                self.event_number = self.EVENTS[self.current_event_cycle][0][self.current_event_cycle_index]
            self.y += 20
        elif self.y >= self.initial_y and self.falling:
            self.current_event_cycle = random.choice([7,15])
            self.current_event_cycle_index = 0
            self.cycle = 0
            self.event_number = self.EVENTS[self.current_event_cycle][0][self.current_event_cycle_index]
            self.falling = False
            self.y = self.initial_y
            
        frame = self.imageGif[self.images[self.event_number]][self.cycle]
        if self.event_number in [8, 9, 3]:
            self.x -= 8
        elif self.event_number in [18, 19, 13]:
            self.x += 8
            
        if self.animation_running:        
            self.gif_work()
            self.window.geometry('160x160+' + str(self.x) + '+' + str(self.y))
            self.label.configure(image=frame)
            self.window.after(1, self.event)

    def choose_event_change(self):
        if self.current_event_cycle_index < len(self.EVENTS[self.current_event_cycle][0]) - 1:
            self.current_event_cycle_index += 1
        else:
            next_event_cycle = random.choice(self.EVENTS[self.current_event_cycle][1])
            while self.x > self.initial_x+200 and next_event_cycle in [2, 3, 4]:
                next_event_cycle = random.choice(self.EVENTS[self.current_event_cycle][1])
            while self.x < self.initial_y-200 and next_event_cycle in [10, 11, 12]:
                next_event_cycle = random.choice(self.EVENTS[self.current_event_cycle][1])
            self.current_event_cycle = next_event_cycle
            self.current_event_cycle_index = 0
        return self.EVENTS[self.current_event_cycle][0][self.current_event_cycle_index]

    def show_window(self):
        print('show_window')
        self.window.after(0, self.window.deiconify)
        if self.icon_created:
            self.icon_created = False
            self.icon.stop()

    def hide_window(self, event):
        print('hide_window')
        if self.command_created:
            self.clearCommand()
        self.window.withdraw()
        self.create_tray_icon()

    def exit_application(self):
        print('exit_application')
        if self.command_created:
            self.clearCommand()        
        self.icon.stop()
        self.window.quit()

    def create_tray_icon(self):
        print('create_tray_icon')
        icon_image = Image.open(self.tray_path)
        menu = (item('Show', lambda: self.show_window()), item('Exit', self.exit_application))
        self.icon = pystray.Icon("DesktopCat", icon_image, "DesktopCat", menu)
        self.icon_created = True
        self.icon.run()
        
    def clearCommand(self):
        self.command_created = False
        self.message.deleteMessageBox()
        del self.message
        self.message = None
        self.current_event_cycle = random.randint(0,20)
        self.current_event_cycle_index = 0
        self.cycle = 0
        self.event_number = self.EVENTS[self.current_event_cycle][0][self.current_event_cycle_index]

    def openMenu(self, event):
        print('openMenu: ')
        if not self.command_created:
            print('   command_created')
            self.show_window()
            self.command_created = True
            self.message = PixelArtMessageBoxApp(Image.open(self.menu_bg_image_path).convert("RGBA"))
            self.current_event_cycle = 22
            self.current_event_cycle_index = 0
            self.cycle = 0
            self.event_number = self.EVENTS[self.current_event_cycle][0][self.current_event_cycle_index]
            self.message.init(self.x-295, self.y-110)
        elif self.message != None:
            print('   message deleted')
            self.clearCommand()
            
    def trueAnimation(self):
        self.animation_running = True
            
    def restartAnimation(self):
        self.animation_running = False
        self.current_event_cycle = random.choice([0, 8, 1, 9, 5, 13])
        self.current_event_cycle_index = 0
        self.cycle = 0
        self.event_number = self.EVENTS[self.current_event_cycle][0][self.current_event_cycle_index] 
        
        thread = threading.Thread(target=self.window.after(2000, self.trueAnimation))
        thread.start()
        thread.join()
        self.window.after(1, self.update)
       
                    
if __name__ == '__main__':
    desktop_cat = DesktopCat()
