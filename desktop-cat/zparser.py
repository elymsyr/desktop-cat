import webbrowser
from settings import functions
from zworkload import Workload
from json import load
from subprocess import run

END = "$endOfMessage"

class Parser:
    def __init__(self):
        self.workload: Workload = Workload()
        self.help_commands = [
            (f"\nhelp|h", "See commands."),
            (f"\nworklad|w", "See *w h."),
            (f"\nsleep|s", "Long sleep mode."),
            (f"\nbook|b", "See the book."),
            (f"\ntray", "Send the cat to taskbar."),
            (f"\nconfig", "See the configurations."),
            (f"\ng", "Google it."),
            (f"\nexit", "Terminate cat.")
            ]
        self.commands: dict = {
            '*': {'help': 'Toggle message box', 'func': self.open_close_messagebox},
            ('h', 'help'): {'help': 'Show help', 'func': self.help},
            ('w', 'workload'): {'help': 'Handle workload', 'func': self.handle_workload},
            ('s', 'sleep'): {'help': 'De/activate sleep mode', 'func': self.sleep},
            'tray': {'help': 'Toggle tray icon', 'func': self.tray},
            'config': {'help': 'Handle configuration', 'func': self.handle_config},
            'exit': {'help': 'Exit application', 'func': self.exit_application},
            'g': {'help': 'Google search', 'func': self.google_search},
            ('b', 'book'): {'help': 'Toggle book', 'func': self.open_close_book}
        }

        self.workload_commands: dict = {
            ('h', 'help'): {'help': 'Show workload help', 'func': self.workload_help},
            ('l', 'list'): {'help': 'List workloads', 'func': self.workload_list},
            ('s', 'save'): {'help': 'Save workload', 'func': self.workload.save_workload},
            ('r', 'run'): {'help': 'Run workload', 'func': self.workload.run_workload},
            ('e', 'edit'): {'help': 'Edit configuration', 'func': self.handle_config},
            ('d', 'delete'): {'help': 'Delete workload', 'func': self.workload_delete}
        }

        self.name_required_arguments: list = ["g", "workload", "w", "s","save","r","run","d","delete"]        
        self.workload_help_string = "*workload|w\n   help|h\n   list|l\n   run|r [Workload Name]\n   save|s [Workload Name]\n   edit|e [Workload Name]\n   delete|d [Workload Name]]"

    def parser(self, message) -> str:
        if not message or len(message) == 0:
            raise functions.CommandException(string_to_book="Message is not eligible.")
        command = message[0]
        for key in self.commands:
            if command in key and command in self.name_required_arguments:
                return self.commands[command]['func'](message[1:])
            elif command in key and not command in self.name_required_arguments:
                check_end = self.get_next(message=message, word=command)
                if check_end == END:
                    return self.commands[command]['func']()
                else: raise functions.CommandException(string_to_book="The number of argument is more than expected.")
            raise functions.CommandException(string_to_book="Command is not found.")

    def get_next(self, message, word):
        if len(message) > message.index(word)+1:
            try:
                return str(message[message.index(word)+1]) 
            except:
                raise functions.CommandException(string_to_book="Unknown argument error.")
        raise functions.CommandException(string_to_book="Missing argument error.")

    def handle_workload(self, message) -> None:
        command = message[0]
        if command in self.workload_commands:
            if command in self.name_required_arguments:
                next_word = self.get_next(message=message, word=message[0])
                check_end = self.get_next(message=message, word=message[1])
                if check_end == END:
                    return self.workload_commands[command](next_word)
                else: raise functions.CommandException(string_to_book="The number of argument is more than expected.")
            else:
                check_end = self.get_next(message=message, word=command)
                if check_end == END:
                    return self.workload_commands[command]()
                else: raise functions.CommandException(string_to_book="The number of argument is more than expected.")
        raise functions.CommandException(string_to_book="Unknown workload command.")

    def workload_help(self):
        raise functions.CommandException(string_to_book=self.generate_help_string(dict_to_str=self.workload_commands), show_book=True)
    
    def workload_delete(self,name:str):
        functions.delete_key(f"workloads.{name}")

    def handle_config(self):
        run("zconfig.json", shell=True)

    def exit_application(self):
        raise functions.CommandException(exit=True)

    def google_search(self, query):
        webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(functions.find_key("config.paths.chrome")))
        webbrowser.get('chrome').open(f"https://www.google.com/search?q={' '.join(query)}")
        raise functions.CommandException(hide_book=True, hide_messagebox=True)

    def open_close_book(self):
        raise functions.CommandException(switch_book_vis=True)
    
    def open_close_messagebox(self):
        raise functions.CommandException(switch_messagebox_vis=True)

    def help(self):
        raise functions.CommandException(help=True, string_to_book=self.generate_help_string(dict_to_str=self.commands))

    def sleep(self):
        raise functions.CommandException(sleep=True, hide_book=True, hide_messagebox=True)

    def tray(self):
        raise functions.CommandException(tray=True, hide_book=True, hide_messagebox=True)

    def workload_list(self):
        data = None
        string_to_book = ""
        with open("zconfig.path", 'r') as file:
            data = load(file)
        i=0
        if len(list(data['workloads'].keys())) > 0:
            string_to_book += "\nWorkloads:"
            for workload in list(data['workloads'].keys()):
                string_to_book += f"{i}- {workload}\n"
                i+=1
        else: string_to_book += f"\nNo workload founded...\n"
        raise functions.CommandException(show_book=True, string_to_book=string_to_book)

    def generate_help_string(self,dict_to_str:dict) -> str:
        help_strings = []
        for key, command_info in dict_to_str.items():
            if isinstance(key, tuple):
                keys = '|'.join(key)
            else:
                keys = key
            help_message = command_info['help']
            help_strings.append(f"{keys}: {help_message}")
        return '\n'.join(help_strings)
    
app = Parser()
app.parser(f"*b {END}")