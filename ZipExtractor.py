import zipfile

from Base import Base
from Logger import Logger


class ZipExtractor(Base):
    source_directory = ""
    destination_directory = ""
    archive_file = ""

    def __init__(self, destination_directory, archive_file):
        Base.__init__(self)
        self.destination_directory = destination_directory
        self.archive_file = archive_file
        self.process_zip_archive()

    def process_zip_archive(self):
        try:
            with zipfile.ZipFile(self.destination_directory + self.directory_separator + self.archive_file,
                                 "r") as zip_file:
                zip_file.extractall(self.destination_directory + self.directory_separator +
                                    self.archive_file[:str(self.archive_file).find(".z")])
        except Exception as e:
            Logger("Error - " + str(e))

    def is_zip_archive(self, target_file_name):
        if not zipfile.is_zipfile(target_file_name):
            return False
        else:
            return True
