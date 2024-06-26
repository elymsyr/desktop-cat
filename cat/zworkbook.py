import tkinter as tk
from PIL import Image, ImageTk
from traceback import extract_tb
from settings import functions

class Workbook():
    def __init__(self, windows=tk.Tk, book_name: str = 'book_07'):
        self.book = tk.Toplevel(windows)
        self.book_name: str = book_name
        self.book_bg_image: Image = None
        self.create_book()
        
    def create_bg(self) -> None:
        """Creates a book_canvas to display the background image.
        """
        self.book_bg_image = Image.open(functions.find_key(path='config.paths.books_bg') + f"\\{self.book_name}.png")
        self.book_canvas = tk.Canvas(self.book, width=self.book_bg_image.width, height=self.book_bg_image.height, highlightthickness=0, bg='black')
        self.book_canvas.pack(fill="both", expand=True)
        self.book_bg_photo = ImageTk.PhotoImage(self.book_bg_image)
        
    def set_book(self) -> None:
        """Adds a textbox and sets the geometry.
        """
        font: str = functions.find_key(path='config.fonts.current_font_name')
        size: int = functions.find_key(path='config.fonts.default_font_size')
        self.text_box = tk.Text(self.text_frame, wrap=tk.WORD, font=(font, size), bg='#f2b888', fg='#100000')
        self.text_box.pack(fill="both", expand=True)
        self.text_box.config(border=0, highlightthickness=0, state=tk.DISABLED, padx=10, pady=10)
        self.book.geometry(f'{self.book_bg_image.width}x{self.book_bg_image.height}+' + str(1400) + '+' + str(400))        
        
    def create_book(self) -> None:
        """Creates and sets book.
        """
        self.create_bg()
        self.book.config(highlightbackground='black', )
        self.book.overrideredirect(True)
        self.book.wm_attributes('-transparentcolor', 'black')
        self.book.wm_attributes('-topmost', 1)
        try:
            self.book_canvas.create_image(0, 0, anchor="nw", image=self.book_bg_photo)
        except Exception as e:
            tb_info = extract_tb(e.__traceback__)
            row_number = tb_info[-1].lineno
            print(f"Exception at {row_number}: {e}")
        self.text_frame = tk.Frame(self.book_canvas, bg='black')
        self.text_frame.place(relx=0.1, rely=0.1, relwidth=0.81, relheight=0.82)  # Adjust the position and size of the frame
        self.set_book()

    def pos_book(self, x: int, y: int) -> None:
        """Repositions book to x and y coordinates.

        Args:
            x (int)
            y (int)
        """
        self.book.geometry(f'{self.book_bg_image.width}x{self.book_bg_image.height}+' + str(x-275) + '+' + str(y-505)) # ?!
        
    def write_text(self, text: str) -> None:
        """Add text to book.

        Args:
            text (str): Text to be added.
        """
        def update_text_box():
            self.text_box.config(state=tk.NORMAL)
            self.text_box.insert(tk.END, f"\n\n{text}")
            self.text_box.see(tk.END)
            self.text_box.config(state=tk.DISABLED)
        
        self.book.after(0, update_text_box)

    def hide_book(self) -> None:
        """Hides book with withdraw().
        """
        self.book.withdraw()

    def show_book(self) -> None:
        """Make book visible with deiconify().
        """
        self.book.deiconify()
