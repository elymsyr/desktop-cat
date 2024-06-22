from os import chdir
from webbrowser import register, BackgroundBrowser, get
from subprocess import run
from threading import Thread
from json import load
from pygetwindow import getAllTitles, getWindowsWithTitle
from pyautogui import hotkey, getActiveWindowTitle
from pyperclip import paste
from settings import functions

class Workload():
    def __init__(self):
        self.chrome_path: str = functions.find_key(path='config.paths.chrome')
    
    def refresh_data(self) -> None:
        """Refreshes values from config.json data.
        """
        self.chrome_path: str = functions.find_key(path='config.paths.chrome')
    
    def get_open_windows(self, specify_name: str = None) -> list:
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
        selected = self.get_open_windows(specify_name='Visual Studio Code')
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

    def current_sites(self) -> dict[str, str]:
        """Controls Chrome for a short time. Gets open tab titles and urls by switching between tabs.

        Returns:
            dict[str, str]: A dictionary of tab titles and urls.  
        """
        tab_urls={}
        tabs = []
        windows = self.get_open_windows(specify_name='Google Chrome')
        for window in windows:
            browsers = getWindowsWithTitle(window)
            for browser in browsers:
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
                    else: check+=1
                    if check >= 2:
                        break
                    browser.activate()
                    hotkey('ctrl','tab')
        return tab_urls
    
    def open_vscode(self, path: str) -> None:
        """Opens a folder on Vscode.

        Args:
            path (str): Folder path.

        Raises:
            NotImplementedError: _description_
        """
        chdir(path)
        run(["code", "."], shell=True)
    
    def open_tab(self, query_list: list) -> None:
        """Opens a chrome tab

        Args:
            query_list (_type_): Url.
        """
        for query in query_list:
            register('chrome', None, BackgroundBrowser(self.chrome_path))
            get('chrome').open(query)
    
    def run_workload(self, workload_name: str) -> None:
        """Runs the workload with the name workload_name in a thread.

        Args:
            workload_name (str)
        """
        thread = Thread(target=self.ready_workload, args=(workload_name,))
        thread.start()
        thread.join()

    def ready_workload(self, workload_name: str) -> None:
        """Function that runs a workload to be used in the function run_worklaod.

        Args:
            workload_name (str)
            queue (queue.Queue): Queue that catches errors.
        """
        data: dict
        vscode: dict
        chrome: dict
        error: str
        urls: list[str] = []
        threads: list[Thread] = []
        with open('zconfig.json', 'r') as file:
            data = load(file)    
        if workload_name in data["workloads"]:
            vscode = data["workloads"][workload_name]["vscode"]
            chrome = data["workloads"][workload_name]["chrome"]
        if chrome:
            for _, url in chrome.items():
                urls.append(url)
            threads.append(Thread(target=self.open_tab, args=(urls,)))
        if vscode:
            for project in vscode:
                threads.append(Thread(target=self.open_vscode, args=(vscode[project],)))
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
        data = functions.get_data()
        data['workloads'][workload_name] = workload
        functions.set_data(data)

    def help(self, list_functions: list = []) -> dict:
        """Returns a dictionary of lines about how to use workload class functions.

        Returns:
            dict: Function name, Docstring
        """
        functions = ['run_workload', 'refresh_data'] + list_functions
        methods = {k: v for k, v in Workload.__dict__.items() if callable(v)}
        {key: value.__doc__ for key, value in methods.items() if key in functions}
        return {key: value.__doc__ for key, value in methods.items() if key in functions}