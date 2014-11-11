from yaml import load

from window import Window
from input_types import InputFile

from pprint import pprint

class Opaline:
    def __init__(self, input_type="", **kwargs):
        self.input_type = input_type
        with open(kwargs.get('config',"config.yaml")) as f:
            config_info = load(f)
        if input_type == "":
            if "input_type" in config_info.keys():
                input_type = config_info['input_type'].upper()
            else:
                raise ValueError, "No input type found."
        if input_type == "STREAM":
            #self.data_object = stream()
            pass
        elif input_type == "FILE":
            filename = kwargs.get('filename')
            if filename is None:
                if "input_file" in config_info.keys():
                    filename = config_info['input_file']
                else:
                    raise ValueError, "No filename entered."
            self.data_object = InputFile(
                    filename,
                    kwargs.get('channels',{"sec":"time", "CH40":"bp", "CH46":"rr"}),
                    separator=kwargs.get('separator',','),
                )
        else:
            raise ValueError, "Unknown input type \"%s\"." % input_type

    def _build_second_data(self, channel_data):
        start_index = 0
        output = []
        for index, time in enumerate(channel_data['time']):
            if time % 1 == 0 and time != 0:
                output.append((
                    channel_data['bp'][start_index:index+1],
                    channel_data['rr'][start_index:index+1],
                    channel_data['time'][start_index:index+1],
                    ))
                start_index = index
        return output

op = Opaline(filename="data/brs_250.txt", separator='\t')
seconds = op._build_second_data(op.data_object.channel_data)
print(len(seconds[0][0]))