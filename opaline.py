from pprint import pprint

from yaml import load
# from scipy.interpolate import InterpolatedUnivariateSpline

from window import Window
from input_types import InputFile


class Opaline:
    def __init__(self, input_type="", **kwargs):
        def get_option(option_name):
            option = kwargs.get(option_name, self.config_info.get(option_name))
            if option is None:
                raise ValueError("No ``{0}`` found.".format(option_name))
            return option

        self.config_info = None
        with open(kwargs.get('config', "config.yaml")) as f:
            self.config_info = load(f)

        self.input_type = get_option('input_type').upper()
        self.data_object = None
        self.timestamps = None
        if self.input_type == "STREAM":
            # self.data_object = stream()
            pass
        elif self.input_type == "FILE":
            channels = get_option('channels')

            self.data_object = InputFile(
                filename=get_option('filename'),
                # load first from kwargs, otherwise default to config
                channels=channels,
                separator=get_option('separator'),
            )

            self.timestamps = self.data_object.build_timestamps(
                search_channels=channels.keys(),
            )


"""capture the rr and bp along with timestamps
and then when you need the time do a lookup for the time:
run through the list and grab all the points until we have them
within the certain time window. ie. if we need points from 0 - 3:

time   bp
0.1    23
1.2    50
2.5    34
2.9    40
3.2    11

only grab the first four points """


#if __name__ == "__main__":
op = Opaline(separator='\t')
"""seconds = op._build_second_data(op.data_object.channel_data)
op.calculate(seconds)"""
