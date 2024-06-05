import pygetwindow as gw # type: ignore
import os
import sqlite3, subprocess, webbrowser, threading, queue
import shutil
from urllib.parse import urlparse
import json
from pygetwindow import getAllTitles, getWindowsWithTitle
from pyautogui import hotkey
from pyperclip import paste

from set import *

class Workload():
    def __init__(self):
        self.chrome_profile_path = "\\AppData\\Local\\Google\\Chrome\\User Data\\"
        self.profile_name = 'Default' 
        self.chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"   
        self.vscode = {}
        self.chrome = {}
         
    def get_data(self):
        new_vscode = {}
        data = None
        with open(CONFIG_PATH, 'r') as file:  # Use raw string to handle backslashes
            data = json.load(file)
        return data
            
    def process_input(self, input_str, source_dict):
        try:
            new_dict = {}
            include = []
            exclude = []
            # Create a copy of the dictionary keys
            dict_keys = list(source_dict.keys())
            
            items = input_str.split(' ')
            for n in range(len(items)):
                if n > 0:
                    items[n] = items[n].strip()
                    if '*' not in items[n]:
                        if ('-' not in items[n] and items[n].startswith(".")):
                            number = int(items[n].replace(".",""))-1
                            order = [number,number]
                        elif '-' not in items[n]:
                            order = [1, int(items[n])]
                        else:
                            order = items[n].split('-')
                        order = self.str_int(order)
                        if order:
                            if order[0]==order[1]:
                                include.append(order[0])
                            elif order[0]>order[1]:
                                for n in range(order[1]-1, order[0]):
                                    include.append(n)
                            else:
                                for n in range(order[0]-1, order[1]):
                                    include.append(n)
                    elif items[n].startswith("*"):
                        item = items[n].replace("*","")
                        if '-' in item:
                            order = item.split('-')
                            order = self.str_int(order)
                            if order:
                                if order[0]==order[1]:
                                    exclude.append[order[0]]
                                elif order[0]>order[1]:
                                    for n in range(order[1]-1, order[0]):
                                        exclude.append(n)
                                else:
                                    for n in range(order[0]-1, order[1]):
                                        exclude.append(n)
                        else: exclude.append(int(item)-1)
            result = list(set([n for n in include if n not in exclude]))   
            
            for n in result:
                new_dict[dict_keys[n]] = source_dict[dict_keys[n]]
            return new_dict
        except: return None
    
    def str_int(self, value):
        for n in range(len(value)):
            try:
                value[n] = int(value[n])
            except:
                return False
        return value
    
    def reload_config(self, chrome_profile_path, profile_name, chrome_path):
        self.chrome_profile_path = chrome_profile_path
        self.profile_name = profile_name
        self.chrome_path = chrome_path
            
    def print_chrome(self, chrome, number = 0):
        string = '\n'
        # Determine the maximum width needed for numbering
        max_width = len(str(len(chrome)))
        i = 0
        for index, (key, value) in enumerate(chrome.items(), start=1):
            # Format the string to fit within the remaining space
            formatted_key = self.format_string(key[:30 - max_width - 2])  # Adjust for number and dot
            string += f'{str(index).rjust(max_width)}.{formatted_key} {self.get_main_link(value)}\n'
            i += 1
            if number > 0 and i >= number:
                break
        return string
   
    def get_open_windows(self):
        selected = []
        windows = gw.getAllTitles()
        for window in windows:
            if len(window)>0:
                selected.append(window.strip())
        return selected
    
    def findVSCode(self):
        vscode = {}
        selected = self.get_open_windows()
        for window in selected:
            if window.endswith('Visual Studio Code'):
                splitted = window.split(' - ')
                if len(splitted) == 3:
                    if '(Workspace)' in splitted[1]:
                        vscode[splitted[1].replace(' (Workspace)', '')] = splitted[0]
                    else: vscode[splitted[1]] = splitted[0]
                elif len(splitted) == 2:
                    if '(Workspace)' in splitted[0]:
                        vscode[splitted[0].replace(' (Workspace)', '')] = ''
                    else: vscode[splitted[0]] = ''
        return vscode
        
    def get_chrome_recently_visited_sites(self, max_sites):
        # Chrome'un veritabanı dosyasının yolu
        profile_path = os.path.expanduser('~') + f'{self.chrome_profile_path}{self.profile_name}'
        print(profile_path)
        history_db = os.path.join(profile_path, 'History')
        history_db_copy = os.path.join(profile_path, 'History_copy')
        recently_visited_sites = []
        if os.path.isfile(history_db):
            # Veritabanı dosyasının bir kopyasını oluştur
            shutil.copy2(history_db, history_db_copy)
            try:
                # Veritabanına bağlan
                connection = sqlite3.connect(history_db_copy)
                cursor = connection.cursor()
                
                # Ziyaret tarihine göre sıralanmış son ziyaretleri al
                cursor.execute('''SELECT urls.url, urls.title, visits.visit_time
                                FROM urls INNER JOIN visits ON urls.id = visits.url
                                ORDER BY visits.visit_time DESC LIMIT ?''', (max_sites,))
                rows = cursor.fetchall()
                # Ziyaret edilen siteleri listeye ekle
                for row in rows:
                    site = {
                        'url': row[0],
                        'title': row[1],
                        'visit_time': row[2] / 1000000  # Unix zaman damgasını saniyeye dönüştür
                    }
                    recently_visited_sites.append(site)  
            except sqlite3.Error as e:
                print(f"Chrome veritabanı okunurken hata oluştu: {e}")
            finally:
                if connection:
                    connection.close()
                # Kopyalanan veritabanı dosyasını sil
                os.remove(history_db_copy)
        else:
            print("Chrome veritabanı bulunamadı.")
        return recently_visited_sites        

    def findChrome(self, max_sites = 40):
        chrome = {}
        recently_visited_sites = self.get_chrome_recently_visited_sites(max_sites*2)
        # print("Son Ziyaret Edilen Siteler:")
        # for site in recently_visited_sites:
        #     print(f"Başlık: {site['title']}\n  URL: {site['url']}") # , Ziyaret Zamanı: {site['visit_time']}
        for site in recently_visited_sites:
            chrome[site['title']] = site['url']
        return chrome

    def get_main_link(self, url):
        parsed_url = urlparse(url)
        main_link = parsed_url.netloc
        return main_link
    
    def format_string(self, s):
        # Ensure the string is exactly 30 characters long
        if len(s) > 30:
            # Truncate to the first 30 characters if longer
            formatted_string = s[:30]
        else:
            # Pad with spaces if shorter
            formatted_string = s.ljust(30)
        return formatted_string
    
    def open_vscode(self, path=None):
        try:
            os.chdir(path)
            subprocess.run(["code", "."], shell=True)
        except Exception as e:
            return str(e)
        return ""
            
    def open_tab(self, query):
        webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(self.chrome_path))
        webbrowser.get('chrome').open(query)
    
    def run_workload(self, workload_name):
        ready_queue = queue.Queue()
        thread = threading.Thread(target=self.ready_workload, args=(workload_name,ready_queue))
        thread.start()
        thread.join()
        return ready_queue.get()
            
    def ready_workload(self, worklaod_name, queue):
        data = None
        vscode = None
        chrome = None
        error = ""
        with open(CONFIG_PATH, 'r') as file:
            data = json.load(file)    
        if worklaod_name in data["workloads"]:
            vscode = data["workloads"][worklaod_name]["vscode"]
            chrome = data["workloads"][worklaod_name]["chrome"]
        if vscode:
            for key in vscode:
                error = self.open_vscode(path=vscode[key][0])
        if chrome:
            for key in chrome:
                self.open_tab(chrome[key])
        queue.put(error)
        
    def choose_windows(self):
        windows = []
        for window in getAllTitles():
            if 'Google Chrome' in window:
                windows.append(window)
        return windows

    def get_open_tabs_urls(self):
        """
        Check urls we got and control if the pasted strings are acceptable. Otherwise, break the while loop to avoid an infinit loop.
        """
        
        tab_urls={}
        tabs = []
        windows = self.choose_windows()
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
                    if tab_url not in tabs: 
                        tab_urls[self.get_main_link(tab_url)] = tab_url
                        tabs.append(tab_url)
                    else: check+=1
                    if check >= 2:
                        break
                    browser.activate()
                    hotkey('ctrl','tab')
                    # sleep(.05)
        # for tab in tab_urls:
        #     print(tab)
        return tab_urls
                

# new = Workload()
# new.run_workload('exampleWorkload')
