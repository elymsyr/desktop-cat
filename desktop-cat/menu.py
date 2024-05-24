import tkinter as tk
from PIL import Image, ImageTk
import pyglet

class PixelArtMessageBoxApp:
    def __init__(self, command_bg_image):
        self.command_bg_photo = None
        self.command_prompt = None
        self.command_canvas = None
        self.command_entry = None
        self.command_bg_image = command_bg_image # Image.open(self.menu_bg_image_path).convert("RGBA")
        # self.font_path = "C:\\Users\\orhun\\OneDrive\\Belgeler\\GitHub\\desktop-cat\\desktop-cat\\Cats\\greyCat-160x160-10\\Minecraftia-Regular.ttf"
        self.font_path = "C:\\Users\\orhun\\OneDrive\\Belgeler\\GitHub\\desktop-cat\\desktop-cat\\Cats\\greyCat-160x160-10\\pixelmix.ttf"
        pyglet.font.add_file(self.font_path)
        

    def draw_background_image(self):
        self.command_bg_photo = ImageTk.PhotoImage(self.command_bg_image)
        try:
            self.command_canvas.create_image(0, 0, anchor="nw", image=self.command_bg_photo)
        except Exception as e:
            print(e)

    def on_enter_pressed(self, event):
        message = self.command_entry.get("1.0", "end-1c")  # Get all text from the widget
        self.command_entry.delete("1.0", "end")  # Delete all text from the widget
        print(message)
        return message
    
    def pos_window(self, x, y):
        self.command_prompt.geometry(f'{self.command_bg_image.width}x{self.command_bg_image.height}+' + str(x) + '+' + str(y))

    def create_windows(self):
        self.command_prompt = tk.Toplevel()
        # Create a command_canvas to display the background image
        self.command_canvas = tk.Canvas(self.command_prompt, width=self.command_bg_image.width, height=self.command_bg_image.height, highlightthickness=0, bg='black')
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
        self.command_entry = tk.Text(self.command_prompt, bg='#fff7f5', fg='#111111', font=entry_font, borderwidth=0, width=entry_width, height=entry_height)
        self.command_entry.bind("<Return>", self.on_enter_pressed)
        # Center the command_entry widget with padding
        self.command_entry.place(relx=0.5, rely=0.5, anchor="center")
        self.command_entry.config(padx=2, pady=12)

    def init(self, x, y):
        self.create_windows()
        self.draw_background_image()
        self.pos_window(x, y)
        self.command_prompt.mainloop()
        
    def deleteMessageBox(self):
        self.command_prompt.destroy()