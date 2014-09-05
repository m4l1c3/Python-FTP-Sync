#!/Library/Frameworks/Python.framework/Versions/3.4/bin python3
import os
import re
import datetime
import json

from ftplib import FTP
from Base import Base
from Logger import Logger


class FileSyncer(Base):
    ftpConnection = None
    ftpUser = ""
    ftpPassword = ""
    ftpServer = ""
    ftpPort = 21
    remoteDirectoryToSync = ""
    localDirectoryToSync = ""
    currentWorkingDirectory = ""
    remoteDirectoryTree = {}
    check_for_directory_reg_ex = re.compile("\d")

    def __init__(self, server, user, password, port, remote_directory, local_directory):
        Base.__init__(self)
        self.ftpServer = server
        self.ftpUser = user
        self.ftpPassword = password
        self.ftpPort = port
        self.remoteDirectoryToSync = remote_directory
        self.localDirectoryToSync = local_directory
        self.synchronize()

    def create_ftp_connection(self):
        Logger("Status - Opening FTP Connection at: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        ftp = FTP()
        ftp.connect(self.ftpServer, int(self.ftpPort))
        ftp.login(self.ftpUser, self.ftpPassword)
        return ftp

    @staticmethod
    def close_ftp_connection(obj_ftp):
        Logger("Status - Closing FTP Connection at: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        obj_ftp.close()

    def check_local_folders(self):
        list_of_files = []

        if not os.path.isdir("PendingDownloadQueue"):
            os.mkdir("PendingDownloadQueue")

        if os.listdir("PendingDownloadQueue"):
            for f in os.listdir("PendingDownloadQueue"):
                if not f.startswith("."):
                    list_of_files.append(f[:f.rfind(".txt")])

        if os.listdir(self.localDirectoryToSync):
            for f in os.listdir(self.localDirectoryToSync):
                list_of_files.append(f)

        return list_of_files

    def check_remote_folders(self, obj_ftp):
        list_of_files = []

        try:
            obj_ftp.cwd(self.remoteDirectoryToSync)
            obj_ftp.retrlines('NLST', list_of_files.append)
            Logger("Status - Creating Remote File List")

        except Exception as resp:
            if str(resp) == "550 No files found":
                Logger("Error - No files in this directory -- 550 No files found, " + self.remoteDirectoryToSync)
            else:
                raise

        return list_of_files

    def find_missing_folders(self, local_list, remote_list):
        return [i for i in remote_list if i not in local_list]

    def create_local_directory(self, folder_to_create):
        try:
            if not os.path.isdir(self.localDirectoryToSync + self.directory_separator + folder_to_create):
                os.mkdir(self.localDirectoryToSync + self.directory_separator + folder_to_create)
            else:
                Logger("Status - Directory: " + self.localDirectoryToSync + self.directory_separator + folder_to_create
                       + " already exists.\n")

        except Exception as e:
            Logger("Error - creating local directory: " + str(e))

    def get_directory_structure(self, obj_ftp, file_to_scan):
        Logger("Status - Checking: " + file_to_scan + " for files and folders")

        directory_directories = []
        directory_files = []
        files = []
        child_items = {}

        try:
            obj_ftp.cwd(self.remoteDirectoryToSync + self.directory_separator + file_to_scan)
            obj_ftp.retrlines('LIST', files.append)
            self.remoteDirectoryTree[obj_ftp.pwd()] = []

            for f in files:
                index = self.check_for_directory_reg_ex.search(f)
                file_or_directory_name = f[f.rfind(" "):].strip()

                if int(f[index.start()]) > 1:
                    #we have a directory
                    directory_directories.append(file_or_directory_name)
                else:
                    #we do not have a directory
                    directory_files.append(file_or_directory_name)

            self.remoteDirectoryTree[obj_ftp.pwd()] = directory_files

        except Exception as e:
            Logger("Error - An error has occurred checking for child items: " + str(e))

        if directory_directories:
            for dir in directory_directories:
                self.get_directory_structure(obj_ftp, file_to_scan + self.directory_separator + dir)

        child_items["Files"] = sorted(self.remoteDirectoryTree)

        return child_items

    def find_folder_files(self, obj_ftp, directory_tree, current_directory, directory_files):

        directory_tree["Files"][current_directory] = directory_files

        return directory_tree

    def append_download_queue(self, obj_ftp, list_of_remote_files):
        try:
            if not os.path.isdir("PendingDownloadQueue"):
                os.mkdir("PendingDownloadQueue")

            try:
                for singleFile in list_of_remote_files:
                    self.remoteDirectoryTree = {}

                    with open("PendingDownloadQueue" + self.directory_separator + singleFile + ".txt", "w") as f:
                        f.write(json.dumps(self.get_directory_structure(obj_ftp, singleFile), separators=(',', ':'), indent=4))

                self.close_ftp_connection(obj_ftp)

            except Exception as e:
                Logger("Error - Unable to write datafile: " + str(e))

        except Exception as e:
            Logger("Error - Unable to create download queue folder: " + str(e))

    def synchronize(self):
        obj_ftp = self.create_ftp_connection()
        list_of_local_folders = self.check_local_folders()
        list_of_remote_folders = self.check_remote_folders(obj_ftp)
        missing_files = self.find_missing_folders(list_of_local_folders, list_of_remote_folders)
        self.append_download_queue(obj_ftp, missing_files)
