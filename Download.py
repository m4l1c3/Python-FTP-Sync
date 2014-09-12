import shutil
import os

from Base import Base
from ftpSync import FileSyncer

class Download(Base):
    ftp_connection = None
    parent_directory = ""
    file_to_download = ""
    size_written = 0

    def __init__(self, obj_ftp, parent_directory, file_to_download):
        Base.__init__(self)
        self.ftp_connection = obj_ftp
        self.parent_directory = parent_directory
        self.file_to_download = file_to_download
        self.download()

    def download(self):
        try:
            obj_ftp = self.ftp_connection.create_ftp_connection()
            obj_ftp.sendcmd("TYPE i")
            with open(str(self.file_to_download).replace("u'","").replace("'",""), "wb") as file:
                print("Downloading: " + self.file_to_download)
                obj_ftp.retrbinary("RETR " + self.parent_directory + self.directory_separator + self.file_to_download, file.write)

            shutil.move(self.file_to_download, self.local_directory_to_sync + self.directory_separator + self.parent_directory.replace(self.remote_directory_to_sync, ""))
        except Exception as e:
            print("Error downloading: " + str(e))