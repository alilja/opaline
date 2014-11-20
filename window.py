class TimeWindow:
    def __init__(self, items=None, start=0, width=10, overlap=9, iterations=6):
        self.items = items
        self.width = width
        self.overlap = overlap
        self.iterations = iterations
        self.start = start

        self.cursor = width - overlap
        if self.cursor <= 0:
            raise ValueError("Overlap ({0}) is greater than or equal to width ({1})."
                             .format(overlap, width))
        self.offset = 0

    def size(self):
        """ returns the minimum number of seconds needed for all iterations """
        return (self.width - self.overlap) * (self.iterations) + self.width - self.cursor

    def __iter__(self):
        self.offset = self.start
        return self

    def next(self):
        if self.offset + self.width > self.items[-1][1] + 1:
            raise StopIteration

        output = []
        for data, time in self.items:
            if time >= self.offset and time <= self.offset + self.width:
                output.append((data, time))
        self.offset += self.cursor
        return output
