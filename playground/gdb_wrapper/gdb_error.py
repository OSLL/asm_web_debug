class gdb_error(Exception):
    """Exception raised for errors in gdb.

    Attributes:
        log -- log received from gdb with error
        message -- explanation of the error
    """

    def __init__(self, log, message):
        self.log = log
        self.message = message
