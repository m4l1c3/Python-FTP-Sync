import zipfile
from Base import Base
from Logger import Logger


class ZipArchive(Base):
    source_directory = ""
    destination_directory = ""
    archive_file = ""

    def __init__(self, source_directory, destination_directory, archive_file):
        Base.__init__(self)
        self.source_directory = source_directory
        self.destination_directory = destination_directory
        self.archive_file = archive_file
        self.process_zip_archive()

    def process_zip_archive(self):
        try:
            with zipfile.ZipFile(self.source_directory + self.directory_separator + self.archive_file, "r") as zip_file:
                Logger("Extracting - " + zip_file.filename)
                zip_file.extractall(self.destination_path + self.directory_separator +
                                    self.archive_file[:str(self.archive_file).find(".z")])
        except Exception as e:
            Logger(str(e))

    def is_zip_archive(self, target_file_name):
        if not zipfile.is_zipfile(target_file_name):
            return False
        else:
            return True
