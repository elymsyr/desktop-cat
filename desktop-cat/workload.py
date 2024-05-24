import pygetwindow as gw # type: ignore
import os
import sqlite3
import shutil
from urllib.parse import urlparse

class Workload():
    def __init__(self):
        self.vscode = {}
        self.chrome = {}
        
    def get_open_windows(self):
        selected = []
        windows = gw.getAllTitles()
        for window in windows:
            if len(window)>0:
                selected.append(window.strip())
        return selected
    
    def findVSCode(self):
        selected = self.get_open_windows()
        for window in selected:
            if window.endswith('Visual Studio Code'):
                splitted = window.split(' - ')
                if len(splitted) == 3:
                    if '(Workspace)' in splitted[1]:
                        self.vscode[splitted[1].replace(' (Workspace)', '')] = [splitted[0], ""]
                    else: self.vscode[splitted[1]] = [splitted[0], ""]
                elif len(splitted) == 2:
                    if '(Workspace)' in splitted[0]:
                        self.vscode[splitted[0].replace(' (Workspace)', '')] = ['', ""]
                    else: self.vscode[splitted[0]] = ['', ""]
        
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

    def findChrome(self, max_sites = 20):
        recently_visited_sites = self.get_chrome_recently_visited_sites(max_sites*2)
        # print("Son Ziyaret Edilen Siteler:")
        # for site in recently_visited_sites:
        #     print(f"Başlık: {site['title']}\n  URL: {site['url']}") # , Ziyaret Zamanı: {site['visit_time']}
        for site in recently_visited_sites:
            self.chrome[site['title']] = site['url']

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

workload = Workload()
workload.findVSCode()
workload.findChrome()

print('Open VSCode:')
for key, value in workload.vscode.items():
    print(f'{key} : {value}')

print('\nLast Chrome Tabs:')
for key, value in workload.chrome.items():
    print(f'{workload.format_string(key)} : {workload.get_main_link(value)}')
