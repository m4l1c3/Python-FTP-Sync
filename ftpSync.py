#!/Library/Frameworks/Python.framework/Versions/3.4/bin python3
import os
import re
import logging
import datetime
import json
import sys
import operator

from ftplib import FTP



def logger(message):
    if os.path.isdir("Logs") == False:
        os.mkdir("Logs")

    log_filename = "Logs/" + datetime.datetime.now().strftime("%Y-%m-%d") + ".log"
    logging.basicConfig(filename=log_filename, level=logging.DEBUG)
    logging.debug(message)


class FileSyncer:
    ftpConnection = None
    ftpUser = ""
    ftpPassword = ""
    ftpServer = ""
    ftpPort = 21
    remoteDirectoryToSync = ""
    localDirectoryToSync = ""
    subScans = 0
    currentWorkingDirectory = ""
    remoteDirectoryTree = {}
    check_for_directory_reg_ex = re.compile("\d")

    def __init__(self, server, user, password, port, remote_directory, local_directory):
        self.ftpServer = server
        self.ftpUser = user
        self.ftpPassword = password
        self.ftpPort = port
        self.remoteDirectoryToSync = remote_directory
        self.localDirectoryToSync = local_directory

    def create_ftp_connection(self):
        logger("Status - Opening FTP Connection at: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        ftp = FTP()
        ftp.connect(self.ftpServer, int(self.ftpPort))
        ftp.login(self.ftpUser, self.ftpPassword)
        return ftp

    @staticmethod
    def close_ftp_connection(obj_ftp):
        logger("Status - Closing FTP Connection at: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        obj_ftp.close()

    @staticmethod
    def check_local_folders():
        list_of_files = []

        if not os.path.isdir("PendingDownloadQueue"):
            os.mkdir("PendingDownloadQueue")

        if os.listdir("PendingDownloadQueue"):
            for f in os.listdir("PendingDownloadQueue"):
                if not f.startswith("."):
                    list_of_files.append(f[:f.rfind(".txt")])

        return list_of_files

    def check_remote_folders(self, obj_ftp):
        list_of_files = []

        try:
            obj_ftp.cwd(self.remoteDirectoryToSync)
            logger("Status - Creating Remote File List")
            obj_ftp.retrlines('NLST', list_of_files.append)

        except Exception as resp:  #TODO: add more cases here
            if str(resp) == "550 No files found":
                logger("Error - No files in this directory -- 550 No files found, " + self.remoteDirectoryToSync)
            else:
                raise

        return list_of_files

    def find_missing_folders(self, local_list, remote_list):
        return [i for i in remote_list if i not in local_list]

    def create_local_directory(self, folder_to_create):
        try:
            if not os.path.isdir(self.localDirectoryToSync + "/" + folder_to_create):
                os.mkdir(self.localDirectoryToSync + "/" + folder_to_create)
            else:
                logger("Status - Directory: " + self.localDirectoryToSync + "/" + folder_to_create
                       + " already exists.\n")

        except Exception as e:
            logger("Error - creating local directory: " + str(e))

    def get_directory_structure(self, obj_ftp, file_to_scan):
        logger("Status - Checking: " + file_to_scan + " for files and folders")

        directory_directories = []
        directory_files = []
        files = []
        child_items = {}

        try:
            obj_ftp.cwd(self.remoteDirectoryToSync + "/" + file_to_scan)
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
            # self.remoteDirectoryTree[obj_ftp.pwd()]["Files"]

            self.remoteDirectoryTree[obj_ftp.pwd()] = directory_files

        except Exception as e:
            logger("Error - An error has occurred checking for child items: " + str(e))

        if directory_directories:
            for dir in directory_directories:
                self.get_directory_structure(obj_ftp, file_to_scan + "/" + dir)

        child_items["Files"] = self.remoteDirectoryTree
        # child_items["Files"][self.remoteDirectoryToSync + "/" + file_to_scan] = directory_files

        return child_items

    def find_folder_files(self, obj_ftp, directory_tree, current_directory, directory_files):

        directory_tree["Files"][current_directory] = directory_files

        return directory_tree
        # child_items["Files"][directory] = directory_files

    def append_download_queue(self, obj_ftp, list_of_remote_files):
        try:
            if not os.path.isdir("PendingDownloadQueue"):
                os.mkdir("PendingDownloadQueue")

            try:
                for singleFile in list_of_remote_files:
                    self.remoteDirectoryTree = {}
                    directory = {}
                    # directory[self.remoteDirectoryToSync + "/" + singleFile] = self.get_directory_structure(obj_ftp, singleFile)

                    with open("PendingDownloadQueue/" + singleFile + ".txt", "w") as f:
                        f.write(json.dumps(self.get_directory_structure(obj_ftp, singleFile), separators=(',', ':'), indent=4))

                self.close_ftp_connection(obj_ftp)

            except Exception as e:
                logger("Error - Unable to write datafile: " + str(e))

        except Exception as e:
            logger("Error - Unable to create download queue folder: " + str(e))

def init():
    ftp_connection = FileSyncer(os.environ["FtpSyncServer"], os.environ["FtpSyncUser"], os.environ["FtpSyncPassword"], os.environ["FtpSyncPort"], os.environ["FtpSyncRemoteDirectory"], os.environ["FtpSyncLocalDirectory"])
    obj_ftp = ftp_connection.create_ftp_connection()
    list_of_local_folders = ftp_connection.check_local_folders()
    list_of_remote_folders = ftp_connection.check_remote_folders(obj_ftp)
    missing_files = ftp_connection.find_missing_folders(list_of_local_folders, list_of_remote_folders)
    ftp_connection.append_download_queue(obj_ftp, missing_files)

init()