from window import Window
from input_types import InputFile

class Opaline:
    def __init__(self, input_type, filename):
        self.input_type = input_type
        if input_type is "STREAM":
            #self.data_object = stream()
            pass
        elif input_type is "FILE":
            self.data_object = InputFile(filename,{"sec":"time", "CH40":"bp", "CH46":"rr"},separator="\t")
        else:
            raise ValueError, "Unknown input type \"%s\"." % input_type

    
