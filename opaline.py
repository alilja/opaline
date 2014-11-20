from pprint import pprint

from yaml import load
# from scipy.interpolate import InterpolatedUnivariateSpline

from window import TimeWindow
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

        self.window_options = get_option('window')
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
                channels=channels,
                separator=get_option('separator'),
            )

            self.timestamps = self.data_object.build_timestamps(
                search_channels=channels.keys(),
            )

    def _get_data_for_time(self, start, length, timestamp_data=None):
        if timestamp_data is None:
            timestamp_data = self.timestamps

        output = {}
        for key in timestamp_data.keys():
            output[key] = []

        for key, column in timestamp_data.items():
            for data, time in column:
                if time >= start and time <= start + length:
                    output[key].append((data, time))
        return output

    def calculate(self, timestamp_data=None):
        if timestamp_data is None:
            timestamp_data = self.timestamps

        window = TimeWindow(
            width=self.window_options['width'],
            overlap=self.window_options['overlap'],
            iterations=self.window_options['iterations'],
        )
        print window.size()

        shortest_key = min(
            timestamp_data,
            key=lambda x: len(set(timestamp_data[x]))
        )

        start_time = 0
        while start_time + window.size() < len(timestamp_data[shortest_key]):
            unshifted_data = self._get_data_for_time(
                start_time,
                self.window_options['width'],
                timestamp_data
            )['bp']

            window.items = self._get_data_for_time(
                start_time,
                window.size(),  # by default this returns 15
                timestamp_data,
            )['rr']
            window.start = start_time  # to account for the shifting in start data
            for shifted_data in window:
                print shifted_data
            print "---"
            start_time += window.cursor
        # go through each list and grab the data that fits within the timestamps


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


if __name__ == "__main__":
    op = Opaline()
    op.calculate()