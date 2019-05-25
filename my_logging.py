class MyLogging:
    def __init__(self):
        self.file = None

    def cfg_log_file(self, fname):
        if self.file:
            self.file.close()
        self.file = open(fname, 'w')

    def log(self, message):
        self.file.write(message)
        self.file.write('\n')

my_logging = MyLogging()