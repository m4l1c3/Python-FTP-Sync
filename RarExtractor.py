import imp
from Base import Base
rar_file = imp.load_source('rarfile', 'rarfile/rarfile.py')


class RarArchive(Base):
    source_directory = ""
    destination_directory = ""
    archive_file = ""

    def __init__(self, source_directory, destination_directory, archive_file):
        self.source_directory = source_directory
        self.destination_directory = destination_directory
        self.archive_file = archive_file
        self.process_rar_archive()

    def process_rar_archive(self):
        try:
            with rar_file.RarFile(self.source_directory + self.directory_separator + self.archive_file) as obj_rar_file:
                print("Extracting - " + str(obj_rar_file))
                obj_rar_file.extractall(self.destination_directory)
        except Exception as e:
            print("Error - Unable to extract rar: " + str(e))