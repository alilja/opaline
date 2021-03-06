#!/usr/bin/env python
from yaml import load
from scipy.interpolate import interp1d
from scipy.stats.stats import pearsonr

from window import TimeWindow
from input_types import InputFile, InputStream


class Opaline(object):
    def __init__(self, config_file=None, **kwargs):
        """Note that one of the channels must have a human-readable name of "time" with
        timestamps correlated with the data. This is used to build the lookup table of
        when cardiovascular events occured.

        Args:
            config_info (string): The path to the configuration file.
            window (dict): Configuration for the moving window. See window.py for more
                information.
            input_type (string): ``STREAM`` or ``FILE`` depending on whether or not
                you want real-time or static data. Arguments after this point are
                broken down by input type.

            FILE:
            filename (string): The path to the data file.
            separator (string): The separator for columns in the file. For example,
                in CSV file, it would be a comma. Defaults to a comma.
            channels (dict): A dict, where keys are the human-readable name of the
                channel and the value is the actual column heading in the data file.
            shifted_channel (string): The human-readable name of the channel that will
                be shifted by the window.

            STREAM:
            manifest_location (string): Location of the manifest_lookup.yaml file.
            server (string): The server address.
            port (int): The port number."""

        def _get_option(option_name):
            """Looks for an option first form **kwargs and then from the config file.

            Args:
                option_name (string): the name of the kwarg or line in the config file.

            Returns:
                The value of that argument."""
            option = kwargs.get(option_name, self.config_info.get(option_name))
            if option is None:
                raise ValueError("No ``{0}`` found.".format(option_name))
            return option

        self.config_info = None
        with open(config_file) as f:
            self.config_info = load(f)

        self.window_options = _get_option('window')
        self.data_object = None
        channels = _get_option('channels')

        self.input_type = _get_option('input_type').upper()
        if self.input_type == "STREAM":
            # get the manifest map that matches biopacd channels with
            # human-readable channel names

            try:
                manifest_lookup_file = _get_option('manifest_location')
            except ValueError:
                manifest_lookup_file = "config/manifest_lookup.yaml"
            with open(manifest_lookup_file) as f:
                manifest_lookup = load(f)

            # remove time from input channels since we're doing that
            # manually
            try:
                del channels["time"]
            except ValueError:
                pass

            self.data_object = InputStream(
                channels,
                _get_option('server'),
                _get_option('port'),
                manifest_lookup,
            )

            self._stream_spline(channels)

        elif self.input_type == "FILE":

            self.data_object = InputFile(
                filename=_get_option('filename'),
                channels=channels,
                separator=_get_option('separator'),
            )

            # get data in timestamp format
            self.timestamps = self.data_object.build_timestamps(
                search_channels=channels.keys(),
            )
            print self.timestamps

            # greedily find the unshifted channel
            self.shifted_channel = _get_option('shifted_channel')
            self.unshifted_channel = ""
            for key in channels.keys():
                if key != self.shifted_channel and key != "time":
                    self.unshifted_channel = key
                    break

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

    @staticmethod
    def _get_spline(channel_data):
        return interp1d(
            [data[1] for data in channel_data],
            [data[0] for data in channel_data],
            kind='cubic',
        )

    @staticmethod
    def _bound_range(low_bound, high_bound, required_items):
        """Returns a list of numbers within a certain range,
        with a ``required_items`` number of items."""
        step = float(high_bound - low_bound) / float(required_items)
        out = []
        i = 0
        while i < required_items:
            out.append(step * i + low_bound)
            i += 1
        return out

    def _stream_spline(self, channels):
        # steps here: fill the buffer up as far as needed
        # then build the timestamp data
        # then pass that to the spliner
        # do this until quit
        import time
        time.sleep(3)
        data = self.data_object.get_data(50, channels)
        self.timestamps = self.data_object.build_timestamps(
            search_channels=channels.keys(),
            channel_data=data,
        )
        print self.timestamps

    def calculate(self, timestamp_data=None, shifted_channel='bp', unshifted_channel='rr'):
        if timestamp_data is None:
            timestamp_data = self.timestamps

        window = TimeWindow(
            width=self.window_options['width'],
            overlap=self.window_options['overlap'],
            iterations=self.window_options['iterations'],
        )
        shortest_key = min(
            timestamp_data,
            key=lambda x: len(set(timestamp_data[x]))
        )

        brs = []
        start_time = 0
        # this while loop needs to be broken out
        while start_time + window.size() < len(timestamp_data[shortest_key]) + 1: #BROKEN
            # first, get the splines and their correlation

            # get the data for the unshifted channel
            unshifted_data = self._get_data_for_time(
                start_time,
                window.width,
                timestamp_data,
            )[unshifted_channel]
            # calculate the spline for it
            unshifted_spline = Opaline._get_spline(unshifted_data)

            # load the window with the right number of items
            # it needs to shift the other channel
            window.items = self._get_data_for_time(
                start_time,
                window.size(),  # by default this returns 15
                timestamp_data,
            )[shifted_channel]
            # the data shifts -- make sure the window is shifting with it
            window.start = start_time

            highest_r = 0
            splines = []
            for shifted_data in window:
                shifted_spline = Opaline._get_spline(shifted_data)
                # if the window is 10 seconds, sample the spline 10 times
                # This is a 1 Hz sample rate
                correlation_r, two_tail_p = pearsonr(
                    unshifted_spline(Opaline._bound_range(
                        unshifted_data[0][1],
                        unshifted_data[-1][1],
                        window.width
                    )),
                    shifted_spline(Opaline._bound_range(
                        shifted_data[0][1],
                        shifted_data[-1][1],
                        window.width
                    ))
                )
                if two_tail_p <= 0.01 and correlation_r > 0:
                    print correlation_r, two_tail_p
                    if correlation_r > highest_r:
                        splines = [unshifted_spline, shifted_spline]
                        highest_r = correlation_r

            if len(splines) == 0:
                brs.append(None)
            else:
                brs.append((highest_r, splines))
            start_time += window.cursor
        return brs


if __name__ == "__main__":
    op = Opaline("config/config.yaml")
    """print op.calculate(
        shifted_channel=op.shifted_channel,
        unshifted_channel=op.unshifted_channel,
    )"""
