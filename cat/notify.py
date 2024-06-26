from tkinter import Toplevel, Tk, Label, PhotoImage

class Notify():
    def __init__(self, main_window: Tk) -> None:
        self.show_notify: bool = False
        self.main_window = main_window
        self.notify_window = None

    def update_geometry(self, notify_counter: int = 0):
        if self.notify_window:
            main_x = self.main_window.winfo_x()
            main_y = self.main_window.winfo_y()
            if notify_counter > 1000:
                notify_counter = 0
            if notify_counter > 500:
                main_y += 1
            elif notify_counter > 0: 
                main_y -= 1
            main_width = self.main_window.winfo_width()
            main_height = self.main_window.winfo_height()
            self.notify_window.geometry(f"{main_width}x{main_height}+{main_x}+{main_y}")
        
            if self.show_notify: 
                self.notify_window.after(1, lambda: self.update_geometry(notify_counter + 1))
    
    def start_notify(self, notification: PhotoImage):
        if not self.notify_window:
            self.notify_window = Toplevel(self.main_window)
            self.notify_window.overrideredirect(True)
            self.notify_window.wm_attributes('-transparentcolor', 'black')
            self.notify_window.wm_attributes('-topmost', 1)
            self.notify_window.wm_attributes('-toolwindow', 1)
        
        self.label = Label(self.notify_window, image=notification, bg='black')
        self.label.pack()
        self.show_notify = True
        self.update_geometry()