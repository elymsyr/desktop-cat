from pygetwindow import getAllTitles, getWindowsWithTitle
from pyautogui import hotkey
from pyperclip import paste
# from time import sleep

def choose_windows():
    windows = []
    for window in getAllTitles():
        if 'Google Chrome' in window:
            windows.append(window)
    return windows

def get_open_tabs_urls():
    tab_urls=[]
    windows = choose_windows()
    for window in windows:
        print(f"\nGetting from {window}...")
        browsers = getWindowsWithTitle(window)
        for browser in browsers:
            print(browser)
            browser.activate()
            # sleep(.2)
            hotkey('ctrl','tab')
            check = 0
            while True:
                browser.activate()
                hotkey('ctrl','l')
                hotkey('ctrl','c')
                tab_url = paste()
                if tab_url not in tab_urls: tab_urls.append(tab_url)
                else: check+=1
                if check >= 2:
                    break
                browser.activate()
                hotkey('ctrl','tab')
                # sleep(.05)
    for tab in tab_urls:
        print(tab)
    return tab_urls