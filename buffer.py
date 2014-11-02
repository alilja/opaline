class Buffer:
    def __init__(self,items, start=0, width=10, overlap=9, iterations=6):
        self.items = items
        self.width = width
        self.cursor = width-overlap
        if self.cursor <= 0:
            raise ValueError, "Overlap ({0}) is greater than or equal to width ({1}).".format(overlap, width)
        self.offset = 0
        self.iterations = iterations
        self.start = start

    def __len__(self):
        return self.iterations

    def __iter__(self):
        self.offset = 0
        return self

    def next(self):
        self.offset += self.cursor
        if(self.offset > self.iterations * self.cursor): raise StopIteration
        return self.items[self.start + self.offset - self.cursor:self.start + self.width + self.offset - self.cursor] 

buffer = Buffer(range(1,100),iterations=10)
len(buffer)
for n in buffer:
    print len(n)
    print n