from traceback import extract_tb
import tkinter as tk
from threading import Thread
from PIL import Image, ImageTk

from settings import functions

class MessageBox():
    def __init__(self, windows=tk.Tk, cat=None):
        """Message Box window. Parser and command used here.
        """
        self.command_prompt: tk.Toplevel = tk.Toplevel(windows)
        self.command_bg_image_height: int
        self.cat = cat
        self.command_bg_image_width: int
        self.var: tk.StringVar = tk.StringVar()
        self.command_bg_photo: ImageTk.PhotoImage = None
        self.white: bool = True
        self.create_cp()
        
    def open_close_messagebox(self, open_close: bool = None, esc=False, event=None) -> list:
        """Opens or hides message box. Returns a list of possible next animation cycles.

        Args:
            open_close (bool): Open -> true / Close(Hide) -> false

        Returns:
            list: List of possible next animation cycles.
        """
        if open_close:
            print('open cp')
            self.command_prompt.deiconify()
            if not self.cat.long_sleep:
                self.cat.reset_cycle([22,23,24])
            self.cat.messagebox_vis = True
            self.command_entry.focus_set()
            return [22,23,24]
        else:
            print('close cp')
            self.command_prompt.withdraw()
            if not self.cat.long_sleep:
                self.cat.reset_cycle([0, 8, 1, 9, 5, 13, 7, 15, 16, 17, 18])
            self.cat.messagebox_vis = False
            self.cat.book.hide_book()
            if esc:
                self.cat.book_vis = False
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
        
        self.command_prompt.bind('<Escape>', lambda event: self.open_close_messagebox(open_close=False, esc=True))
        # FONT = ("Minecraftia", 11)
        entry_width = 33  # Set the width of the command_entry widget
        entry_height = 1  # Set the height of the command_entry widget to 1-2 rows
        self.command_entry = tk.Text(self.command_prompt, bg='#fff7f5', fg='#100000', font=(functions.find_key("config.fonts.current_font_name"),functions.find_key("config.fonts.default_font_size")) , borderwidth=0, width=entry_width, height=entry_height, cursor='arrow')
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
            message: list = message[1:].split()
            message.append("$endOfMessage")
            self.cat.parser(message)
            self.white = True
        elif not self.white:
            self.cat.insert_text("Parser is already working.")
        else:
            self.cat.insert_text(f"uhm what... {message}...")
        return message
    
    def return_var(self):
        self.open_close_messagebox(True)
        self.cat.window.wait_variable(self.var)
        input = self.var.get()
        self.var.set("")  # Reset self.var to an empty string
        return input      