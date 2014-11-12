from yaml import load

from window import Window
from input_types import InputFile

from pprint import pprint

class Opaline:
    def __init__(self, input_type="", **kwargs):
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

    def _build_second_data(self, channel_data):
        start_index = 0
        output = []
        for index, time in enumerate(channel_data['time']):
            if time % 1 == 0 and time != 0:
                output.append((
                    channel_data['time'][start_index:index+1],
                    channel_data['bp'][start_index:index+1],
                    channel_data['rr'][start_index:index+1],
                    ))
                start_index = index
        return output

if __name__ == "__main__":
    op = Opaline(filename="data/brs_250.txt", separator='\t')
    seconds = op._build_second_data(op.data_object.channel_data)
    print(seconds[1][2])