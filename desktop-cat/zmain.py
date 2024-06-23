from zanimations import CatAnimations
from settings import functions
from zworkbook import Workbook
from zmessagebox import MessageBox
from zworkload import Workload
from zparser import Parser
import multiprocessing, threading
from tkinter import Tk
from time import sleep

class Cat():
    def __init__(self) -> None:
        self.window = Tk()
        self.book = Workbook(windows=self.window)
        self.messageBox = MessageBox(windows=self.window, book=self.book)


app = Cat()