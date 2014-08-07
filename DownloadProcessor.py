#!/Library/Frameworks/Python.framework/Versions/3.4/bin python3

import json
import shutil
import os
import sys

from ftpSync import FileSyncer


class DownloadProcessor():
    timeOut = 60 * 60
    DownloadQueue = ""
    ftpSync = None

    def __init__(self, localDownloadQueue):
        self.DownloadQueue = localDownloadQueue
        self.move_file_into_processing()
        self.ftpSync = FileSyncer(os.environ["FtpSyncServer"], os.environ["FtpSyncUser"], os.environ["FtpSyncPassword"], os.environ["FtpSyncPort"], os.environ["FtpSyncRemoteDirectory"], os.environ["FtpSyncLocalDirectory"])


    def move_file_into_processing(self):
        if not os.path.isdir("ProcessingFiles"):
            os.mkdir("ProcessingFiles")

        files_to_process = [f for f in os.listdir("PendingDownloadQueue") if f.endswith(".txt")]

        if files_to_process:
            try:
                shutil.move("PendingDownloadQueue/" + files_to_process[0], "ProcessingFiles")
                self.process_download_file(files_to_process[0])
            except OSError as e:
                print("Error - Unable to move: " + files_to_process[0] + " into queue.")
                try:
                    self.move_file_into_failed(files_to_process[0])
                except OSError as e:
                    print("Error - Unable to move failed file: " + files_to_process[0] + " into failed queue.")
            finally:
                self.move_file_into_processing()

    def move_file_into_failed(self, failed_file):
        if not os.path.isdir("FailedFiles"):
            os.mkdir("FailedFiles")
        try:
            shutil.move("PendingDownloadQueue/" + failed_file, "FailedFiles")

        except OSError as e:
            print("Error moving: " + failed_file + " into failed folder.")

    def map_download_directories(self, parent_directory, mapped_directory_data=""):
        os.mkdir(os.environ["FtpSyncLocalDirectory"] + "/" + parent_directory)

        if mapped_directory_data:
            for directory in mapped_directory_data:
                os.mkdir(os.environ["FtpSyncLocalDirectory"] + parent_directory + "/" + directory)

    def process_download_file(self, file_to_process):
        with open("ProcessingFiles/" + file_to_process, "r") as download_file:
            try:
                download_data = json.loads(download_file.read())
                for f in download_data["Files"]:
                    self.map_download_directories(file_to_process.replace(".txt", ""), f)
            except Exception as e:
                print("Error - Unable to download file: " + str(download_file) + ", " + str(e))
                # for fi in download_data[f]:
                #     #we need to create all the random directories
                #     if fi == "Directories":
                #

                        #self.map_download_directories(f.replace(str(),  ""), fi)
                    #we need to download all the random files into the appropriate directories

                # objFtp.sendcmd("TYPE i")
                # logger("Status - Downloading file: " + fileToDownload + " " + str(objFtp.size(fileToDownload) / 1024 / 1024) + "MB\n")
                # file = open(fileToDownload, 'wb')
                # objFtp.retrbinary('RETR '+ fileToDownload, file.write)
                # file.close()
                # logger("Status - Download successful: " + fileToDownload)
                # self.moveFile(fileToDownload, destinationFolder)

processor = DownloadProcessor("/Users/jwisdom/Dev/Workspace/GitRepos/PendingDownloadQueue")