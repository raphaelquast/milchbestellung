from milchbestellung import gui
import sys

def run(arg):
    # initialize class object
    asdf = gui()
    # call gui
    asdf.gui(arg)


if __name__ == '__main__':
    run(sys.argv[1:])