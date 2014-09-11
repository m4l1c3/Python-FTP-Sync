import platform
import os


class Base():
    current_os = ""
    directory_separator = ""
    ftp_user = ""
    ftp_password = ""
    ftp_server = ""
    ftp_port = 21
    remote_directory_to_sync = ""
    local_directory_to_sync = ""
    # logger = Logger("Initializing Base")

    def __init__(self):
        self.current_os = platform.system()
        self.set_directory_separator()
        self.ftp_server = os.environ["FtpSyncServer"]
        self.ftp_user = os.environ["FtpSyncUser"]
        self.ftp_password = os.environ["FtpSyncPassword"]
        self.ftp_port = os.environ["FtpSyncPort"]
        self.remote_directory_to_sync = os.environ["FtpSyncRemoteDirectory"]
        self.local_directory_to_sync = os.environ["FtpSyncLocalDirectory"]


    def set_directory_separator(self):
        if self.is_windows():
            self.directory_separator = "\\"
        elif self.is_linux() or self.is_osx():
            self.directory_separator = "/"
        else:
            return

    def is_windows(self):
        if platform.system() is "Windows":
            return True
        else:
            return False

    def is_linux(self):
        if not platform.system() == "Linux":
            return True
        else:
            return False

    def is_osx(self):
        if not platform.system() == "Darwin":
            return True
        else:
            return False