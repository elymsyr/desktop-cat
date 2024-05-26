import pygetwindow as gw # type: ignore
import os
import sqlite3, subprocess, webbrowser, threading
import shutil
from urllib.parse import urlparse
import json

from set import *

class Workload():
    def __init__(self):
        self.vscode = {}
        self.chrome = {}
        
    def save_workload(self, workload_name):
        new_vscode = {}
        new_chrome = {}
        code_url = ''
        data = None
        with open(r'desktop-cat\config-test.json', 'r') as file:  # Use raw string to handle backslashes
            data = json.load(file)
        vscode = self.findVSCode()
        chrome = self.findChrome()
        
        for key in list(vscode.keys()):  # Convert dict_keys to list
            if key in data['workload_data']['vscode']:
                code_url = data['workload_data']['vscode'][key]
            else:
                code_url_takin = input(f'Do you mind giving the path to your project {key}? (Leave empty to go on...)')
                while (len(code_url_takin) > 0 and (code_url_takin.split('\\'))[-1] != key) :
                    code_url_takin = input(f'Is this true? Let\'s try again: {code_url_takin} (Leaving it empty is an option but...)')
                code_url = code_url_takin
                if len(code_url) > 0:
                    data['workload_data']['vscode'][key] = code_url
            new_vscode[key] = [code_url, vscode[key]]
        self.print_chrome(chrome, 10)
        input_numbers = input('Specify the numbers (Example: \'1-5 *4 .10\') :\n  .n to add from 1 to n\n  n-m to add from n to m\n  n to add n\n  *n to exclude n\n  *n-m to exclude from n to m\nInput Waiting: ')
        selected = self.process_input(input_numbers, chrome)
        while not selected:
            input_numbers = input('Please specify the numbers correctly:\n  .n to add from 1 to n\n  n-m to add from n to m\n  n to add n\n  *n to exclude n\n *n-m to exclude from n to m\nInput Waiting: ')
            selected = self.process_input(input_numbers, chrome)
        self.print_chrome(selected)                                
        new_chrome = selected
        data['workloads'][workload_name] = {"vscode": new_vscode,"chrome": new_chrome}
            
        with open('desktop-cat\config-test.json', 'w') as file:
            json.dump(data, file, indent=4)
            
    def process_input(self, input_str, source_dict):
        try:
            new_dict = {}
            include = []
            exclude = []
            # Create a copy of the dictionary keys
            dict_keys = list(source_dict.keys())
            
            items = input_str.split(' ')
            for n in range(len(items)):
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
            
    def print_chrome(self, chrome, number = 0):
        # Determine the maximum width needed for numbering
        max_width = len(str(len(chrome)))
        i = 0
        for index, (key, value) in enumerate(chrome.items(), start=1):
            # Format the string to fit within the remaining space
            formatted_key = self.format_string(key[:30 - max_width - 2])  # Adjust for number and dot
            print(f'{str(index).rjust(max_width)}. {formatted_key} : {self.get_main_link(value)}')
            i += 1
            if number > 0 and i >= number:
                break
   
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
        
    def get_chrome_recently_visited_sites(self, max_sites, profile_name='Default'):
        # Chrome'un veritabanı dosyasının yolu
        profile_path = os.path.expanduser('~') + f'\\AppData\\Local\\Google\\Chrome\\User Data\\{profile_name}'
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
        os.chdir(path)
        subprocess.run(["code", "."], shell=True)
            
    def open_tab(self, query):
        webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(CHROME_PATH))
        webbrowser.get('chrome').open(query)
        
    def open_chrome(self, queries):
        threads = []
        for query in queries:
            thread = threading.Thread(target=self.open_tab, args=(query,))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
    
    def run_workload(self, workload_name):
        thread = threading.Thread(target=self.set_workload, args=(workload_name,))
        thread.start()
        thread.join()
            
    def set_workload(self, worklaod_name):
            data = None
            vscode = None
            chrome = None
            chrome_tabs = []
            with open(r'desktop-cat\config-test.json', 'r') as file:
                data = json.load(file)    
            if worklaod_name in data["workloads"]:
                vscode = data["workloads"][worklaod_name]["vscode"]
                chrome = data["workloads"][worklaod_name]["chrome"]
            for key in vscode:
                self.open_vscode(path=vscode[key][0])
            for key in chrome:
                chrome_tabs.append(chrome[key])
            self.open_chrome(chrome_tabs)
                

new = Workload()
new.run_workload('exampleWorkload')
