import tkinter as tk
from PIL import Image, ImageTk
import traceback

from set import *

class Workbook():
    def __init__(self):
        self.book = tk.Tk()
        self.book_bg_image = None
        self.text_content = ""
        self.create_book()
        self.book.mainloop()
        
    def create_book(self):
        # Create a book_canvas to display the background image
        self.book_bg_image = Image.open(BOOKS_PATH + "\\book_07.png")
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
        self.text_frame.place(relx=0.1, rely=0.1, relwidth=0.81, relheight=0.82)  # Adjust the position and size of the frame
        # Add a text box to the frame
        self.text_box = tk.Text(self.text_frame, wrap=tk.WORD, font=FONT, bg='#f2b888', fg='black')
        self.text_box.pack(fill="both", expand=True)
        self.text_box.config(border=0, highlightthickness=0, state=tk.DISABLED, padx=10, pady=10)
        self.book.geometry(f'{self.book_bg_image.width}x{self.book_bg_image.height}+' + str(1400) + '+' + str(400))
        
        # self.book.withdraw()

    def pos_book(self, x, y):
        self.book.geometry(f'{self.book_bg_image_width}x{self.book_bg_image_height}+' + str(x-295) + '+' + str(y-110)) # ?!
        
    def write_text(self, text):
        # Add text to the text box
        self.text_box.config(state=tk.NORMAL)
        self.text_box.insert(tk.END, text)
        self.text_box.see(tk.END)  # Scroll to the end
        self.text_box.config(state=tk.DISABLED)
        
if __name__ == '__main__':
    new = Workbook()