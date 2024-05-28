import os,sys

EVENTS = { # eventNumber: [[actionOrderToBeCompleted], [PossibleNextEventNumbers]]
    # Left events
    0: [[1, 1, 1, 1, 2, 2, 2, 2, 1, 1, 4, 4, 4, 4, 1, 1, 1, 1, 2, 2], [0, 1, 2, 3, 5, 8, 9, 10, 11, 13, 16, 17, 18]], # idle 1
    1: [[2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 5, 5, 5, 5, 5, 5, 5, 1, 1, 1], [0, 1, 2, 3, 5, 8, 9, 10, 11, 13, 16, 17, 18]], # idle 2
    2: [[8, 8, 8], [0, 1, 2, 3, 4, 7, 8, 9, 10, 11, 12, 15, 16, 17, 18]], # walk 1
    3: [[9, 9, 9], [0, 1, 2, 3, 4, 7, 8, 9, 10, 11, 12, 15, 16, 17, 18]], # walk 2
    4: [[3], [0, 1, 2, 3, 8, 9]], # jump
    5: [[6, 6, 6], [0, 1, 5, 7, 8, 9, 13, 15, 16, 17, 5, 5, 5, 18, 20]], # sleep
    6: [[7], [0, 1, 4, 7, 7, 7, 7, 8, 9, 12]], # touch
    7: [[0], [0, 1, 4, 5, 6, 8, 9, 12, 13, 14,0, 1,0, 1]], # goosebumps
    # Right events
    8: [[11, 11, 11, 11, 12, 12, 12, 12, 11, 11, 14, 14, 14, 14, 11, 11, 11, 11, 12, 12], [0, 1, 2, 3, 5, 8, 9, 10, 11, 13, 16, 17, 18]], # idle 1 R
    9: [[12, 12, 12, 12, 12, 12, 11, 11, 11, 11, 15, 15, 15, 15, 15, 15, 15, 11, 11, 11], [0, 1, 2, 3, 5, 8, 9, 10, 11, 13, 16, 17, 18]], # idle 2 R 
    10: [[18, 18, 18], [0, 1, 2, 3, 4, 7, 8, 9, 10, 11, 12, 15, 16, 17, 18]], # walk 1 R
    11: [[19, 19, 19], [0, 1, 2, 3, 4, 7, 8, 9, 10, 11, 12, 15, 16, 17, 18]], # walk 2 R
    12: [[13], [0, 1, 10, 11, 8, 9]], # jump R
    13: [[16, 16, 16], [0, 1, 5, 7, 8, 9, 13, 15, 16, 17, 16, 16, 16, 18, 20]], # sleep R
    14: [[17], [0, 1, 4, 8, 9, 12, 15, 15, 15, 15]], # touch R
    15: [[10], [0, 1, 4, 5, 6, 8, 9, 12, 13, 14]], # goosebumps R
    # Extra events
    16: [[1, 1, 1, 1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 1, 1, 14, 14, 14, 14, 14, 15, 15, 15, 15, 15, 15, 1, 1, 1, 1, 11, 11, 11, 11, 12, 12, 12, 12, 12], [0, 1, 8, 9, 5, 17, 18, 19, 20]], # idle 3
    17: [[2, 2, 2, 2, 2, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 11, 11, 11, 11, 11, 11, 14, 14, 14, 14, 14, 14, 14, 12, 12, 11, 11, 11], [0, 1, 8, 9, 5, 16, 18, 19, 20]], # idle 4
    18: [[12, 12, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16], [0, 1, 8, 9]], # sleep long
    19: [[8, 8, 19, 19, 9, 9, 18, 18], [0, 1, 8, 9, 16, 17, 18, 20]], # walk there
    20: [[3, 0, 10], [16, 17, 18, 19]], # jump and goosebumps
    21: [[20], [21]], # falling
    22: [[7], [23,24]], # stay put
    23: [[4], [23,24]], # stay put continue
    24: [[2], [24]], # stay put continue
    25: [[6], [25]], # long sleep
}

PREVIEW = """
0: L_goosebumps.gif,  len 16
1: L_idle.gif,  len 10
2: L_idle2.gif,  len 11
3: L_jump.gif,  len 10
4: L_licking.gif,  len 13
5: L_licking2.gif,  len 14
6: L_sleep.gif,  len 11
7: L_touch.gif,  len 11
8: L_walk.gif,  len 10
9: L_walk2.gif,  len 11
"""

PREFIX = '*'

# COMMANDS = {
#     "help/h": "See the Help Book",
#     "worklad/w": "Use with [list/l | run/r [Workload Name] | create/c [Workload Name] | edit/e [Workload Name] | delete/d [Workload Name]] to use the workload operations.",
#     "sleep/s": "De/activate the long sleep mode for the cat.",
#     "menu": "See the cookbook",
#     "tray": "Send the cat to taskbar tray",
#     "config": "See the configurations",
#     "exit": "Exit program",
# }

COMMANDS = [
    (f"\n{PREFIX}help/h", "See the Help Book"),
    (f"\n{PREFIX}worklad/w", "Add h to see workload operations."),
    (f"\n{PREFIX}sleep/s", "De/activate the long sleep mode for the cat."),
    (f"\n{PREFIX}book/b", "See the book."),
    (f"\n{PREFIX}tray", "Send the cat to taskbar tray or use double click!"),
    (f"\n{PREFIX}config", "See the configurations."),
    (f"\n{PREFIX}q", "Add your sentence after it to search on google."),
    (f"\n{PREFIX}exit", "Exit program."),
]

def HELP_BOOK():
    string = "\nDektopCat Commands\n"
    max_len = max(len(command[0]) for command in COMMANDS)
    for command in COMMANDS:
        string+=(f"{command[0].ljust(max_len)}   {command[1]}\n")
    return string

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)     

GIFS_PATH = resource_path('media\\gifs')
FALLING_GIF_PATH = resource_path('media\\gifs_others\\falling.gif')
COMMAND_BG_PATH = resource_path('media\\messagebox.png')
TRAY_ICON_PATH = resource_path('media\\tray-icon.png')
FONT_PATH = resource_path('media\\pixelmix.ttf')
BOOKS_PATH = resource_path( "media\\books\\")
CONFIG_PATH = resource_path("data\\config-test.json")

CHROME_PATH = "C:/Program Files/Google/Chrome/Application/chrome.exe" 

INITIAL_X = 1400
INITIAL_Y = 922

FONT = ("pixelmix", 10)

ERROR_LIST = {
    'error$99': "Unknown argument",
    'error$98': "Missing argument",
}


# data = {
#     "events": EVENTS,
#     "commands": COMMANDS,
#     "paths": {
#         "current_path": CURRENT_PATH,
#         "gifs_path": GIFS_PATH,
#         "falling_gif_path": FALLING_GIF_PATH,
#         "command_bg_path": COMMAND_BG_PATH,
#         "tray_icon_path": TRAY_ICON_PATH,
#         "font_path": FONT_PATH,
#         "chrome_path": CHROME_PATH
#     },
#     "initial_positions": {
#         "initial_x": INITIAL_X,
#         "initial_y": INITIAL_Y
#     },
#     "error_list": ERROR_LIST
# }

# # Write to a JSON file
# with open('desktop-cat\config-test.json', 'w') as json_file:
#     json.dump(data, json_file, indent=4)