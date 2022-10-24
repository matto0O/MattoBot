import datetime

def log(command, args, msg):
    with open("errors.txt", 'a', encoding="utf-8") as file:
        file.write("\n\n===========================================\n\n")
        file.write("{} // {} {}\n {}".format(datetime.datetime.now(), command, args, msg))