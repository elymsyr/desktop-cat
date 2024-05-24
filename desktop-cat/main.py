import random, webbrowser, traceback, pyglet, os
import tkinter as tk
from PIL import Image, ImageTk
from pystray import MenuItem as item, Icon

from set import *

EXAMPLE_WORKLOADS = ['Workload_1', 'Workload_2', 'Workload_3']

class DesktopCat():
    def __init__(self):
        self.animation_running = True
        self.falling = False
        self.long_sleep = False
        self.x = 1400
        self.y = 922
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
            
    def reset_cycle(self, events = [0, 8, 1, 9, 5, 13, 6, 7, 14, 15, 16, 17, 18], event_cycle=True):
        if event_cycle:
            self.current_event_cycle = random.choice(events)
        self.current_event_cycle_index = 0
        self.cycle = 0
        self.event_number = self.EVENTS[self.current_event_cycle][0][self.current_event_cycle_index]
   

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
        self.window.title("DesktopCat")
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
        
        if self.y+40 < INITIAL_Y:
            if not self.falling:
                self.falling = True
                self.long_sleep = False
                self.reset_cycle([21])
            if abs(self.y-INITIAL_Y) >= 20:
                self.y += 20
            else: self.y += abs(self.y-INITIAL_Y)                
        elif self.y < INITIAL_Y:
            self.falling = True
            if abs(self.y-INITIAL_Y) >= 20:
                self.y += 20
            else: self.y += abs(self.y-INITIAL_Y)
        elif abs(self.y-INITIAL_Y) <= 20 and self.falling:
            if self.command_created:
                self.reset_cycle([22,23,24])
            else:
                self.current_event_cycle = random.choice([7,14,15, 0, 8, 1, 9, 5, 13, 6, 7, 14, 15, 16, 17, 18]) # [0, 8, 1, 9, 5, 13, 6, 7, 14, 15, 16, 17, 18] [7,14,15]
            self.reset_cycle(event_cycle=False)
            self.falling = False
            self.y = INITIAL_Y
            
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
            while (self.x < INITIAL_X-100 or self.x > INITIAL_X+100) and next_event_cycle == 19:
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
        if self.icon_created:
            self.icon.stop()
        if self.command_prompt != None:
            self.command_prompt.destroy()
        self.window.quit()

    def create_tray_icon(self):
        print('create_tray_icon')
        icon_image = Image.open(self.tray_path)
        menu = (item('Show', lambda: self.show_window(), default=True), item('Exit', self.exit_application))
        self.icon = Icon("DesktopCat", icon_image, "DesktopCat", menu)
        self.icon_created = True
        self.icon.run()

    def open_close_cp(self, close=False, event=None):
        if close and self.command_prompt != None and not self.icon_created and self.command_created:
            print('close cp')
            self.reset_cycle([0, 8, 1, 9, 5, 13, 7, 15, 16, 17, 18])
            self.command_prompt.withdraw()
            self.command_created = False
        else:
            if not self.command_created and not self.icon_created:
                print('open cp')
                self.reset_cycle([22,23,24]) 
                self.command_prompt.deiconify()
                self.pos_cp()
                self.command_created = True
                self.command_entry.focus_set()
            elif self.command_prompt != None and not self.icon_created:
                print('close cp')
                self.reset_cycle([0, 8, 1, 9, 5, 13, 7, 15, 16, 17, 18])
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
        
        self.command_prompt.bind('<Escape>', lambda event: self.open_close_cp(close=True))
        
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
            tb_info = traceback.extract_tb(e.__traceback__)
            row_number = tb_info[-1].lineno
            print(f"Exception at {row_number}: {e}")
        self.pos_cp()
        self.command_prompt.withdraw()
            
    def pos_cp(self):
        self.command_prompt.geometry(f'{self.command_bg_image_width}x{self.command_bg_image_height}+' + str(self.x-295) + '+' + str(self.y-110))  

    def on_enter_pressed(self, event):
        message = self.command_entry.get("1.0", "end-1c")  # Get all text from the widget
        self.command_entry.delete("1.0", "end")  # Delete all text from the widget
        message = message.strip()
        if message.startswith(PREFIX):
            self.parser(message[1:].split())
        else:
            print(message)
    
    def parser(self, message):
        if len(message) > 0:
            if message[0] == '*':
                self.open_close_cp(close=True)
            if message[0] == 'h' or message[0] == 'help':
                self.help()               
            elif message[0] == 'workload' or message[0] == 'w':
                next = self.get_next(message, message[0])
                if self.check_error(next, extra_error_info=f"*w requires an argument."):
                    match next:
                        case 'l' | 'list': self.workload_list()
                        case 'c' | 'create' | 'r' | 'run' | 'e' | 'edit' | 'd' | 'delete' | 'ce' | 'create-edit':
                            after_next = self.get_next(message, next)
                            if self.check_error(after_next, extra_error_info=f"*w {next} requires a Workload Name."):
                                self.workload_edit(after_next, next)
                        case _ : self.check_error('error$99')
            elif message[0] == 's' or message[0] == 'sleep':
                self.sleep()
            elif message[0] == 'tray':
                self.tray()
            elif message[0] == 'config':
                self.config()
                next = self.get_next(message, message[0])
                if self.check_error(next):
                    match next:
                        case 'shortcut':
                            after_next = self.get_next(message, next)
                            if self.check_error(after_next, extra_error_info=f"Add your shortcut. (default ctrl+shift+a)"):
                                self.shortcut(after_next)
                        case _ : self.check_error('error$99')
            elif message[0] == 'exit':
                self.exit_application()                
            else: self.google_search(message)
        else: self.check_error('error$98')
        
    def google_search(self, query):
        webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(CHROME_PATH))
        webbrowser.get('chrome').open(f"https://www.google.com/search?q={' '.join(query)}")
        self.open_close_cp(close=True)

    def workload_list(self):
        print(EXAMPLE_WORKLOADS)
    def workload_edit(self, workload_name, operation):
        print('edit')
        match operation:
            case 'c' | 'create': print(f'create {workload_name}')
            case 'r' | 'run': print(f'run {workload_name}')
            case 'e' | 'edit': print(f'edit {workload_name}')
            case 'd' | 'delete': print(f'delete {workload_name}')
            case 'ce' | 'create-edit': print(f'create with edit {workload_name}')
            case _: print('error')

    def sleep(self):
        self.long_sleep = not self.long_sleep
        print(f'Long Sleep {self.long_sleep}\n')
    def tray(self):
        self.hide_window()
        print('tray')
    def config(self):
        print('config')
    def shortcut(self, new_shortcut):
        try:
            self.bind_shortcut(self.open_cp, new_shortcut)
        except Exception as e:
            tb_info = traceback.extract_tb(e.__traceback__)
            row_number = tb_info[-1].lineno
            print(f"Shortcuts is not available | Exception at {row_number}: {e}")
    def help(self):
        print(HELP_BOOK())
        
    def check_error(self, expected_error, extra_error_info = ''):
        if expected_error in list(ERROR_LIST.keys()):
            print(f'\n{expected_error}: {ERROR_LIST[expected_error]}\n  {extra_error_info}\n  (See the Help Book with the command {PREFIX}h)')
        else: return True

    def get_next(self, message, word):
        if len(message) > message.index(word)+1:
            try:
                return str(message[message.index(word)+1]) 
            except:
                return 'error$99'
        return 'error$98'
          
if __name__ == '__main__':
    desktop_cat = DesktopCat()