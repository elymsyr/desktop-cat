import pyautogui
import random
import tkinter as tk
import os
from tkinter import messagebox
from PIL import Image, ImageTk
import pystray
from pystray import MenuItem as item
import threading

class DesktopCat:
    def __init__(self):
        self.animation_running = True
        self.x = 1400
        self.cycle = 0
        self.position = 0
        self.current_event_cycle = random.choice([0, 8, 1, 9, 5, 13, 20])
        self.current_event_cycle_index = 0
        self.EVENTS = {
            # Left events
            0: [[1, 1, 1, 1, 2, 2, 2, 2, 1, 1, 4, 4, 4, 4, 1, 1, 1, 1, 2, 2], [0, 1, 2, 3, 5, 8, 9, 10, 11, 13, 16, 17, 18]],
            1: [[2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 5, 5, 5, 5, 5, 5, 5, 1, 1, 1], [0, 1, 2, 3, 5, 8, 9, 10, 11, 13, 16, 17, 18]],
            2: [[8, 8, 8], [0, 1, 2, 3, 4, 7, 8, 9, 10, 11, 12, 15, 16, 17, 18]],
            3: [[9, 9, 9], [0, 1, 2, 3, 4, 7, 8, 9, 10, 11, 12, 15, 16, 17, 18]],
            4: [[3], [0, 1, 2, 3, 8, 9]],
            5: [[6, 6, 6], [0, 1, 5, 7, 8, 9, 13, 15, 16, 17, 5, 5, 5, 5, 18, 20]],
            6: [[7], [0, 1, 4, 7, 7, 7, 7, 8, 9, 12]],
            7: [[0], [0, 1, 4, 5, 6, 8, 9, 12, 13, 14]],
            # Right events
            8: [[11, 11, 11, 11, 12, 12, 12, 12, 11, 11, 14, 14, 14, 14, 11, 11, 11, 11, 12, 12], [0, 1, 2, 3, 5, 8, 9, 10, 11, 13, 16, 17, 18]],
            9: [[12, 12, 12, 12, 12, 12, 11, 11, 11, 11, 15, 15, 15, 15, 15, 15, 15, 11, 11, 11], [0, 1, 2, 3, 5, 8, 9, 10, 11, 13, 16, 17, 18]],
            10: [[18, 18, 18], [0, 1, 2, 3, 4, 7, 8, 9, 10, 11, 12, 15, 16, 17, 18]],
            11: [[19, 19, 19], [0, 1, 2, 3, 4, 7, 8, 9, 10, 11, 12, 15, 16, 17, 18]],
            12: [[13], [0, 1, 10, 11, 8, 9]],
            13: [[16, 16, 16], [0, 1, 5, 7, 8, 9, 13, 15, 16, 17, 5, 5, 5, 5, 18, 20]],
            14: [[17], [0, 1, 4, 8, 9, 12, 15, 15, 15, 15]],
            15: [[10], [0, 1, 4, 5, 6, 8, 9, 12, 13, 14]],
            # Extra events
            16: [[1, 1, 1, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 1, 1, 14, 14, 14, 14, 14, 15, 15, 15, 15, 15, 15, 1, 1, 1, 1, 11, 11, 11, 11, 12, 12, 12, 12, 12], [0, 1, 8, 9, 5, 17, 18, 19, 20]],
            17: [[2, 2, 2, 2, 2, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 11, 11, 11, 11, 11, 11, 14, 14, 14, 14, 14, 14, 14, 12, 12, 11, 11, 11], [0, 1, 8, 9, 5, 16, 18, 19, 20]],
            18: [[12, 12, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16], [0, 1, 8, 9]],
            19: [[8, 8, 19, 19, 9, 9, 18, 18], [0, 1, 8, 9, 16, 17, 18, 20]],
            20: [[3, 0, 10], [16, 17, 18, 19]],
        }
        self.event_number = self.EVENTS[self.current_event_cycle][0][0]
        self.impath = 'C:\\Users\\orhun\\OneDrive\\Belgeler\\GitHub\\desktop-cat\\desktop-cat\\Cats\\greyCat-160x160-10\\gifs\\'
        self.tray_path = 'C:\\Users\\orhun\\OneDrive\\Belgeler\\GitHub\\desktop-cat\\desktop-cat\\Cats\\greyCat-160x160-10\\tray-icon.png'
        self.imageGif = {}
        self.images = []
        self.position = 0
        self.icon = None
        self.window = tk.Tk()
        self.label = tk.Label(self.window, bd=0, bg='black')
        self.error = self.load_images()
        if self.error == 0:
            self.setup_window()
            self.start_animation()

    def load_images(self):
        self.images = os.listdir(self.impath)
        error = 0
        for image in self.images:
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
        return error

    def setup_window(self):
        self.window.config(highlightbackground='black')
        self.label.pack()
        self.window.overrideredirect(True)
        self.window.wm_attributes('-transparentcolor', 'black')
        self.window.wm_attributes('-topmost', 1)
        self.window.bind("<Double-Button-1>", self.hide_window)

    def start_animation(self):
        self.window.after(1, self.update, self.cycle, self.event_number, self.x)
        self.window.mainloop()

    def event(self, cycle, event_number, x):
        times = [600, 1200, 1200, 1050, 900]
        if event_number in [1, 2, 4, 5] or event_number - 10 in [1, 2, 4, 5]:
            self.window.after(200, self.update, cycle, event_number, x)
        elif event_number in [8, 9, 0] or event_number - 10 in [8, 9, 0]:
            self.window.after(150, self.update, cycle, event_number, x)
        elif event_number in [6, 16]:
            self.window.after(1000, self.update, cycle, event_number, x)
        elif event_number in [3, 13]:
            self.window.after(160, self.update, cycle, event_number, x)
        elif event_number in [7, 17]:
            self.window.after(160, self.update, cycle, event_number, x)

    def gif_work(self, cycle, frames, event_number):
        if cycle < len(frames) - 1:
            cycle += 1
        else:
            cycle = 0
            event_number = self.choose_event_change()
        return cycle, event_number

    def update(self, cycle, event_number, x):
        if not self.animation_running:
            return
        frame = self.imageGif[self.images[event_number]][cycle]
        if event_number in [8, 9, 3]:
            x -= 8
            self.position = x
        elif event_number in [18, 19, 13]:
            x += 8
            self.position = x

        cycle, event_number = self.gif_work(cycle, self.imageGif[self.images[event_number]], event_number)
        self.window.geometry('160x160+' + str(x) + '+922')
        self.label.configure(image=frame)
        self.window.after(1, self.event, cycle, event_number, x)

    def choose_event_change(self):
        if self.current_event_cycle_index < len(self.EVENTS[self.current_event_cycle][0]) - 1:
            self.current_event_cycle_index += 1
        else:
            next_event_cycle = random.choice(self.EVENTS[self.current_event_cycle][1])
            while self.position > 1600 and next_event_cycle in [2, 3, 4]:
                next_event_cycle = random.choice(self.EVENTS[self.current_event_cycle][1])
            while self.position < 1200 and next_event_cycle in [10, 11, 12]:
                next_event_cycle = random.choice(self.EVENTS[self.current_event_cycle][1])
            self.current_event_cycle = next_event_cycle
            self.current_event_cycle_index = 0
        return self.EVENTS[self.current_event_cycle][0][self.current_event_cycle_index]

    def show_window(self):
        self.animation_running = True
        self.window.after(0, self.window.deiconify)
        self.icon.stop()

    def hide_window(self, event=None):
        self.animation_running = False
        self.window.withdraw()
        self.create_tray_icon()

    def exit_application(self, icon, item):
        icon.stop()
        self.window.quit()

    def create_tray_icon(self):
        icon_image = Image.open(self.tray_path)
        menu = (item('Show', lambda: self.show_window()), item('Exit', self.exit_application))
        self.icon = pystray.Icon("name", icon_image, "Tkinter App", menu)
        self.icon.run()


if __name__ == '__main__':
    desktop_cat = DesktopCat()
