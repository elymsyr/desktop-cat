mydict = {
    (1,2): ("func12", "help,1,2"),
    (3,4): ("func34", "help,3,4")
}


for key in mydict:
    if 2 in key:
        print(mydict[key][1])
        

