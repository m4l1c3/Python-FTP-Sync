#!/Library/Frameworks/Python.framework/Versions/3.4/bin python3
import os
import re
import datetime
import json

from ftplib import FTP
from Base import Base
from Logger import Logger


class FileSyncer(Base):
    ftp_connection = None
    remote_directory_tree = {}
    check_for_directory_reg_ex = re.compile("\d")
    current_working_directory = ""
    def __init__(self):
        Base.__init__(self)
        self.synchronize()

    def create_ftp_connection(self):
        Logger("Status - Opening FTP Connection at: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        ftp = FTP()
        ftp.connect(self.ftp_server, int(self.ftp_port))
        ftp.login(self.ftp_user, self.ftp_password)
        return ftp

    @staticmethod
    def close_ftp_connection(obj_ftp):
        Logger("Status - Closing FTP Connection at: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        obj_ftp.close()

    def check_local_folders(self):
        list_of_files = []

        if not os.path.isdir("PendingDownloadQueue"):
            os.mkdir("PendingDownloadQueue")

        for f in os.listdir("PendingDownloadQueue"):
            if not f.startswith("."):
                list_of_files.append(f[:f.rfind(".txt")])

        for f in os.listdir(self.local_directory_to_sync):
            list_of_files.append(f)

        if not os.path.isdir("ProcessingFiles"):
            os.mkdir("ProcessingFiles")

        for f in os.listdir("ProcessingFiles"):
            if not f.startswith("."):
                list_of_files.append(f[:f.rfind(".txt")])

        return list_of_files

    def check_remote_folders(self, obj_ftp):
        list_of_files = []

        try:
            obj_ftp.cwd(self.remote_directory_to_sync)
            obj_ftp.retrlines('NLST', list_of_files.append)
            Logger("Status - Creating Remote File List")

        except Exception as resp:
            if str(resp) == "550 No files found":
                Logger("Error - No files in this directory -- 550 No files found, " + self.remote_directory_to_sync)
            else:
                raise

        return list_of_files

    @staticmethod
    def find_missing_folders(local_list, remote_list):
        return [i for i in remote_list if i not in local_list]

    def create_local_directory(self, folder_to_create):
        try:
            if not os.path.isdir(self.local_directory_to_sync + self.directory_separator + folder_to_create):
                os.mkdir(self.local_directory_to_sync + self.directory_separator + folder_to_create)
            else:
                Logger("Status - Directory: " + self.local_directory_to_sync + self.directory_separator + folder_to_create
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
            obj_ftp.cwd(self.remote_directory_to_sync + self.directory_separator + file_to_scan)
            obj_ftp.retrlines('LIST', files.append)
            self.remote_directory_tree[obj_ftp.pwd()] = []

            for f in files:
                index = self.check_for_directory_reg_ex.search(f)
                file_or_directory_name = f[f.rfind(" "):].strip()

                if int(f[index.start()]) > 1:
                    #we have a directory
                    directory_directories.append(file_or_directory_name)
                else:
                    #we do not have a directory
                    directory_files.append(file_or_directory_name)

            self.remote_directory_tree[obj_ftp.pwd()] = directory_files

        except Exception as e:
            Logger("Error - An error has occurred checking for child items: " + str(e))

        if directory_directories:
            for d in directory_directories:
                self.get_directory_structure(obj_ftp, file_to_scan + self.directory_separator + d)

        child_items["Files"] = self.remote_directory_tree

        return child_items

    @staticmethod
    def find_folder_files(directory_tree, current_directory, directory_files):
        directory_tree["Files"][current_directory] = directory_files

        return directory_tree

    def append_download_queue(self, obj_ftp, list_of_remote_files):
        try:
            if not os.path.isdir("PendingDownloadQueue"):
                os.mkdir("PendingDownloadQueue")

            try:
                for single_file in list_of_remote_files:
                    self.remote_directory_tree = {}

                    with open("PendingDownloadQueue" + self.directory_separator + single_file + ".txt", "w") as f:
                        f.write(json.dumps
                                (
                                    self.get_directory_structure(obj_ftp, single_file),
                                    separators=(',', ':'), indent=4, sort_keys=True
                                )
                               )

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