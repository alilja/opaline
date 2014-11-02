from opaline.window import Window

class Opaline:
    def __init__(self, window):
        self.window = window


window = Window(range(0,100),overlap=9)
print len(window)
for n in window:
    print len(n)
    print n

