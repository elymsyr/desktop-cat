from os import listdir
from os.path import join
from pyglet.font import add_file
from random import choice
from tkinter import Tk, Label, StringVar, PhotoImage, TclError
from PIL import Image
from traceback import format_exc
from pystray import MenuItem as item, Icon
from settings import functions
from zworkbook import Workbook
from zmessagebox import MessageBox
from zworkload import Workload
from zparser import Parser

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
        self.long_sleep = False
        self.messagebox_vis: bool = False
        self.book_vis: bool = False
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
        self.var = StringVar()
        self.command_parser = Parser()
        self.text_content = ""
        if self.load_images() :
            add_file(functions.find_key("config.paths.font"))
            self.book = Workbook(windows=self.window)
            self.messagebox = MessageBox(windows=self.window, cat=self)
            # self.write_text("\nDo not move the cat fast.\nThere is a bug :(\nRight click to cat!")
            self.setup_window()
            self.start_animation()
   
    def reset_cycle(self, events = [0, 8, 1, 9, 5, 13, 6, 7, 14, 15, 16, 17, 18], event_cycle=True):
        if event_cycle:
            self.current_event_cycle = choice(events)
        self.current_event_cycle_index = 0
        self.cycle = 0
        self.event_number = self.EVENTS[self.current_event_cycle][0][self.current_event_cycle_index]

    def load_images(self):
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
        self.messagebox.pos_cp(self.x, self.y)
        self.book.pos_book(self.x, self.y)       

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
        self.window.bind("<ButtonPress-3>", self.messagebox_appear)
        self.window.bind("<B1-Motion>", self.on_drag_motion)
        self.window.bind("<ButtonRelease-1>", self.on_drag_stop)
        self.hide_window()

    def messagebox_appear(self, event=None):
        if self.messagebox_vis:
            self.reset_cycle(self.messagebox.open_close_cp(open_close=False))
            self.book.hide_book()
        else: 
            self.reset_cycle(self.messagebox.open_close_cp(open_close=True))
            if self.book_vis:
                self.book.show_book()
        self.messagebox_vis = not self.messagebox_vis
        
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
        print('show_window')
        self.window.after(0, self.window.deiconify)
        if self.icon_created:
            self.icon_created = False
            self.icon.stop()
        if self.messagebox_vis: self.reset_cycle(self.messagebox.open_close_cp(open_close=self.messagebox_vis))

    def hide_window(self, event=None):
        print('hide_window')
        self.window.withdraw()
        self.book.hide_book()
        self.book_vis = False
        self.reset_cycle(self.messagebox.open_close_cp(open_close=False))
        self.create_tray_icon()

    def exit_application(self):
        print('exit_application')
        if self.icon_created:
            self.icon.stop()
        self.window.quit()

    def create_tray_icon(self):
        print('create_tray_icon')
        icon_image = Image.open(functions.find_key("config.paths.tray_ico"))
        menu = (item('Show', lambda: self.show_window(), default=True), item('Exit', self.exit_application))
        self.icon = Icon("DesktopCat", icon_image, "DesktopCat", menu)
        self.icon_created = True
        self.icon.run()
        
    def parser(self, message):
        try: self.command_parser.parser(message=message)
        except functions.CommandException as command_exception:
            print(f"parser from CommandException:")
            attributes = vars(command_exception)
            for attribute, value in attributes.items():
                print(f"    {attribute}: {value}")            
        except Exception as exception:
            exception_name = type(exception).__name__
            exception_message = str(exception)
            exception_traceback = format_exc()
            print(f"Exception occurred: {exception_name}: {exception_message}")
            print(f"Traceback:\n{exception_traceback}")
            
        
cat = DesktopCat()