import csv


class InputStream:
    """ a stream loads data into the buffer until it has enough, then calls correlations """
    pass


class InputFile:
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

    def build_timestamps(self, channel_data, search_channels, time_channel="time"):
        output = {}
        # build the right keys
        search_channels = [key for key in search_channels if key != time_channel]
        for key in search_channels:
            output[key] = []

        for key, column in channel_data.items():
            if key != time_channel:
                previous_data_point = -1
                for line, data_point in enumerate(column):
                    if data_point != previous_data_point:
                        # make a tuple containing the data and its timestamp
                        output[key].append((data_point, channel_data[time_channel][line]))
                        previous_data_point = data_point
        return output
