import logging
import os
import datetime

from Base import Base

class Logger(Base):
    message = ""

    def __init__(self, message):
        Base.__init__(self)
        self.message = message
        self.log_error()

    def log_error(self):
        if not os.path.isdir("Logs"):
            os.mkdir("Logs")

        log_filename = "Logs" + self.directory_separator
        log_filename += datetime.datetime.now().strftime("%Y-%m-%d") + ".log"
        logging.basicConfig(filename=log_filename, level=logging.DEBUG)
        logging.debug(self.message)

