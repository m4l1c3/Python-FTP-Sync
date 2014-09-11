#!/Library/Frameworks/Python.framework/Versions/3.4/bin python3

import json
import shutil
import os

from ftpSync import FileSyncer
from Base import Base
from Download import Download
from Extractor import Extractor
from Cleaner import Cleaner

class DownloadProcessor(Base):
    timeOut = 60 * 60
    download_queue = ""
    ftp_sync = None

    def __init__(self, localDownloadQueue):
        Base.__init__(self)
        self.download_queue = localDownloadQueue
        self.ftp_sync = FileSyncer()
        self.move_file_into_processing()

    def move_file_into_processing(self):
        if not os.path.isdir("ProcessingFiles"):
            os.mkdir("ProcessingFiles")

        processing_files = [f for f in os.listdir("ProcessingFiles") if f.endswith(".txt")]
        files_to_process = [f for f in os.listdir(self.download_queue) if f.endswith(".txt")]

        for single_file in processing_files:
            try:
                self.process_download_file(single_file)
            except Exception as e:
                print("Error - Unable to process: " + single_file + " " + str(e))
            finally:
                os.remove("ProcessingFiles" + self.directory_separator + single_file)

        for single_file in files_to_process:
            try:
                shutil.move("PendingDownloadQueue" + self.directory_separator + single_file, "ProcessingFiles")
                self.process_download_file(single_file)
            except OSError as e:
                print("Error - Unable to move: " + single_file + " into queue.  " + str(e))
                self.move_file_into_failed(single_file)
            finally:
                os.remove("ProcessingFiles" + self.directory_separator + single_file)

    def move_file_into_failed(self, failed_file):
        if not os.path.isdir("FailedFiles"):
            os.mkdir("FailedFiles")
        try:
            shutil.move("PendingDownloadQueue" + self.directory_separator + failed_file, "FailedFiles")
        except OSError as e:
            print("Error moving: " + failed_file + " into failed folder.")

    def map_download_directories(self, parent_directory, mapped_directory_data=""):
        if not os.path.isdir(self.local_directory_to_sync + self.directory_separator + parent_directory):
            try:
                os.mkdir(self.local_directory_to_sync + self.directory_separator + parent_directory)
            except OSError as e:
                print("Unable to create directory: " + self.local_directory_to_sync +
                        self.directory_separator + parent_directory + " " + str(e))

    def process_download_file(self, file_to_process):
        with open("ProcessingFiles" + self.directory_separator + file_to_process, "r") as download_file:
            try:
                download_data = json.loads(download_file.read())
                for f in sorted(download_data["Files"]):
                    self.map_download_directories(f.replace(self.remote_directory_to_sync + "/", ""))

                for f in download_data["Files"]:
                    Download(self.ftp_sync, f, download_data["Files"][f])
                    Extractor(f.replace(self.remote_directory_to_sync, self.local_directory_to_sync), f.replace(self.remote_directory_to_sync, self.local_directory_to_sync))

            except Exception as e:
                print("Error - Unable to download file: " + str(download_file) + ", " + str(e))



processor = DownloadProcessor("/Users/jwisdom/Dev/Workspace/GitRepos/Python-FTP-Sync/PendingDownloadQueue")
