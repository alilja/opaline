import csv
import time

from libbiopacndt_py import Client


class _Input(object):
    def build_timestamps(self, search_channels, channel_data=None, time_channel="time"):
        if channel_data is None:
            channel_data = self.channel_data

        output = {}
        # build the right keys
        search_channels = [key for key in search_channels if key != time_channel]
        for key in search_channels:
            output[key] = []

        for key, column in channel_data.items():
            if key != time_channel:
                previous_data_point = None
                for line, data_point in enumerate(column):
                    if data_point != previous_data_point:
                        # make a tuple containing the data and its timestamp
                        output[key].append((data_point, channel_data[time_channel][line]))
                        previous_data_point = data_point
        return output


class InputStream(_Input):
    """ a stream loads data into the buffer until it has enough, then calls correlations """
    def __init__(self, channels, server, port, lookup):
        self.channels = channels  # bp, rr, etc
        self.remote_channels = [bio_chan for local_chan, bio_chan in lookup.items() if local_chan in channels]
        self.lookup = lookup

        self.client = Client(self.remote_channels, server, port)
        self.client.connect()

    def get_data(self, size, channels):
        data = {channel: [] for channel in channels}
        data["time"] = []
        initial_time = time.time()
        for i in range(size):
            data_time = 0
            for channel in channels:
                item = self.client.poll(self.lookup[channel]).next()
                data[channel].append(item[0])
                data_time += item[1]
            # append the average times
            data["time"].append(data_time / 2)
        return data


class InputFile(_Input):
    """ expects a filename, and a dict of strings where the keys are the human-readble channel
    names and the values are the channel names in the text file.

    InputFile.data is the raw data, with no processing of any kind (including type changes)

    InputFile.channel_data is a dictionary of lists of floats, with the human-readable channel
    name as the key and the values for that channel in the list.
    """
    def __init__(self, filename, channels, separator=","):
        with open(filename) as data_file:
            data_matrix = list(csv.reader(data_file, delimiter=separator))

        # find the channel info
        header_location = self._find_header(data_matrix)
        channel_info = data_matrix[header_location]
        channel_indices = dict(
            (channel_name, channel_info.index(channel_key)) for
            channel_name, channel_key in channels.items()
        )
        self.data = data_matrix[header_location + 2:]  # strip header

        # build channel data dictionary
        self.channel_data = dict((channel_name, list()) for channel_name, index in channel_indices.items())
        for line, row_data in enumerate(self.data):
            if not row_data or row_data is None or row_data == "":
                if line + 1 < len(self.data):
                    if self.data[line + 1] == "" or self.data[line + 1] is None:
                        break
            for name, index in channel_indices.items():
                if index >= len(row_data):
                    break
                value = float(row_data[index].strip())
                self.channel_data[name].append(value)

    def _find_header(self, csv_data, flag="CH"):
        for i, line in enumerate(csv_data):
            if any(flag in s for s in line):
                return i
        else:
            raise ValueError("Flag \"%s\" not found. Header missing?" % flag)
