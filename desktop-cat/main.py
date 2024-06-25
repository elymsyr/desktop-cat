import random, webbrowser, traceback, pyglet, os, json, subprocess
import tkinter as tk
from PIL import Image, ImageTk
from time import sleep
from pystray import MenuItem as item, Icon
# for index, (key, value) in enumerate(chrome.items(), start=1):
from set import *
import workload

class DesktopCat():
    def __init__(self):
        self.font = ('pixelmix', 10)
        self.chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"
        self.prefix = "*"
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
        self.fallingGif = []
        self.flyPNG = []
        self.imageGif = {}
        self.white = True
        self.images = []
        self.position = 0
        self.before_ms = 0
        self.icon = None
        self.icon_created = False
        self.command_created = False
        self.message = None
        self.window = tk.Tk()
        self.var = tk.StringVar()
        self.book = tk.Toplevel(self.window)
        self.label = tk.Label(self.window, bd=0, bg='black')
        self.book_bg_image = None
        self.book_bg_image_width = 0
        self.book_bg_image_height = 0
        self.book_bg_photo = None        
        self.command_prompt = tk.Toplevel(self.window)
        self.command_bg_photo = None
        self.command_canvas = None
        self.command_entry = None
        self.book_photo = None
        self.command_bg_image_width = 0
        self.command_bg_image_height = 0
        self.text_content = ""
        self.wl = workload.Workload()
        self.error = self.load_images() 
        pyglet.font.add_file(FONT_PATH)
        self.create_book()
        self.create_cp()
        self.open_close_book(True)
        self.open_close_cp()
        self.help()
        self.write_text("\nDo not move the cat fast.\nThere is a bug :(\nRight click to cat!")
        self.reload_config()
        if self.error == 0:
            self.setup_window()
            self.start_animation()
            
    def reload_config(self):
        try:
            data = self.get_config()
            self.prefix = data['config']['prefix']
            self.chrome_path = data['config']['chrome_settings']['chrome_path']
            self.font = (data['config']['fonts']['current_font_name'], data['config']['fonts']['default_font_size'])
            self.wl.reload_config(data['config']['chrome_settings']['chrome_profile_path'], data['config']['chrome_settings']['chrome_profile_name'], self.chrome_path)
            self.write_text("\nConfigurations reloaded...")
        except: self.write_text("\nA problem occured during the data reload process :/")
                    
    def create_book(self):
        # Create a book_canvas to display the background image
        self.book_bg_image = Image.open(BOOKS_PATH + "\\book_test.png")
        self.book_canvas = tk.Canvas(self.book, width=self.book_bg_image.width, height=self.book_bg_image.height, highlightthickness=0, bg='black')
        self.book_canvas.pack(fill="both", expand=True)

        self.book.config(highlightbackground='black', )
        self.book.overrideredirect(True)
        self.book.wm_attributes('-transparentcolor', 'black')
        self.book.wm_attributes('-topmost', 1)

        self.book_bg_photo = ImageTk.PhotoImage(self.book_bg_image)
        try:
            self.book_canvas.create_image(0, 0, anchor="nw", image=self.book_bg_photo)
        except Exception as e:
            tb_info = traceback.extract_tb(e.__traceback__)
            row_number = tb_info[-1].lineno
            print(f"Exception at {row_number}: {e}")
        # Add a frame to hold the text box
        self.text_frame = tk.Frame(self.book_canvas, bg='black')
        self.text_frame.place(relx=0.093, rely=0.08, relwidth=0.81, relheight=0.85)  # Adjust the position and size of the frame
        # Add a text box to the frame
        self.text_box = tk.Text(self.text_frame, wrap=tk.WORD, font=self.font, bg='#e8ebef', fg='#111111')
        self.text_box.pack(fill="both", expand=True)
        self.text_box.config(border=0, highlightthickness=0, state=tk.DISABLED)
        self.book.bind('<Escape>', lambda event: self.open_close_book(False))
        self.book.bind('<Button-3>', lambda event: self.open_close_book(False))
        self.pos_book()
        self.open_close_book(False)
        
    def open_close_book(self, onoff):
        if not onoff:
            self.book.withdraw()
        else:
            self.book.deiconify()

    def pos_book(self):
        self.book.geometry(f'{self.book_bg_image.width}x{self.book_bg_image.height}+' + str(self.x-320) + '+' + str(self.y-620)) # ?!

    def write_text(self, text):
        # Add text to the text box
        self.text_box.config(state=tk.NORMAL)
        # self.insert_text(text)
        self.text_box.insert(tk.END, "\n")
        self.text_box.insert(tk.END, text)
        self.text_box.see(tk.END)  # Scroll to the end
        self.text_box.config(state=tk.DISABLED)
        
    def insert_text(self, text, sleeptime = 0.01):
        while sleeptime>0:
            for row in text.split('\n'):
                for letter in row:
                    self.text_box.insert(tk.END, text)
                    sleep(sleeptime)
                self.text_box.insert(tk.END, "\n")
    
    def reset_cycle(self, events = [0, 8, 1, 9, 5, 13, 6, 7, 14, 15, 16, 17, 18], event_cycle=True):
        if event_cycle:
            self.current_event_cycle = random.choice(events)
        self.current_event_cycle_index = 0
        self.cycle = 0
        self.event_number = self.EVENTS[self.current_event_cycle][0][self.current_event_cycle_index]

    def load_images(self):
        self.images = os.listdir(GIFS_PATH)
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
                self.imageGif[image] = [tk.PhotoImage(file=os.path.join(GIFS_PATH, image), format=f'gif -index {i}') for i in range(defrange)]
            except tk.TclError as e:
                print(f"Error loading {os.path.join(GIFS_PATH, image)} : {e}")
                error = 1
        self.imageGif['falling'] = [tk.PhotoImage(file=FALLING_GIF_PATH, format=f'gif -index {i}') for i in range(4)]
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
        new_x = max(min(new_x, 1800), 400)
        deltay = event.y_root - self.drag_start_y
        new_y = self.initial_window_y + deltay
        new_y = max(min(new_y, 922), 400)
        self.window.geometry(f"+{new_x}+{new_y}")
        self.x = new_x
        self.y = new_y
        self.pos_cp()
        self.pos_book()        

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
        self.hide_window()

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
        self.pos_book()
        self.window.after(1, self.event)

    def choose_event_change(self):
        if self.current_event_cycle_index < len(self.EVENTS[self.current_event_cycle][0]) - 1:
            self.current_event_cycle_index += 1
        elif self.long_sleep:
            next_event_cycle = 25
            self.current_event_cycle = next_event_cycle
            self.current_event_cycle_index = 0
        elif self.x < 500:
            next_event_cycle = random.choice([0, 8, 1, 9, 5, 13, 6, 7, 14, 15, 16, 17, 18, 10, 11])
            self.current_event_cycle = next_event_cycle
            self.current_event_cycle_index = 0            
        elif self.x > 1700:
            next_event_cycle = random.choice([0, 8, 1, 9, 5, 13, 6, 7, 14, 15, 16, 17, 18, 2, 3])
            self.current_event_cycle = next_event_cycle
            self.current_event_cycle_index = 0
        else:
            next_event_cycle = random.choice(self.EVENTS[self.current_event_cycle][1])
            while (self.x < INITIAL_X-500 or self.x > INITIAL_X+100) and next_event_cycle == 19:
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

    def hide_window(self, event=None):
        print('hide_window')
        self.window.withdraw()
        self.command_prompt.withdraw()
        self.open_close_book(False)
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
        icon_image = Image.open(TRAY_ICON_PATH)
        menu = (item('Show', lambda: self.show_window(), default=True), item('Exit', self.exit_application))
        self.icon = Icon("DesktopCat", icon_image, "DesktopCat", menu)
        self.icon_created = True
        self.icon.run()

    def open_close_cp(self, close=False, event=None):
        self.pos_book()
        if close and self.command_prompt != None and not self.icon_created and self.command_created:
            print('close cp')
            if not self.long_sleep:
                self.reset_cycle([0, 8, 1, 9, 5, 13, 7, 15, 16, 17, 18])
            self.command_prompt.withdraw()
            self.command_created = False
            self.open_close_book(False)
        else:
            if not self.command_created and not self.icon_created:
                print('open cp')
                if not self.long_sleep:
                    self.reset_cycle([22,23,24]) 
                self.command_prompt.deiconify()
                self.pos_cp()
                self.command_created = True
                self.command_entry.focus_set()
            elif self.command_prompt != None and not self.icon_created:
                print('close cp')
                if not self.long_sleep:
                    self.reset_cycle([0, 8, 1, 9, 5, 13, 7, 15, 16, 17, 18])
                self.open_close_book(False)
                self.command_prompt.withdraw()
                self.command_created = False

    def create_cp(self):
        command_bg_image = Image.open(COMMAND_BG_PATH)
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
        # FONT = ("Minecraftia", 11)
        entry_width = 33  # Set the width of the command_entry widget
        entry_height = 1  # Set the height of the command_entry widget to 1-2 rows
        self.command_entry = tk.Text(self.command_prompt, bg='#fff7f5', fg='#111100', font=self.font, borderwidth=0, width=entry_width, height=entry_height, cursor='arrow')
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

    def return_var(self):
        self.open_close_book(True)
        self.window.wait_variable(self.var)
        input = self.var.get()
        self.var.set("")  # Reset self.var to an empty string
        return input
    
    def check_error(self, expected_error, extra_error_info = '', write = True):
        if expected_error in list(ERROR_LIST.keys()):
            if write: self.write_text(f'\n{expected_error}: {ERROR_LIST[expected_error]}\n  {extra_error_info}\n  (See the Help Book with the command {self.prefix}h)')
        else: return True

    def get_next(self, message, word):
        if len(message) > message.index(word)+1:
            try:
                return str(message[message.index(word)+1]) 
            except:
                return 'error$99'
        return 'error$98'

    def on_enter_pressed(self, event):
        message = self.command_entry.get("1.0", "end-1c")  # Get all text from the widget
        self.var.set(message)
        self.command_entry.delete("1.0", "end")  # Delete all text from the widget
        message = message.strip()
        if message.startswith(self.prefix) and self.white:
            self.white = False
            self.parser(message[1:].split())
            self.white = True
        else:
            print(message)
        return message
    
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
                        case 'h':
                            self.open_close_book(True)
                            self.write_text("\n *w can be used with\n   list/l\n   run/r [Workload Name]\n   save/s [Workload Name]\n   edit/e [Workload Name]\n   delete/d [Workload Name]]")
                        case 'l' | 'list': self.workload_list()
                        case 's' | 'save' | 'r' | 'run' | 'e' | 'edit' | 'd' | 'delete':
                            after_next = self.get_next(message, next)
                            if self.check_error(after_next, extra_error_info=f"*w {next} requires a Workload Name."):
                                self.workload_edit(after_next, next)
                        case _ : self.check_error('error$99')
            elif message[0] == 's' or message[0] == 'sleep':
                self.sleep()
            elif message[0] == 'tray':
                self.tray()
            elif message[0] == 'config':
                next = self.get_next(message, message[0])
                if self.check_error(next, False):
                    if next == 'h':
                        next = self.get_next(message, next)
                        if next in list(ERROR_LIST.keys()):
                            self.get_config_help()
                        elif self.check_error(next):
                            data = self.get_config()
                            values = []
                            for key, value in data['config'].items():
                                if isinstance(value, dict):
                                    values.append(key)
                            if next in values:
                                self.get_subconfig_help(next)
                            else: self.check_error('error$99')
                    elif next == 'e':
                        next = self.get_next(message, next)
                        if next in list(ERROR_LIST.keys()):
                            self.edit_config()
                    elif next == 'r':
                        next = self.get_next(message, next)
                        if next in list(ERROR_LIST.keys()):
                            self.reload_config()
                else:
                    self.get_config_help()
                        
            elif message[0] == 'exit':
                self.exit_application()
            elif message[0] == 'q':                
                self.google_search(message)
            elif message[0] == 'book' or message[0] == 'b':                
                self.open_close_book(True)
        else: self.check_error('error$98')
        
    def google_search(self, query):
        webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(self.chrome_path))
        webbrowser.get('chrome').open(f"https://www.google.com/search?q={' '.join(query)}")
        self.open_close_cp(close=True)
        
    def get_config(self):
        with open(CONFIG_PATH, 'r') as file:
            return json.load(file)
        
    def write_config(self, data):
        with open(CONFIG_PATH, 'w') as file:
            json.dump(data, file, indent=4)        
        
    def get_config_help(self):
        data = self.get_config()
        self.write_text(f"\nConfiguration commands: ")
        self.write_text(f"{self.prefix}config e to edit.")
        self.write_text(f"{self.prefix}config r to reload.\n")
        self.write_text('Configs:')
        for key, value in data['config'].items():
            if isinstance(value, dict):
                self.write_text(f"  {self.prefix}config h {key}")
                for sub_key in list(data['config'][key]):
                    self.write_text(f"    {sub_key}")
            else: self.write_text(f"  {key} {value}")

    def edit_config(self):
        try:
            subprocess.run(CONFIG_PATH, shell=True)
        except Exception as e:
            return str(e)
        return ""        

    def get_subconfig_help(self, main_key):
        data = self.get_config()
        self.write_text(f"\n{main_key}")
        for key, value in data['config'][main_key].items():
            self.write_text(f"\n{key}: {value}")
            
        return

    def workload_list(self):
        self.open_close_book(True)
        data = None
        with open(CONFIG_PATH, 'r') as file:
            data = json.load(file)
        i=0
        if len(list(data['workloads'].keys())) > 0:
            self.write_text(f"\nWorkloads:")
            for workload in list(data['workloads'].keys()):
                self.write_text(f"{i}- {workload}\n")
                i+=1
        else: self.write_text(f"\nNo workload founded...\n")
    
    def workload_edit(self, workload_name, operation):
        self.write_text(f"\nWrite {self.prefix}cancel to stop operation.")
        error = ""
        self.open_close_book(True)
        match operation:
            case 's' | 'save': self.save_workload(workload_name)
            case 'r' | 'run': 
                error = self.wl.run_workload(workload_name)
                self.write_text(f"\n\n{error}")
            case 'e' | 'edit': self.write_text("\nComing soon...\n")
            case 'd' | 'delete': self.write_text("\nComing soon...\n")
            case _: self.write_text('\n\nerror?')

    def save_workload(self, workload_name):
        new_vscode = {}
        new_chrome = {}
        code_url = ''
        data = None
        with open(CONFIG_PATH, 'r') as file:  # Use raw string to handle backslashes
            data = json.load(file)
        vscode = self.wl.findVSCode()
        # chrome = self.wl.findChrome()
        chrome = self.wl.get_open_tabs_urls()
        
        for key in list(vscode.keys()):  # Convert dict_keys to list
            if key in data['workload_data']['vscode']:
                code_url = data['workload_data']['vscode'][key]
            else:
                self.write_text(f'\nEnter path to your project {key}...')
                code_url_takin = self.return_var()
                if code_url_takin == '*cancel':
                    self.write_text(f"\n\nOops...\n")
                    return
                while (len(code_url_takin) > 0 and (code_url_takin.split('\\'))[-1] != key) :
                    self.write_text(f'\nLeaving it empty is an option but... maybe try again?')
                    code_url_takin = self.return_var()
                    if code_url_takin == '*cancel':
                        self.write_text(f"\n\nOops...\n")
                        return                    
                code_url = code_url_takin
                if len(code_url) > 0:
                    data['workload_data']['vscode'][key] = code_url
            new_vscode[key] = [code_url, vscode[key]]
            
        self.open_close_book(True)
            
        # self.write_text('\nExample: \'1-5 *4 .10\' :\n   .n to add from 1 to n\n   n-m to add from n to m\n   n to add n\n   *n to exclude n\n   *n-m to exclude from n to m\n')
        # self.write_text(self.wl.print_chrome(chrome, 10))
        # self.write_text('\nChoose which tabs will be included...')
        # input_numbers = self.return_var()
        # if input_numbers == '*cancel':
        #     self.write_text(f"\n\nOops...\n")
        #     return        
        # selected = self.wl.process_input(input_numbers, chrome)
        # while selected == None:
        #     self.write_text('\nPlease specify the numbers correctly:\n   .n to add from 1 to n\n   n-m to add from n to m   \n  n to add n\n   *n to exclude n\n   *n-m to exclude from n to m\nInput Waiting: \n')
        #     input_numbers = self.return_var()
        #     if input_numbers == '*cancel':
        #         self.write_text(f"\n\nOops...\n")
        #         return             
        #     selected = self.wl.process_input(input_numbers, chrome)
        # self.write_text(self.wl.print_chrome(chrome, 10))                               
        # new_chrome = selected
        
        # data['workloads'][workload_name] = {"vscode": new_vscode,"chrome": new_chrome}
        data['workloads'][workload_name] = {"vscode": new_vscode,"chrome": chrome}
            
        with open(CONFIG_PATH, 'w') as file:
            json.dump(data, file, indent=4)
        self.write_text(f"\nWorkload {workload_name} saved.")

    def sleep(self):
        self.long_sleep = not self.long_sleep
        self.write_text(f'\nLong Sleep {self.long_sleep}')
    
    def tray(self):
        self.hide_window()
        self.write_text(f'\nHidded')
        
    def help(self):
        self.open_close_book(True)
        self.write_text("\n")
        self.write_text(HELP_BOOK())

if __name__ == '__main__':
    desktop_cat = DesktopCat()