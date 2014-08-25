import logging
import os
import datetime

from Base import Base

class Logger(Base):
    message = ""

    def __init__(self, message):
        Base.__init__(self)

    def log_error(self):
        if os.path.isdir("Logs") == False:
            os.mkdir("Logs")

        log_filename = "Logs" + self.directory_separator + datetime.datetime.now().strftime("%Y-%m-%d") + ".log"
        logging.basicConfig(filename=log_filename, level=logging.DEBUG)
        logging.debug(self.message)