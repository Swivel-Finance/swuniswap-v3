from colorama import init, deinit, Fore

def start():
    init()

def stop():
    deinit()

def white(s):
    return Fore.WHITE + s

def yellow(s):
    return Fore.YELLOW + s

def blue(s):
    return Fore.BLUE + s

def green(s):
    return Fore.GREEN + s

def red(s):
    return Fore.RED + s

def cyan(s):
    return Fore.CYAN + s

def magenta(s):
    return Fore.MAGENTA + s
