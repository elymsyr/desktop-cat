import pyautogui
import random
import tkinter as tk
import os
from tkinter import messagebox
from PIL import Image, ImageTk
import pystray
from pystray import MenuItem as item
import threading
import time
import pyglet

EVENTS = { # eventNumber: [[actionOrderToBeCompleted], [PossibleNextEventNumbers]]
    # Left events
    0: [[1, 1, 1, 1, 2, 2, 2, 2, 1, 1, 4, 4, 4, 4, 1, 1, 1, 1, 2, 2], [0, 1, 2, 3, 5, 8, 9, 10, 11, 13, 16, 17, 18]], # idle 1
    1: [[2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 5, 5, 5, 5, 5, 5, 5, 1, 1, 1], [0, 1, 2, 3, 5, 8, 9, 10, 11, 13, 16, 17, 18]], # idle 2
    2: [[8, 8, 8], [0, 1, 2, 3, 4, 7, 8, 9, 10, 11, 12, 15, 16, 17, 18]], # walk 1
    3: [[9, 9, 9], [0, 1, 2, 3, 4, 7, 8, 9, 10, 11, 12, 15, 16, 17, 18]], # walk 2
    4: [[3], [0, 1, 2, 3, 8, 9]], # jump
    5: [[6, 6, 6], [0, 1, 5, 7, 8, 9, 13, 15, 16, 17, 5, 5, 5, 18, 20]], # sleep
    6: [[7], [0, 1, 4, 7, 7, 7, 7, 8, 9, 12]], # touch
    7: [[0], [0, 1, 4, 5, 6, 8, 9, 12, 13, 14,0, 1,0, 1]], # goosebumps
    # Right events
    8: [[11, 11, 11, 11, 12, 12, 12, 12, 11, 11, 14, 14, 14, 14, 11, 11, 11, 11, 12, 12], [0, 1, 2, 3, 5, 8, 9, 10, 11, 13, 16, 17, 18]], # idle 1 R
    9: [[12, 12, 12, 12, 12, 12, 11, 11, 11, 11, 15, 15, 15, 15, 15, 15, 15, 11, 11, 11], [0, 1, 2, 3, 5, 8, 9, 10, 11, 13, 16, 17, 18]], # idle 2 R 
    10: [[18, 18, 18], [0, 1, 2, 3, 4, 7, 8, 9, 10, 11, 12, 15, 16, 17, 18]], # walk 1 R
    11: [[19, 19, 19], [0, 1, 2, 3, 4, 7, 8, 9, 10, 11, 12, 15, 16, 17, 18]], # walk 2 R
    12: [[13], [0, 1, 10, 11, 8, 9]], # jump R
    13: [[16, 16, 16], [0, 1, 5, 7, 8, 9, 13, 15, 16, 17, 16, 16, 16, 18, 20]], # sleep R
    14: [[17], [0, 1, 4, 8, 9, 12, 15, 15, 15, 15]], # touch R
    15: [[10], [0, 1, 4, 5, 6, 8, 9, 12, 13, 14]], # goosebumps R
    # Extra events
    16: [[1, 1, 1, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 1, 1, 14, 14, 14, 14, 14, 15, 15, 15, 15, 15, 15, 1, 1, 1, 1, 11, 11, 11, 11, 12, 12, 12, 12, 12], [0, 1, 8, 9, 5, 17, 18, 19, 20]], # idle 3
    17: [[2, 2, 2, 2, 2, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 11, 11, 11, 11, 11, 11, 14, 14, 14, 14, 14, 14, 14, 12, 12, 11, 11, 11], [0, 1, 8, 9, 5, 16, 18, 19, 20]], # idle 4
    18: [[12, 12, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16], [0, 1, 8, 9]], # sleep long
    19: [[8, 8, 19, 19, 9, 9, 18, 18], [0, 1, 8, 9, 16, 17, 18, 20]], # walk there
    20: [[3, 0, 10], [16, 17, 18, 19]], # jump and goosebumps
    21: [[20], [21]], # falling
    22: [[7], [23,24]], # stay put
    23: [[4], [23,24]], # stay put continue
    24: [[2], [24]], # stay put continue
    25: [[6], [25]], # long sleep
}

HELP_BOOK = """
DektopCat Commands

--help / -h : see the commands
--worklad [-list / -run workloadID / -create workloadID / -edit workloadID / -delete workloadID] : setting about workloads
--sleep : set the long sleep mode for Non-Toothless
--menu : see the cookbook
--tray : send Non-Toothless to taskbar tray
--config : see the configurations
""" 

PREVIEW = """
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

CURRENT_PATH = f"{os.getcwd()}\\"
GIFS_PATH = CURRENT_PATH+'desktop-cat\\media\\gifs'
FALLING_GIF_PATH = CURRENT_PATH+'desktop-cat\\media\\gifs_others\\falling.gif'
COMMAND_BG_PATH = CURRENT_PATH+'desktop-cat\\media\\messagebox.png'
TRAY_ICON_PATH = CURRENT_PATH+'desktop-cat\\media\\tray-icon.png'
FONT_PATH = CURRENT_PATH+'desktop-cat\\media\\pixelmix.ttf'

class DesktopCat():
    def __init__(self):
        self.animation_running = True
        self.falling = False
        self.long_sleep = False
        self.x = 1400
        self.y = 922
        self.initial_x = 1400
        self.initial_y = 922
        self.cycle = 0
        self.current_event_cycle = random.choice([0, 8, 1, 9, 5, 13, 6, 7, 14, 15, 16, 17, 18])
        self.current_event_cycle_index = 0
        self.EVENTS = EVENTS
        self.event_number = self.EVENTS[self.current_event_cycle][0][0]
        self.impath = GIFS_PATH
        self.fallingPath = FALLING_GIF_PATH
        self.menu_bg_image_path = COMMAND_BG_PATH
        self.fallingGif = []
        self.tray_path = TRAY_ICON_PATH
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
        self.command_prompt = tk.Toplevel()
        self.command_bg_photo = None
        self.command_canvas = None
        self.command_entry = None
        self.command_bg_image_width = 0
        self.command_bg_image_height = 0
        self.font_path = FONT_PATH
        pyglet.font.add_file(self.font_path)
        self.create_cp()
        if self.error == 0:
            self.setup_window()
            self.start_animation()
   

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
        self.animation_running = False
        deltax = event.x_root - self.drag_start_x
        new_x = self.initial_window_x + deltax
        new_x = max(min(new_x, 1800), 1100)
        deltay = event.y_root - self.drag_start_y
        new_y = self.initial_window_y + deltay
        new_y = max(min(new_y, 922), 400)
        self.window.geometry(f"+{new_x}+{new_y}")
        self.x = new_x
        self.y = new_y
        self.pos_cp()

    def on_drag_stop(self, event):
        print('on_drag_stop')
        if not self.animation_running:
            self.animation_running = True
            self.window.after(100, self.update)

    def setup_window(self):
        self.window.config(highlightbackground='black')
        self.label.pack()
        self.window.overrideredirect(True)
        self.window.wm_attributes('-transparentcolor', 'black')
        self.window.wm_attributes('-topmost', 1)
        self.window.bind("<Double-Button-1>", self.hide_window)
        self.window.bind("<ButtonPress-1>", self.on_drag_start)
        self.window.bind("<ButtonPress-3>", self.open_close_cp)
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
        # current_milliseconds = int(time.time() * 1000)
        # # print('update ', current_milliseconds-self.before_ms)
        # self.before_ms = current_milliseconds    
            
        if not self.animation_running:
            return
        
        if self.y < self.initial_y:
            if not self.falling:
                self.falling = True
                self.long_sleep = False
                self.current_event_cycle = 21
                self.current_event_cycle_index = 0
                self.cycle = 0
                self.event_number = self.EVENTS[self.current_event_cycle][0][self.current_event_cycle_index]
            self.y += 20
        elif self.y >= self.initial_y and self.falling:
            if self.command_created:
                self.set_animations_cp()
            else:
                self.current_event_cycle = random.choice([7,14,15])
            self.current_event_cycle_index = 0
            self.cycle = 0
            self.event_number = self.EVENTS[self.current_event_cycle][0][self.current_event_cycle_index]
            self.falling = False
            self.y = self.initial_y
            
        frame = self.imageGif[self.images[self.event_number]][self.cycle]
        if self.event_number in [8, 9, 3]:
            self.x -= 6
        elif self.event_number in [18, 19, 13]:
            self.x += 6
        
        self.gif_work()
        self.window.geometry('160x160+' + str(self.x) + '+' + str(self.y))
        self.label.configure(image=frame)
        self.pos_cp()
        self.window.after(1, self.event)

    def choose_event_change(self):
        if self.current_event_cycle_index < len(self.EVENTS[self.current_event_cycle][0]) - 1:
            self.current_event_cycle_index += 1
        elif self.long_sleep:
            next_event_cycle = 25
            self.current_event_cycle = next_event_cycle
            self.current_event_cycle_index = 0
        elif self.x < 1200:
            next_event_cycle = random.choice([0, 8, 1, 9, 5, 13, 6, 7, 14, 15, 16, 17, 18, 10, 11])
            self.current_event_cycle = next_event_cycle
            self.current_event_cycle_index = 0            
        elif self.x > 1700:
            next_event_cycle = random.choice([0, 8, 1, 9, 5, 13, 6, 7, 14, 15, 16, 17, 18, 2, 3])
            self.current_event_cycle = next_event_cycle
            self.current_event_cycle_index = 0
        else:
            next_event_cycle = random.choice(self.EVENTS[self.current_event_cycle][1])
            while (self.x < self.initial_x-100 or self.x > self.initial_x+100) and next_event_cycle == 19:
                next_event_cycle = random.choice(self.EVENTS[self.current_event_cycle][1])                
            self.current_event_cycle = next_event_cycle
            self.current_event_cycle_index = 0
        return self.EVENTS[self.current_event_cycle][0][self.current_event_cycle_index]

    def show_window(self):
        print('show_window')
        self.window.after(0, self.window.deiconify)
        if self.command_created:
            self.command_prompt.after(0, self.command_prompt.deiconify)        
        if self.icon_created:
            self.icon_created = False
            self.icon.stop()        

    def hide_window(self, event):
        print('hide_window')
        self.window.withdraw()
        self.command_prompt.withdraw()
        self.create_tray_icon()

    def exit_application(self):
        print('exit_application')
        self.icon.stop()
        if self.command_prompt != None:
            self.command_prompt.destroy()
        self.window.quit()

    def create_tray_icon(self):
        print('create_tray_icon')
        icon_image = Image.open(self.tray_path)
        menu = (item('Show', lambda: self.show_window(), default=True), item('Exit', self.exit_application))
        self.icon = pystray.Icon("DesktopCat", icon_image, "DesktopCat", menu)
        self.icon_created = True
        self.icon.run()

    def open_close_cp(self, event):
        if not self.command_created:
            print('open cp')
            self.set_animations_cp()
            self.command_prompt.deiconify()
            self.command_created = True
            self.pos_cp()
        elif self.command_prompt != None:
            print('close cp')
            self.reset_animations_cp()
            self.command_prompt.withdraw()
            self.command_created = False

    def create_cp(self):
        command_bg_image = Image.open(self.menu_bg_image_path)
        self.command_bg_image_height = command_bg_image.height
        self.command_bg_image_width = command_bg_image.width
        # Create a command_canvas to display the background image
        # 360 = self.command_bg_image.width // 180 = self.command_bg_image.height
        self.command_canvas = tk.Canvas(self.command_prompt, width=self.command_bg_image_width, height=self.command_bg_image_height, highlightthickness=0, bg='black')
        self.command_canvas.pack(fill="both", expand=True)
        
        self.command_prompt.config(highlightbackground='black')
        
        self.command_prompt.overrideredirect(True)
        self.command_prompt.wm_attributes('-transparentcolor', 'black')
        self.command_prompt.wm_attributes('-topmost', 1)
        
        # Text widget to get user input with double row height
        entry_font = ("pixelmix", 10)
        # entry_font = ("Minecraftia", 11)
        entry_width = 33  # Set the width of the command_entry widget
        entry_height = 1  # Set the height of the command_entry widget to 1-2 rows
        self.command_entry = tk.Text(self.command_prompt, bg='#fff7f5', fg='#111111', font=entry_font, borderwidth=0, width=entry_width, height=entry_height, insertontime=0, cursor='arrow')
        self.command_entry.bind("<Return>", self.on_enter_pressed)
        # Center the command_entry widget with padding
        self.command_entry.place(relx=0.5, rely=0.5, anchor="center")
        self.command_entry.config(padx=2, pady=18)
        
        self.command_bg_photo = ImageTk.PhotoImage(command_bg_image)
        try:
            self.command_canvas.create_image(0, 0, anchor="nw", image=self.command_bg_photo)
        except Exception as e:
            print(e)
        self.pos_cp()
        self.command_prompt.withdraw()
            
    def pos_cp(self):
        self.command_prompt.geometry(f'{self.command_bg_image_width}x{self.command_bg_image_height}+' + str(self.x-295) + '+' + str(self.y-110))
    
    def set_animations_cp(self):
        self.current_event_cycle = random.choice([22,23,24])
        self.current_event_cycle_index = 0
        self.cycle = 0
        self.event_number = self.EVENTS[self.current_event_cycle][0][self.current_event_cycle_index]
    
    def reset_animations_cp(self):
        self.current_event_cycle = random.choice([0, 8, 1, 9, 5, 13, 7, 15, 16, 17, 18])
        self.current_event_cycle_index = 0
        self.cycle = 0
        self.event_number = self.EVENTS[self.current_event_cycle][0][self.current_event_cycle_index]        

    def on_enter_pressed(self, event):
        message = self.command_entry.get("1.0", "end-1c")  # Get all text from the widget
        self.command_entry.delete("1.0", "end")  # Delete all text from the widget
        message = message.strip()
        if message.startswith('--'):
            self.parser(message.split())
        else:
            print(message)
    
    def parser(self, message):
        if message[0] == '--workload' or message[0] == '--w':
            if message[1] == '-list' or message[1] == '-l':
                print('Workload List\n 1- WorkloadVscode\n 2- ChromeOthers\n 3- Project2\n')
            if message[1] == '-run' or message[1] == '-r':
                if message[2] != None:
                    print(f'Workload {message[2]} running...\n')
                else: print('Missing arguments: WorkloadName!\n')
            if message[1] == '-edit' or message[1] == '-e':
                if message[2] != None:
                    print(f'Workload {message[2]} settings showing...\n')
                else: print('Missing arguments: WorkloadName!\n')
            if message[1] == '-create' or message[1] == '-c':
                editMode = False
                if message[2] == '-edit' or message[2] == '-e':
                    editMode = True
                    if message[3] != None:
                        print(f'New Workload Creating... See the edit settings for Workload {message[3]}\n')
                    else: print('Missing arguments: WorkloadName!\n')
                elif message[3] != None:
                    print(f'New Workload Creating... See the edit settings for Workload {message[3]}\n')
                else: print('Missing arguments: WorkloadName!\n')
                
        elif message[0] == '--sleep' or message[0] == '--s':
            self.long_sleep = not self.long_sleep
            print(f'Good Night Non-Toothless... Long Sleep {self.long_sleep}\n')
            
        elif message[0] == '--tray' or message[0] == '--t':
            print(f'Cat Hidden\n')
            
        elif message[0] == '--config' or message[0] == '--c':
            print(f'Config settings are shown...\n')
            
        elif message[0] == '--help' or message[0] == '--h':
            print(HELP_BOOK)          
                                  
        else: print('Unknown error about arguments!')

       
if __name__ == '__main__':
    desktop_cat = DesktopCat()