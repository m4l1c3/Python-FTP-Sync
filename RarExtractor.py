import imp

from Base import Base
from Logger import Logger

rar_file = imp.load_source('rarfile', 'rarfile/rarfile.py')


class RarExtractor(Base):
    source_directory = ""
    destination_directory = ""
    archive_file = ""

    def __init__(self, source_directory, archive_file):
        Base.__init__(self)
        self.source_directory = source_directory
        self.archive_file = archive_file
        self.process_rar_archive()

    def process_rar_archive(self):
        try:
            with rar_file.RarFile(self.archive_file) as obj_rar_file:
                obj_rar_file.extractall(self.source_directory + self.directory_separator)
        except Exception as e:
            Logger("Error - Unable to extract rar: " + str(e))
