class Window:
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

    def __len__(self):
        """ returns the minimum number of items needed for all iterations """
        return (self.width - self.overlap) * (self.iterations) + self.width - self.cursor

    def __iter__(self):
        self.offset = 0
        return self

    def next(self):
        self.offset += self.cursor
        if self.offset + self.width > len(self.items) + self.cursor:
            raise StopIteration
        baseline = self.offset + self.start - self.cursor
        return self.items[
            baseline:
            baseline + self.width
        ]
if __name__ == "__main__":
    window = Window(overlap=9)
    window.items = range(len(window))
    for i in window:
        print i, len(i)
