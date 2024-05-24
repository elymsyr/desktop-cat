import pygetwindow as gw

class Workload():
    def __init__(self):
        self.selected = []
        self.vscode = {}
        
        
    def get_open_windows(self):
        self.selected = []
        windows = gw.getAllTitles()
        for window in windows:
            if len(window)>0:
                self.selected.append(window.strip())
        for window in self.selected:
            print(window)
        return windows
    
    def findVSCode(self):
        for window in self.selected:
            if window.endswith('Visual Studio Code'):
                splitted = window.split(' - ')
                if len(splitted) == 3:
                    if '(Workspace)' in splitted[1]:
                        self.vscode[splitted[1].replace(' (Workspace)', '')] = splitted[0]
                    else: self.vscode[splitted[1]] = splitted[0]
                elif len(splitted) == 2:
                    if '(Workspace)' in splitted[0]:
                        self.vscode[splitted[0].replace(' (Workspace)', '')] = ''
                    else: self.vscode[splitted[0]] = ''
        print(self.vscode)

workload = Workload()
workload.get_open_windows()
workload.findVSCode()