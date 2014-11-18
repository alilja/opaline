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
                    if self.data[line + 1] is "" or None:
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


    # make this grab the right timestamp when it
    # gets the bp and rr
    def eliminate_repeats(self, channel_data):
        output = {}
        for key in channel_data.keys():
            output[key] = []
        for key, data in channel_data.items():
            previous_value = 0
            for item in data:
                if item != previous_value:
                    previous_value = item
                    output[key].append(item)
        return output
