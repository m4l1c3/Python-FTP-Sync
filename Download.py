import shutil
import os

from Base import Base
from ftpSync import FileSyncer

class Download(Base):
    ftp_connection = None
    parent_directory = ""
    list_of_files = []

    def __init__(self, obj_ftp, parent_directory, list_of_files):
        Base.__init__(self)
        self.ftp_connection = obj_ftp
        self.parent_directory = parent_directory
        self.list_of_files = list_of_files
        self.download_file()

    def download_file(self):
        try:
            obj_ftp = self.ftp_connection.create_ftp_connection()

            for f in self.list_of_files:
                obj_ftp.sendcmd("TYPE i")
                with open(str(f).replace("u'","").replace("'",""), "wb") as download:
                    obj_ftp.retrbinary("RETR " + self.parent_directory + self.directory_separator + f, download.write)

                shutil.move(f, os.environ["FtpSyncLocalDirectory"] + self.directory_separator + self.parent_directory.replace(os.environ["FtpSyncRemoteDirectory"], ""))
        except Exception as e:
            print("Error downloading: " + str(e))