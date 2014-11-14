from yaml import load
from scipy.interpolate import UnivariateSpline

from window import Window
from input_types import InputFile

from pprint import pprint

class Opaline:
    def __init__(self, input_type="", **kwargs):
        self.config_info = None
        with open(kwargs.get('config',"config.yaml")) as f:
            self.config_info = load(f)

        self.input_type = input_type
        if input_type == "":
            if "input_type" in self.config_info.keys():
                input_type = self.config_info['input_type'].upper()
            else:
                raise ValueError, "No input type found." 

        if input_type == "STREAM":
            #self.data_object = stream()
            pass
        elif input_type == "FILE":
            filename = kwargs.get('filename')
            if filename is None:
                if "input_file" in self.config_info.keys():
                    filename = self.config_info['input_file']
                else:
                    raise ValueError, "No filename entered."

            self.data_object = InputFile(
                    filename  = filename,
                    # load first from kwargs, otherwise default to config
                    channels  = kwargs.get('channels',self.config_info.get('channels')),
                    separator = kwargs.get('separator',','),
                )
        else:
            raise ValueError, "Unknown input type \"%s\"." % input_type

        return self.data_object

    def _build_second_data(self, channel_data):
        """ returns a list of tuples, where every tuple contains the channel data
        for one second. That is, each tuple is exactly one second long. 

        seconds[0][1] will return the blood pressure data for the first second,
        seconds[1][1] will return it for the second, etc. """
        start_index = 0
        output = []
        for index, time in enumerate(channel_data['time']):
            if time % 1 == 0 and time != 0:
                output.append((
                    channel_data['time'][start_index:index],
                    channel_data['bp'][start_index:index],
                    channel_data['rr'][start_index:index],
                    ))
                start_index = index
        return output

    def calculate(self, second_data, **kwargs):
        window_config = self.config_info.get('window')
        if window_config == None: window_config = {}
        width = window_config.get('width',kwargs.get('width'))
        overlap = window_config.get('overlap',kwargs.get('overlap'))
        iterations = window_config.get('iterations',kwargs.get('iterations'))
        assert width, "Could not find width."
        assert overlap, "Could not find overlap."
        assert iterations, "Could not find iterations."

        start = 0
        shift_window = Window(width=width, iterations=iterations, overlap=overlap, reset_start=True)
        while start+len(shift_window) <= len(second_data):
            unshifted = [x[1] for x in second_data[start:start+width]]
            shift_window.start = 0
            shift_window.items = [x[2] for x in second_data[start:start+len(shift_window)]]
            for window in shift_window:
                all_items = [item for sublist in window for item in sublist]
                x = range(len(all_items))
                print(len(x))
                spline = UnivariateSpline(x, all_items, k=3)
                # spline!
                # correlate!
                print spline
            start += 1

    # see shift test for how to shift data for window
    # should be easy

if __name__ == "__main__":
    op = Opaline(filename="data/brs_250.txt", separator='\t')
    seconds = op._build_second_data(op.data_object.channel_data)
    data = [([0,1,2,3],["a","b","c","d"],[0,1,2,3]),
             ([4,5,6,7],["e","f","g","h"],[4,5,6,7]),
             ([8,9,10,11],["i","j","k","l"],[8,9,10,11]),
             ([12,13,14,15],["m","n","o","p"],[12,13,14,15]),
             ([0,1,2,3],["a","b","c","d"],[0,1,2,31]),
             ([4,5,6,7],["e","f","g","h"],[4,5,6,72]),
             ([8,9,10,11],["i","j","k","l"],[8,9,10,113]),
             ([12,13,14,15],["m","n","o","p"],[12,13,14,154])]
    op.calculate(seconds)
