mydict = {
    (1,2): ("func12", "help,1,2"),
    (3,4): ("func34", "help,3,4")
}


for key in mydict:
    if 2 in key:
        print(mydict[key][1])
        

        self.commands: dict = {
            '*': self.open_close_messagebox,
            ('h', 'help'): self.help,
            ('w', 'workload'): self.handle_workload,
            ('s', 'sleep'): self.sleep,
            : self.sleep,
            'tray': self.tray,
            'config': self.handle_config,
            'exit': self.exit_application,
            'g': self.google_search,
            'b','book': self.open_close_book,
            : self.open_close_book
        }