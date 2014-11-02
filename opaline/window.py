class Window:
    def __init__(self, items, start=0, width=10, overlap=9, iterations=6, reset_start=False):
        self.items = items
        self.width = width
        self.overlap = overlap
        self.iterations = iterations
        self.start = start
        self.reset_start = reset_start

        self.cursor = width-overlap
        if self.cursor <= 0:
            raise ValueError, "Overlap ({0}) is greater than or equal to width ({1}).".format(overlap, width)
        self.offset = 0

    def __len__(self):
        return self.iterations # figure out the math for how much data needs to be collected

    def __iter__(self):
        self.offset = 0
        if self.reset_start: self.start = 0
        return self

    def next(self):
        self.offset += self.cursor
        if(self.offset > self.iterations * self.cursor): 
            self.start = self.offset - self.cursor
            raise StopIteration
        return self.items[self.start + self.offset - self.cursor:
            self.width + self.start + self.offset - self.cursor] 
