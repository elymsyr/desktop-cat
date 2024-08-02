from threading import Thread
from settings import functions
from os.path import exists

class ParserFunctions():
    def __init__(self, cat) -> None:
        self.cat = cat
        
    def wait_input(self, message: str = None):
        if message: self.cat.insert_text(message)
        return self.cat.messagebox.return_var()

    def action_not_found(self):
        self.cat.insert_text("I am confused?")

    def exit(self):
        if self.cat.icon_created:
            self.cat.icon.stop()
        self.cat.window.quit()

    def hide_messagebox(self):
        self.cat.messagebox.open_close_messagebox(False)

    def check_chrome_path(self):
        self.cat.insert_text('There might be a problem with your chrome path.\'*config/*c\' to check it.')

    def switch_book_vis(self):
        if self.cat.book_vis:
            self.cat.book.hide_book()
        else:
            self.cat.book.show_book()
        self.cat.book_vis = not self.cat.book_vis

    def switch_messagebox_vis(self):
        self.cat.messagebox.open_close_messagebox(not self.cat.messagebox_vis)

    def sleep(self):
        self.cat.long_sleep = not self.cat.long_sleep
        self.cat.insert_text(f"Long Sleep {'On' if self.cat.long_sleep else 'Off'}")

    def tray(self):
        self.cat.hide_window()
        self.cat.insert_text('Hidded')

    def save_workload(self, workload_name: str):
        vscode_urls = functions.find_key('workloads.workload_data.vscode')
        vscode_projects: dict = self.cat.workload.find_vsc()
        for project, _ in vscode_projects.items():
            if project in vscode_urls and (self.check_proper_vscode_url(url=vscode_urls[project], project_name=project)):
                vscode_projects[project] = vscode_urls[project]
            else:
                vscode_projects[project] = self.cat.get_project_url(project)
                functions.update_key(path=f'workloads.workload_data.vscode.{project}', value=vscode_projects[project])
        self.cat.workload.save_workload(workload_name=workload_name, vscode=vscode_projects)
        
    def get_project_url(self, project:str) -> str | None:
        url = None
        new_url = self.wait_input(message=f'Enter path to your vscode project {project} (Leave empty to continue.):')
        if new_url == '': return None
        while url == None:
            if self.check_proper_vscode_url(url=new_url, project_name=project):
                return new_url
            url_answer = self.wait_input(message=f'Please check url for your project {project}: {new_url}\nLeave it empty to continue or enter a new url...')
            if url_answer == '': url = new_url
            else: new_url = url_answer
        return url
    
    def check_proper_vscode_url(self, url:str, project_name:str):
        return (exists(url) and 
                (url.split('/')[-1] == project_name or 
                 url.split('\\')[-1] == project_name or
                 url.split('\\\\')[-1] == project_name)
                )
        
    def notify(self, notification_name: str):
        if not self.cat.dnd:
            notification = self.cat.notifications[notification_name]
            if self.cat.notification_thread and self.cat.notification_thread.is_alive():
                return
            self.cat.notification_thread = Thread(target=self.cat.notification.start_notify, args=(notification,))
            self.cat.notification_thread.setDaemon(daemonic=True)
            self.cat.notification_thread.start()  
        
    def silent_notification(self):
        self.cat.notification.notify_window.destroy()
        self.cat.notification_thread.join()
        
    def dnd_mode(self):
        self.cat.dnd = not self.cat.dnd
        if self.cat.dnd and self.cat.notification.notify_window:
            self.silent_notification()
        self.cat.insert_text(f"DND Mode {'On' if self.cat.dnd else 'Off'}.")
        
    def toggle_messagebox(self, event=None):
        if self.cat.messagebox_vis:
            self.cat.messagebox.open_close_messagebox(open_close=False)
            self.cat.book.hide_book()
        else: 
            self.cat.messagebox.open_close_messagebox(open_close=True)
            if self.cat.book_vis:
                self.cat.book.show_book()