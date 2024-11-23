import sys
import os
import platform

colors = True  # Output should be colored
machine = sys.platform  # Detecting the os of current system
checkplatform = platform.platform() # Get current version of OS
if machine.lower().startswith(('os', 'win', 'darwin', 'ios')):
    colors = False  # Colors shouldn't be displayed on mac & windows
if checkplatform.startswith("Windows-10") and int(platform.version().split(".")[2]) >= 10586:
    colors = True
    os.system('')   # Enables the ANSI
if not colors:
    end = red = white = green = yellow = run = bad = good = info = que = ''
else:
    white = '~'
    green = '~'
    red = '~'
    yellow = '~'
    end = '~'
    back = '~'
    info = '~'
    que = '~'
    bad = '~'
    good = '~'
    run = '~'
