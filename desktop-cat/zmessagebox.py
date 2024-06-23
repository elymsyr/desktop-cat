from traceback import extract_tb
import tkinter as tk
from threading import Thread
from PIL import Image, ImageTk
from zanimations import CatAnimations

from settings import functions

class MessageBox():
    def __init__(self, windows=tk.Tk, book=None):
        """Message Box window. Parser and command used here.
        """
        self.command_prompt: tk.Toplevel = tk.Toplevel(windows)
        self.cat = CatAnimations(window=windows, book=book, messagebox=self)
        self.command_bg_image_height: int
        self.command_bg_image_width: int
        self.var: tk.StringVar = tk.StringVar()
        self.command_bg_photo: ImageTk.PhotoImage = None
        self.white: bool = True
        self.create_cp()
        
    def open_close_cp(self, open_close: bool = None, event=None) -> list:
        """Opens or hides message box. Returns a list of possible next animation cycles.

        Args:
            open_close (bool): Open -> true / Close(Hide) -> false

        Returns:
            list: List of possible next animation cycles.
        """
        # if not self.command_created and not self.icon_created:
        if open_close:
            print('open cp')
            self.command_prompt.deiconify()
            # self.pos_cp()
            self.command_entry.focus_set()
            # if not self.long_sleep:
            #     self.reset_cycle([22,23,24])
            return [22,23,24]
        else:
            print('close cp')
            # self.open_close_book(False)
            self.command_prompt.withdraw()
            # if not self.long_sleep:
            #     self.reset_cycle([0, 8, 1, 9, 5, 13, 7, 15, 16, 17, 18])
            return [0, 8, 1, 9, 5, 13, 7, 15, 16, 17, 18]

    def create_cp(self) -> None:
        """Creates message box tkinter window.
        """
        command_bg_image: Image = Image.open(functions.find_key("config.paths.command_bg"))
        self.command_bg_image_height: int = command_bg_image.height
        self.command_bg_image_width: int = command_bg_image.width
        # Create a command_canvas to display the background image
        # 360 = self.command_bg_image.width // 180 = self.command_bg_image.height
        self.command_canvas = tk.Canvas(self.command_prompt, width=self.command_bg_image_width, height=self.command_bg_image_height, highlightthickness=0, bg='black')
        self.command_canvas.pack(fill="both", expand=True)
        
        self.command_prompt.config(highlightbackground='black')
        
        self.command_prompt.overrideredirect(True)
        self.command_prompt.wm_attributes('-transparentcolor', 'black')
        self.command_prompt.wm_attributes('-topmost', 1)
        
        self.command_prompt.bind('<Escape>', lambda event: self.open_close_cp(open_close=False))
        # FONT = ("Minecraftia", 11)
        entry_width = 33  # Set the width of the command_entry widget
        entry_height = 1  # Set the height of the command_entry widget to 1-2 rows
        self.command_entry = tk.Text(self.command_prompt, bg='#fff7f5', fg='#111100', font=(functions.find_key("config.fonts.current_font_name"),functions.find_key("config.fonts.default_font_size")) , borderwidth=0, width=entry_width, height=entry_height, cursor='arrow')
        self.command_entry.bind("<Return>", self.on_enter_pressed)
        # Center the command_entry widget with padding
        self.command_entry.place(relx=0.5, rely=0.5, anchor="center")
        self.command_entry.config(padx=2, pady=18)
        
        self.command_bg_photo = ImageTk.PhotoImage(command_bg_image)
        try:
            self.command_canvas.create_image(0, 0, anchor="nw", image=self.command_bg_photo)
        except Exception as e:
            tb_info = extract_tb(e.__traceback__)
            row_number = tb_info[-1].lineno
            print(f"Exception at {row_number}: {e}")
        self.open_close_cp(open_close=False)
    
    def pos_cp(self, x: float, y: float) -> None:
        """Respositions message box.

        Args:
            x (float): X position of the cat.
            y (float): Y position of the cat.
        """
        self.command_prompt.geometry(f'{self.command_bg_image_width}x{self.command_bg_image_height}+' + str(x-295) + '+' + str(y-110))  

    def on_enter_pressed(self, event) -> str:
        """Returns the text taken from message box when enter is pressed.
        """
        message: str = self.command_entry.get("1.0", "end-1c")  # Get all text from the widget
        self.var.set(message)
        self.command_entry.delete("1.0", "end")  # Delete all text from the widget
        message = message.strip()
        if message.startswith(functions.find_key("config.prefix")) and self.white:
            self.white = False
            parser_thread = Thread(target=self.parser, args=(message[1:].split().append("$endOfMessage"),))
            parser_thread.start()
            parser_thread.join()
            self.white = True
        elif not self.white:
            # raise Exception("Parser is already working.")
            print("Parser is already working.")
        else:
            print(message)
        return message
    
    def parser(self, message: list[str]):
        """Takes the text from the message box and performs certain functions.

        Args:
            message (list[str])
        """
        return