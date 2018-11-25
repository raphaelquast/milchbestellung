from milchbestellung.gui import gui
import sys

def run(arg):
    asdf = gui()
    asdf.gui(arg)

if __name__ is '__main__':
    run(sys.argv[1:])