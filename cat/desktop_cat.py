from os import listdir
from os.path import join, exists
from pyglet.font import add_file
from random import choice
from tkinter import Tk, Label, PhotoImage, TclError
from PIL import Image
from traceback import format_exc
from pystray import MenuItem as item, Icon
from settings import functions
from workbook import Workbook
from messagebox import MessageBox
from workload import Workload
from custom_parser import Parser

INITIAL_X = 1400
INITIAL_Y = 922

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

class DesktopCat():
    def __init__(self):
        self.workload = Workload()
        self.animation_running = True
        self.falling = False
        self.introduction_text = f"Right-click to toggle messagebox. Enter {functions.find_key('config.prefix')}h or {functions.find_key('config.prefix')}help.\nDo not move the cat fast.\nThere is a bug :("
        self.long_sleep = False
        self.messagebox_vis: bool = True
        self.book_vis: bool = True
        self.x = 1400
        self.y = 922
        self.cycle = 0
        self.current_event_cycle = choice([0, 8, 1, 9, 5, 13, 6, 7, 14, 15, 16, 17, 18])
        self.current_event_cycle_index = 0
        self.EVENTS = EVENTS
        self.event_number = self.EVENTS[self.current_event_cycle][0][0]
        self.imageGif = {}
        self.images: list = []
        self.icon = None
        self.icon_created = False
        self.window = Tk()
        self.label = Label(self.window, bd=0, bg='black')
        self.command_parser = Parser()
        self.text_content = ""
        if self.load_images():
            try:
                add_file(functions.find_key("config.paths.font"))
            except:
                functions.reset_file('config')
                add_file(functions.find_key("config.paths.font"))
            self.book = Workbook(windows=self.window)
            self.parser_actions = {
                "exit": self.exit,
                "hide_book": self.book.hide_book,
                "hide_messagebox": self.hide_messagebox,
                "check_chrome_path": self.check_chrome_path,
                "show_book": self.book.show_book,
                "switch_book_vis": self.switch_book_vis,
                "switch_messagebox_vis": self.switch_messagebox_vis,
                "sleep": self.sleep,
                "tray": self.tray,
                "save_workload": self.save_workload
            }
            self.insert_text = self.book.write_text
            self.book.write_text(self.introduction_text)
            self.messagebox = MessageBox(windows=self.window, cat=self)
            self.setup_window()
            self.start_animation()
   
    def reset_cycle(self, events = [0, 8, 1, 9, 5, 13, 6, 7, 14, 15, 16, 17, 18], event_cycle=True):
        if event_cycle:
            self.current_event_cycle = choice(events)
        self.current_event_cycle_index = 0
        self.cycle = 0
        self.event_number = self.EVENTS[self.current_event_cycle][0][self.current_event_cycle_index]

    def load_images(self):
        try:
            gifs_path = functions.find_key("config.paths.gifs")
            falling_gif = functions.find_key("config.paths.falling_gif")
        except:
            functions.reset_file('config')
            gifs_path = functions.find_key("config.paths.gifs")
            falling_gif = functions.find_key("config.paths.falling_gif")
        self.images = listdir(gifs_path)
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
                self.imageGif[image] = [PhotoImage(file=join(gifs_path, image), format=f'gif -index {i}') for i in range(defrange)]
            except TclError as e:
                print(f"Error loading {join(gifs_path, image)} : {e}")
                return False
        self.imageGif['falling'] = [PhotoImage(file=falling_gif, format=f'gif -index {i}') for i in range(4)]
        self.images.append('falling')
        return True
    
    def on_drag_start(self, event):
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
        self.messagebox.pos_cp(self.x, self.y)
        self.book.pos_book(self.x, self.y)

    def on_drag_stop(self, event):
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
        self.window.bind("<ButtonPress-3>", self.toggle_messagebox)
        self.window.bind("<B1-Motion>", self.on_drag_motion)
        self.window.bind("<ButtonRelease-1>", self.on_drag_stop)
        # self.hide_window()

    def toggle_messagebox(self, event=None):
        if self.messagebox_vis:
            self.reset_cycle(self.messagebox.open_close_messagebox(open_close=False))
            self.book.hide_book()
        else: 
            self.reset_cycle(self.messagebox.open_close_messagebox(open_close=True))
            if self.book_vis:
                self.book.show_book()
        
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
            if self.messagebox_vis:
                self.reset_cycle([22,23,24])
            else:
                self.current_event_cycle = choice([7,14,15, 0, 8, 1, 9, 5, 13, 6, 7, 14, 15, 16, 17, 18]) # [0, 8, 1, 9, 5, 13, 6, 7, 14, 15, 16, 17, 18] [7,14,15]
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
        self.messagebox.pos_cp(self.x, self.y)
        self.book.pos_book(x=self.x, y=self.y)
        self.window.after(1, self.event)

    def choose_event_change(self):
        if self.current_event_cycle_index < len(self.EVENTS[self.current_event_cycle][0]) - 1:
            self.current_event_cycle_index += 1
        elif self.long_sleep:
            next_event_cycle = 25
            self.current_event_cycle = next_event_cycle
            self.current_event_cycle_index = 0
        elif self.x < 500:
            next_event_cycle = choice([0, 8, 1, 9, 5, 13, 6, 7, 14, 15, 16, 17, 18, 10, 11])
            self.current_event_cycle = next_event_cycle
            self.current_event_cycle_index = 0            
        elif self.x > 1700:
            next_event_cycle = choice([0, 8, 1, 9, 5, 13, 6, 7, 14, 15, 16, 17, 18, 2, 3])
            self.current_event_cycle = next_event_cycle
            self.current_event_cycle_index = 0
        else:
            next_event_cycle = choice(self.EVENTS[self.current_event_cycle][1])
            while (self.x < INITIAL_X-500 or self.x > INITIAL_X+100) and next_event_cycle == 19:
                next_event_cycle = choice(self.EVENTS[self.current_event_cycle][1])                
            self.current_event_cycle = next_event_cycle
            self.current_event_cycle_index = 0
        return self.EVENTS[self.current_event_cycle][0][self.current_event_cycle_index]

    def show_window(self):
        self.window.after(0, self.window.deiconify)
        if self.icon_created:
            self.icon_created = False
            self.icon.stop()
        if self.book_vis: self.book.show_book()
        if self.messagebox_vis: self.reset_cycle(self.messagebox.open_close_messagebox(open_close=self.messagebox_vis))

    def hide_window(self, event=None):
        self.window.withdraw()
        self.reset_cycle(self.messagebox.open_close_messagebox(open_close=False))
        self.create_tray_icon()

    def exit_application(self):
        if self.icon_created:
            self.icon.stop()
        self.window.quit()

    def create_tray_icon(self):
        try:
            icon_image = Image.open(functions.find_key("config.paths.tray_ico"))
        except:
            functions.reset_file('config')
            icon_image = Image.open(functions.find_key("config.paths.tray_ico"))
        menu = (item('Show', lambda: self.show_window(), default=True), item('Exit', self.exit_application))
        self.icon = Icon("DesktopCat", icon_image, "DesktopCat", menu)
        self.icon_created = True
        self.icon.run()
        
    def parser(self, message):
        string_to_book: str = None
        workload_name: str = None
        file_error: bool = None
        args: list = []
        try: self.command_parser.parser(message=message)
        except Exception as exception:
            if type(exception) == functions.CommandException:
                print(f"\nparser from CommandException:\n")
                string_to_book = exception.string_to_book 
                args = list(exception.args)
                workload_name = exception.workload_name
                file_error = exception.file_error
                print(f"  {string_to_book=}\n  {file_error=}\n  {args=}")
            else:
                exception_name = type(exception).__name__
                exception_message = str(exception)
                exception_traceback = format_exc()
                print(f"Exception occurred: {exception_name}: {exception_message}")
                print(f"Traceback:\n{exception_traceback}")
        self.perform_parser_actions(string_to_book=string_to_book, file_error=file_error, args=args, workload_name=workload_name)
                
    def perform_parser_actions(self, string_to_book: str, args: list, file_error: bool=None, workload_name: str=None):
        if file_error:
            input : str = self.wait_input(f'{file_error} file error. Enter check or, reset or, else to continue...')
            match input.strip():
                case 'check':
                    try:
                        self.command_parser.open_workloads_file() if file_error == 'workloads' else self.command_parser.open_config_file()
                    except functions.CommandException as exception:
                        if exception.file_error:
                            self.insert_text(f'File {file_error} can not be found. Resetting...')
                            functions.reset_file(file_error)
                            self.command_parser.open_workloads_file() if file_error == 'workloads' else self.command_parser.open_config_file()
                case 'reset':
                    functions.reset_file(file_error)
                    self.insert_text(f'File {file_error} is reset.')
                case _:
                    self.insert_text('...')
        else:
            if string_to_book:
                self.insert_text(string_to_book)
            args_functions: list[function] = [self.parser_actions[command] for command in args if command in self.parser_actions]
            for args_function in args_functions:
                match args_function.__name__:
                    case 'save_workload':
                        args_function(workload_name)
                    case _:
                        args_function()

    def wait_input(self, message: str = None):
        if message: self.insert_text(message)
        return self.messagebox.return_var()

    def action_not_found(self):
        self.insert_text("I am confused?")

    def exit(self):
        if self.icon_created:
            self.icon.stop()
        self.window.quit()

    def hide_messagebox(self):
        self.messagebox.open_close_messagebox(False)

    def check_chrome_path(self):
        self.insert_text('There might be a problem with your chrome path.\'*config/*c\' to check it.')

    def switch_book_vis(self):
        if self.book_vis:
            self.book.hide_book()
        else:
            self.book.show_book()
        self.book_vis = not self.book_vis

    def switch_messagebox_vis(self):
        self.messagebox.open_close_messagebox(not self.messagebox_vis)

    def sleep(self):
        self.long_sleep = not self.long_sleep
        self.insert_text(f"Long Sleep {'On' if self.long_sleep else 'Off'}")

    def tray(self):
        self.hide_window()
        self.insert_text('Hidded')

    def save_workload(self, workload_name: str):
        vscode_urls = functions.find_key('workloads.workload_data.vscode')
        vscode_projects: dict = self.workload.find_vsc()
        for project, _ in vscode_projects.items():
            if project in vscode_urls and (self.check_proper_vscode_url(url=vscode_urls[project], project_name=project)):
                vscode_projects[project] = vscode_urls[project]
            else:
                vscode_projects[project] = self.get_project_url(project)
                functions.update_key(path=f'workloads.workload_data.vscode.{project}', value=vscode_projects[project])
        self.workload.save_workload(workload_name=workload_name, vscode=vscode_projects)
        
    def get_project_url(self, project:str) -> str | None:
        url = None
        new_url = self.wait_input(message=f'Enter path to your vscode project {project} (Leave empty to continue.):')
        if new_url == '': return None
        while url == None:
            if self.check_proper_vscode_url(url=new_url, project_name=project):
                return new_url
            url_answer = self.wait_input(message=f'Please check url for your project {project}: {new_url}\nLeave it empty to continue or enter a new url...')
            if url_answer == '': url = new_url
            else: new_url = url_answer
        return url
    
    def check_proper_vscode_url(self, url:str, project_name:str):
        return (exists(url) and 
                (url.split('/')[-1] == project_name or 
                 url.split('\\')[-1] == project_name or
                 url.split('\\\\')[-1] == project_name)
                )
    
if "__main__" == __name__:
    cat = DesktopCat()