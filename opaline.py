from pprint import pprint

from yaml import load
#from scipy.interpolate import InterpolatedUnivariateSpline

from window import Window
from input_types import InputFile


class Opaline:
    def __init__(self, input_type="", **kwargs):
        self.config_info = None
        with open(kwargs.get('config', "config.yaml")) as f:
            self.config_info = load(f)

        self.input_type = input_type
        if input_type == "":
            if "input_type" in self.config_info.keys():
                input_type = self.config_info['input_type'].upper()
            else:
                raise ValueError

        if input_type == "STREAM":
            # self.data_object = stream()
            pass
        elif input_type == "FILE":
            filename = kwargs.get('filename')
            if filename is None:
                if "input_file" in self.config_info.keys():
                    filename = self.config_info['input_file']
                else:
                    raise ValueError("No ``input_file`` found.")

            self.data_object = InputFile(
                filename=filename,
                # load first from kwargs, otherwise default to config
                channels=kwargs.get('channels', self.config_info.get('channels')),
                separator=kwargs.get('separator', ','),
            )
            self.data_object.channel_data = self.data_object.eliminate_repeats(
                self.data_object.channel_data
            )
        else:
            raise ValueError("No ``input_type`` found.")

    def _build_second_data(self, channel_data):
        """ returns a list of tuples, where every tuple contains the channel
        data for one second. That is, each tuple is exactly one second long.

        seconds[0][1] will return the blood pressure data for the first second,
        seconds[1][1] will return it for the second, etc. """
        start_index = 0
        output = []
        for index, time in enumerate(channel_data['time']):
            if time % 1 == 0 and time != 0:
                output.append({
                    'time': channel_data['time'][start_index:index],
                    'bp': channel_data['bp'][start_index:index],
                    'rr': channel_data['rr'][start_index:index],
                })
                start_index = index
        return output

    def calculate(self, second_data, **kwargs):
        def get_second_tuples(channel_name, start, num):
            return [item[channel_name] for item in second_data[start:start + num]]

        def collapse_second_tuples(tuples):
            return [item for sublist in tuples for item in sublist]

        window_config = self.config_info.get('window')
        if window_config is None:
            window_config = {}
        width = window_config.get('width', kwargs.get('width'))
        overlap = window_config.get('overlap', kwargs.get('overlap'))
        iterations = window_config.get('iterations', kwargs.get('iterations'))
        assert width, "Could not find width."
        assert overlap, "Could not find overlap."
        assert iterations, "Could not find iterations."

        start = 0
        shift_window = Window(
            width=width,
            iterations=iterations,
            overlap=overlap,
            reset_start=True
        )

        # this gets ``width`` number of tuples for bp data, representing
        # ``width`` seconds of that data. defaults to 10 seconds, so 10
        # tuples. then it collapses it into a single list so we can spline
        # it down the line.
        unshifted = collapse_second_tuples(get_second_tuples(
            channel_name='bp',
            start=start,
            num=width,
        ))
        # does the same, but gets ``len(shift_window)`` tuples
        # by default this is 15, to cover the overlap required
        all_shifted = get_second_tuples(
            channel_name='rr',
            start=start,
            num=len(shift_window)
        )

        shift_window.start = 0
        shift_window.items = all_shifted
        for windowed_data in shift_window:
            shifted = collapse_second_tuples(windowed_data)
            print(len(shifted))
            #print "---"
            #all_items = window #[item for sublist in window for item in sublist]
            #x = range(len(all_items))
            #spline = InterpolatedUnivariateSpline(x, all_items, k=3)

            #numbers = self._function_to_list(spline, len(all_items))
            # spline!
            # correlate!
            #plt.plot(unshifted)
            #plt.plot(spline(x))
            #return spline
            break




#if __name__ == "__main__":
op = Opaline(filename="data/brs_250.txt", separator='\t')
"""seconds = op._build_second_data(op.data_object.channel_data)
op.calculate(seconds)"""
