import webbrowser
from settings import functions
from workload import Workload
from subprocess import run
from os.path import exists

END = "$endOfMessage"

class Parser:
    def __init__(self):
        """Customizable Parser
        """
        self.workload: Workload = Workload()
        self.commands: dict = {
            '*': {'help': 'Toggle message box', 'func': self.open_close_messagebox},
            ('h', 'help'): {'help': 'Show help', 'func': self.help},
            ('w', 'workload'): {'help': 'Handle workload', 'func': self.handle_workload},
            ('s', 'sleep'): {'help': 'De/activate sleep mode', 'func': self.sleep},
            'tray': {'help': 'Toggle tray icon', 'func': self.tray},
            'config': {'help': 'Handle configuration', 'func': self.open_config_file},
            'exit': {'help': 'Exit application', 'func': self.exit_application},
            'g': {'help': 'Google search', 'func': self.google_search},
            ('b', 'book'): {'help': 'Toggle book', 'func': self.open_close_book},
            "dnd": {'help': 'Toggle do not disturb mode', 'func': self.dnd},
            "silent": {'help': 'Silent notification', 'func': self.silent_notification},
        }

        self.workload_commands: dict = {
            ('h', 'help'): {'help': 'Show workload help', 'func': self.workload_help},
            ('l', 'list'): {'help': 'List workloads', 'func': self.workloads_list},
            ('s', 'save', 'new'): {'help': 'Save workload', 'func': self.save_workload},
            ('r', 'run'): {'help': 'Run workload', 'func': self.workload.run_workload},
            ('e', 'edit'): {'help': 'Edit configuration', 'func': self.open_workloads_file},
            ('d', 'del', 'delete'): {'help': 'Delete workload', 'func': self.workload_delete}
        }

        self.name_required_arguments: list = ["g", "workload", "w", "s", "save","r","run","d","delete", "del", "new"]        
        self.workload_help_string = "*workload|w\n   help|h\n   list|l\n   run|r [Workload Name]\n   save|s [Workload Name]\n   edit|e [Workload Name]\n   delete|d [Workload Name]]"

    def parser(self, message: list):
        """Main parser function that gets the arguments and perform parsing and does the actions.

        Args:
            message (list): List of words of the messages. Ends with '$endOfMessage'.

        Raises:
            functions.CommandException: Checks if the message and the arguments are eligable, or a command.  
        """
        if not message or len(message) == 1:
            raise functions.CommandException("show_book", string_to_book="Message is not eligible.")
        command = message[0]
        for key in self.commands:
            if command in key and command in self.name_required_arguments:
                return self.get_command_func(command, self.commands)(message[1:])
            elif command in key and not command in self.name_required_arguments:
                check_end = self.get_next(message=message, word=command)
                if check_end == END:
                    return self.get_command_func(command, self.commands)()
                else: raise functions.CommandException("show_book", string_to_book="The number of argument is more than expected.")
        raise functions.CommandException("show_book", string_to_book="Command is not found.")

    def dnd(self): raise functions.CommandException('dnd')
    def silent_notification(self): raise functions.CommandException('silent_notification')

    def get_command_func(self, command_key: str, command_dict: dict):
        """Gets the dictionary and the key. Returns the correspounding function.

        Args:
            command_key (str): Target key.
            command_dict (dict): Target dictionary.

        Returns:
            function: Target function.
            None: If no function is found.
        """
        for key, command_info in command_dict.items():
            if (isinstance(key, tuple) and command_key in key) or key == command_key:
                return command_info['func']
        return None

    def get_next(self, message: list, word: str) -> str:
        """Founds the next word after the work in the message list.

        Args:
            message (list): _description_
            word (str): _description_

        Raises:
            functions.CommandException: Unknown or Missing Argument error.

        Returns:
            str: Returns next word in list.
        """
        if len(message) > message.index(word)+1:
            try:
                return str(message[message.index(word)+1]) 
            except:
                raise functions.CommandException("show_book", string_to_book="Unknown argument error.")
        raise functions.CommandException("show_book", string_to_book="Missing argument error.")

    def handle_workload(self, message: list):
        """When a workload command tried to be perform, this functions continues the process.

        Args:
            message (list)

        Raises:
            functions.CommandException: Unknown or Missing Argument error.
            functions.CommandException: Checks if the message and the arguments are eligable, or a command.
        """
        command:str = message[0]
        for key in self.workload_commands:
            if command in key:
                if command in self.name_required_arguments:
                    next_word = self.get_next(message=message, word=message[0])
                    check_end = self.get_next(message=message, word=message[1])
                    if check_end == END:
                        return self.get_command_func(command, self.workload_commands)(next_word)
                    else: raise functions.CommandException("show_book", string_to_book="The number of argument is more than expected.")
                else:
                    check_end = self.get_next(message=message, word=command)
                    if check_end == END:
                        return self.get_command_func(command, self.workload_commands)()
                    else: raise functions.CommandException("show_book", string_to_book="The number of argument is more than expected.")
        raise functions.CommandException("show_book", string_to_book="Unknown or missing workload command.")

    def workload_help(self):
        """Workload Help

        Raises:
            functions.CommandException: Returns "show_book" and help string.
        """
        raise functions.CommandException("show_book", string_to_book=f"Workload Commands:\n{self.generate_help_string(dict_to_str=self.workload_commands)}")
    
    def workload_delete(self, name:str):
        """Deletes target worklaod

        Args:
            name (str): Workload name.
        """
        functions.delete_key(f"workloads.workloads.{name}")

    def open_config_file(self):
        """Opens config.json.
        """
        try:
            return run(functions.CONFIG_PATH, shell=True)
        except:
            raise functions.CommandException(file_error = 'config')
        
    def open_workloads_file(self):
        """Opens config.json.
        """
        try:
            return run(functions.WORKLOADS_PATH, shell=True)
        except:
            raise functions.CommandException(file_error = 'workloads')

    def exit_application(self):
        """Terminates program.

        Raises:
            functions.CommandException: Returns "exit"
        """
        raise functions.CommandException("exit")

    def google_search(self, query: list):
        """Performs a google search.

        Args:
            query (list)

        Raises:
            functions.CommandException: Returns "check_chrome_path", "hide_book", "hide_messagebox", "show_book"
        """
        chrome_path = functions.find_key("config.paths.chrome")
        webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))
        if exists(chrome_path):
            webbrowser.get('chrome').open(f"https://www.google.com/search?q={' '.join(query[:-1])}")
            raise functions.CommandException("hide_book", "hide_messagebox")
        else:
            webbrowser.get(webbrowser._tryorder[0]).open(f"https://www.google.com/search?q={' '.join(query[:-1])}")
            raise functions.CommandException("check_chrome_path", "show_book")

    def open_close_book(self):
        """Opens or closes book

        Raises:
            functions.CommandException: Returns "switch_book_vis"
        """
        raise functions.CommandException("switch_book_vis")
    
    def open_close_messagebox(self):
        """Opens or closes messagebox

        Raises:
            functions.CommandException: Returns "switch_messagebox_vis"
        """
        raise functions.CommandException("switch_messagebox_vis")

    def help(self):
        """Help

        Raises:
            functions.CommandException: Returns help string
        """
        raise functions.CommandException("show_book", string_to_book=f"Commands:\n{self.generate_help_string(dict_to_str=self.commands)}")

    def sleep(self):
        """Toggle long sleep mode.

        Raises:
            functions.CommandException: Returns "sleep", "hide_book", "hide_messagebox"
        """
        raise functions.CommandException("sleep", "hide_book", "hide_messagebox")

    def tray(self):
        """Toggle tray icon mode.

        Raises:
            functions.CommandException: Returns "tray", "hide_book", "hide_messagebox"
        """
        raise functions.CommandException("tray", "hide_book", "hide_messagebox")

    def workloads_list(self):
        """List of workloads.

        Raises:
            functions.CommandException: Returns "show_book" and a list of workloads as a string.
        """
        data: dict = functions.get_data('workloads')
        if not data:
            raise functions.CommandException(file_error = 'workloads')        
        data = data['workloads']['workloads']
        string_to_book = "Workloads:\n"
        i=0
        if len(list(data.keys())) > 0:
            for workload in list(data.keys()):
                string_to_book += f"{i}- {workload}\n"
                i+=1
        else: string_to_book += f"\nNo workload found...\n"
        raise functions.CommandException("show_book", string_to_book=string_to_book[:-1])

    def generate_help_string(self,dict_to_str:dict) -> str:
        """Generates help string of a target dict.

        Args:
            dict_to_str (dict): Target dict

        Returns:
            str: Help
        """
        help_strings = []
        for key, command_info in dict_to_str.items():
            if isinstance(key, tuple):
                keys = '|'.join(key)
            else:
                keys = key
            help_message = command_info['help']
            help_strings.append(f"{keys}: {help_message}")
        return '\n'.join(help_strings)
    
    def save_workload(self, workload_name:str):
        """
        Raises:
            functions.CommandException: Returns 'save_workload'
        """
        raise functions.CommandException('save_workload', workload_name=workload_name)
    