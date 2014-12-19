import tarfile
from Base import Base


class TarArchive(Base):
    containing_folder = ""
    destination_folder = ""
    archive_file = ""

    def __init__(self, containing_folder, destination_folder, archive_file):
        Base.__init__(self)
        self.containing_folder = containing_folder
        self.destination_folder = destination_folder
        self.archive_file = archive_file
        self.process_tar_archive()

    def process_tar_archive(self):
        try:
            obj_tar_file = tarfile.open(self.containing_folder + self.directory_separator + self.archive_file)
            print("Extracting: " + str(obj_tar_file))
            obj_tar_file.extractall(self.destination_folder)
            obj_tar_file.close()
        except Exception as e:
            print("Error - Unable to extract tar: " + str(e))