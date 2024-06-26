from os import chdir
from webbrowser import register, BackgroundBrowser, get, _tryorder
from subprocess import run
from threading import Thread
from pygetwindow import getAllTitles, getWindowsWithTitle, Win32Window
from pyautogui import hotkey, getActiveWindowTitle
from pyperclip import paste
from os.path import exists
from settings import functions

class Workload():
    def __init__(self):
        pass

    def get_open_windows(self, specify_name: str = None) -> list[str]:
        """Finds currently open windows.
        
        Args:
            specify_name (str, optional): Choose the windows including specify_name.

        Returns:
            list: Titles of open windows.
        """
        selected = []
        windows = getAllTitles()
        for window in windows:
            if len(window)>0 and ((specify_name is not None and specify_name in window) or specify_name is None):
                selected.append(window.strip())
        return selected

    def find_vsc(self) -> dict[str, str]:
        """Finds open folders/workspaces/files on VSCode. 

        Returns:
            list: A list of open folders/workspaces/files on VSCode as names/titles.
        """
        vscode = {}
        selected: list[str] = self.get_open_windows(specify_name='Visual Studio Code')
        for window in selected:
            if window.endswith('Visual Studio Code'):
                splitted = window.split(' - ')
                if len(splitted) == 3:
                    if '(Workspace)' in splitted[1]:
                        vscode[splitted[1].replace(' (Workspace)', '')] = ''
                    else: vscode[splitted[1]] = ''
                elif len(splitted) == 2:
                    if '(Workspace)' in splitted[0]:
                        vscode[splitted[0].replace(' (Workspace)', '')] = ''
                    else: vscode[splitted[0]] = ''
        return vscode

    def find_chrome(self) -> dict[str, str]:
        """Finds and prepares a dictionary of chrome history. 

        Args:
            max_sites (int, optional): Defaults to 40.

        Returns:
            dict[str, str]: A dictionary of links. [site name, url]
        """
        chrome = {}
        visited_sites = self.current_sites()
        for title, url in visited_sites.items():
            chrome[title.replace(' - Google Chrome', '')] = url
        return chrome
        
    def activate_chrome_window(self):
        try:
            windows: list[Win32Window] = getWindowsWithTitle('Chrome')
            if windows:
                chrome_window = windows[0]
                if chrome_window.isMinimized:
                    chrome_window.restore()
                chrome_window.activate()
            return True
        except:
            return False   

    def current_sites(self) -> dict[str, str]:
        """Controls Chrome for a short time. Gets open tab titles and urls by switching between tabs.

        Returns:
            dict[str, str]: A dictionary of tab titles and urls.  
        """
        tab_urls={}
        tabs = []
        windows = self.get_open_windows(specify_name='Google Chrome')
        for window in windows:
            browsers:list[Win32Window] = getWindowsWithTitle(window)
            for browser in browsers:
                self.activate_chrome_window()
                browser.activate()
                hotkey('ctrl','tab')
                check = 0
                while True:
                    browser.activate()
                    hotkey('ctrl','l')
                    hotkey('ctrl','c')
                    tab_url = paste()
                    if tab_url not in tabs: 
                        tab_urls[getActiveWindowTitle()] = tab_url
                        tabs.append(tab_url)
                    elif len(tab_url) > 35: check+=2
                    else: check += 1
                    if check > 4:
                        break
                    browser.activate()
                    hotkey('ctrl','tab')
        return tab_urls
    
    def open_vscode(self, path: str, workload_name: str) -> None:
        """Opens a folder on Vscode.

        Args:
            path (str): Folder path.

        Raises:
            NotImplementedError: _description_
        """
        try:
            chdir(path)
            run(["code", "."], shell=True)
        except:
            raise functions.CommandException('vscode_path_error', workload_name=workload_name)    

    def open_tab(self, query_list: list) -> None:
        """Opens a chrome tab

        Args:
            query_list (_type_): Url.
        """
        chrome_path = functions.find_key("config.paths.chrome")
        register('chrome', None, BackgroundBrowser(chrome_path))
        if exists(chrome_path):
            for query in query_list:        
                get('chrome').open(query)
        else:
            for query in query_list:
                get(_tryorder[0]).open(query)
            raise functions.CommandException("check_chrome_path", "show_book")
            
    
    def run_workload(self, workload_name: str) -> None:
        """Runs the workload with the name workload_name in a thread.

        Args:
            workload_name (str)
        """
        thread = Thread(target=self.ready_workload, args=(workload_name,))
        thread.start()
        thread.join()

    def ready_workload(self, workload_name: str) -> None:
        """Function that runs a workload to be used in the function run_workload.

        Args:
            workload_name (str)
            queue (queue.Queue): Queue that catches errors.
        """
        data: dict = functions.get_data('workloads')
        if not data:
            raise functions.CommandException(file_error = 'workloads')
        data = data['workloads']
        vscode: dict = None
        chrome: dict = None
        urls: list[str] = []
        threads: list[Thread] = []  
        if workload_name in data["workloads"]:
            vscode = data["workloads"][workload_name]["vscode"]
            chrome = data["workloads"][workload_name]["chrome"]
        if chrome:
            for _, url in chrome.items():
                urls.append(url)
            threads.append(Thread(target=self.open_tab, args=(urls,)))
        if vscode:
            for project in vscode:
                threads.append(Thread(target=self.open_vscode, args=(vscode[project],workload_name,)))
        for work in threads:
            work.start()
        for work in threads:
            work.join()

    def save_workload(self, workload_name: str, vscode: dict) -> None:
        """Saves workload.

        Args:
            workload_name (str): Workload name to be saved.
            vscode (dict): Vscode dictionary to be saved.
        """
        chrome: dict = self.find_chrome()
        workload = {'vscode': vscode, 'chrome': chrome}
        data = functions.get_data('workloads')
        if not data:
            raise functions.CommandException(file_error = 'workloads')
        data['workloads']['workloads'][workload_name] = workload
        functions.set_data(data, file='workloads')

    def help(self, list_functions: list = []) -> dict:
        """Returns a dictionary of lines about how to use workload class functions.

        Returns:
            dict: Function name, Docstring
        """
        functions = ['run_workload'] + list_functions
        methods = {k: v for k, v in Workload.__dict__.items() if callable(v)}
        {key: value.__doc__ for key, value in methods.items() if key in functions}
        return {key: value.__doc__ for key, value in methods.items() if key in functions}