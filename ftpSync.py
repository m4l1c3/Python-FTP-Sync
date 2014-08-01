import os, subprocess, re, shutil, logging, datetime, json

from ftplib import FTP

def logger(message):
    if(os.path.isdir("Logs") == False):
        os.mkdir("Logs")

    LOG_FILENAME = "Logs/" + datetime.datetime.now().strftime("%Y-%m-%d") + ".log"
    logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)
    logging.debug(message)

class DirectoryTree:
    directories = {}

    def __init__(self):
        self.directories = {}

class Directory():
    name = "";
    folders = []
    files = []

    def __init__(self, name, files = []):
        self.name = name
        self.files = files

class File():
    name = ""

    def __init__(self, name):
        self.name = name

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

    def __init__(self, server, user, password, port, remoteDirectory, localDirectory):
        self.ftpServer = server
        self.ftpUser = user
        self.ftpPassword = password
        self.ftpPort = port
        self.remoteDirectoryToSync = remoteDirectory
        self.localDirectoryToSync = localDirectory
        self.ftpConnection = self.createFtpConnection()

    def createFtpConnection(self):
        logger("Status - Opening FTP Connection at: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        ftp = FTP()
        ftp.connect(self.ftpServer, int(self.ftpPort))
        ftp.login(self.ftpUser, self.ftpPassword)
        return ftp

    def closeFtpConnection(self, objFtp):
        logger("Status - Closing FTP Connection at: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        objFtp.close()

    def checkLocalFiles(self):
        listOfFiles = []

        if not os.path.isdir("PendingDownloadQueue"):
            os.mkdir("PendingDownloadQueue")
        
        if os.listdir("PendingDownloadQueue"):
            for f in os.listdir("PendingDownloadQueue"):
                listOfFiles.append(f[f.rfind("."):])

        return listOfFiles
    
    def checkRemoteFiles(self):
        listOfFiles = []

        try:
            ftp = self.createFtpConnection()
            ftp.cwd(self.remoteDirectoryToSync)
            logger("Status - Creating Remote File List")
            ftp.retrlines('NLST', listOfFiles.append)

        except Exception as resp: #TODO: add more cases here
            if str(resp) == "550 No files found":
                logger("Error - No files in this directory -- 550 No files found, " + self.remoteDirectoryToSync)
            else:
                raise
        
        return listOfFiles

    def findMissingFiles(self, localList, remoteList):
        return [i for i in remoteList if i not in localList]

    def downloadFile(self, objFtp, destinationFolder, fileToDownload):
        try:
            objFtp.sendcmd("TYPE i")
            logger("Status - Downloading file: " + fileToDownload + " " + str(objFtp.size(fileToDownload) / 1024 / 1024) + "MB\n")
            file = open(fileToDownload, 'wb')
            objFtp.retrbinary('RETR '+ fileToDownload, file.write)
            file.close()
            logger("Status - Download successful: " + fileToDownload)
            self.moveFile(fileToDownload, destinationFolder)

        except Exception as e:
            logger("Error - Failed file download file: " + fileToDownload)

    def createLocalDirectory(self, folderToCreate):
        try:
            if(os.path.isdir(self.localDirectoryToSync + "/" + folderToCreate) == False):
                os.mkdir(self.localDirectoryToSync + "/" + folderToCreate)
            else:
                logger("Status - Directory: " + self.localDirectoryToSync + "/" + folderToCreate + " already exists.\n")

        except Exception as e:
            logger("Error - creating local directory: " + str(e))

    def getChildItems(self, objFtp, fileToScan):
        checkForDirectoryRegEx = re.compile("\d")
        directoryFiles = []
        directoryDirectories = []
        files = []
        childItems = {}

        try:
            objFtp.cwd(self.remoteDirectoryToSync + "/" + fileToScan)
            response = objFtp.retrlines("LIST", files.append)
            
            for f in files:
                index = checkForDirectoryRegEx.search(f)
                fileOrDirectoryName = f[f.rfind(" "):].strip()

                if(int(f[index.start()]) > 1): #we have a directory
                    directoryDirectories.append(fileOrDirectoryName)
                else: #we do not have a directory
                    directoryFiles.append(fileOrDirectoryName)
                    
        except Exception as e:
            logger("Error - An error has occured checking for child items: " + str(e))

        childItems["Directories"] = directoryDirectories
        childItems["Files"] = directoryFiles

        if(childItems["Directories"]):
            for dir in childItems["Directories"]:
                childItems["Files"].append("'" + fileToScan + "/" + dir + "':" + str(self.getChildItems(objFtp, fileToScan + "/" + dir)))

        return childItems

    def appendDownloadQueue(self, listOfRemoteFiles):
        try:
            ftp = self.createFtpConnection()
            
            if(os.path.isdir("PendingDownloadQueue") == False):
                os.mkdir("PendingDownloadQueue")

            try:
                for singleFile in listOfRemoteFiles:
                    directory = {}
                    directory[self.remoteDirectoryToSync + "/" + singleFile] = self.getChildItems(ftp, singleFile)
                    
                    with open("PendingDownloadQueue/" + singleFile + ".txt", "w") as f:
                        f.write(json.dumps(directory, separators=(',', ':'), indent=4))
                    
                self.closeFtpConnection(ftp)

            except Exception as e:
                logger("Error - Unable to write datafile: " + str(e))

        except Exception as e:
            logger("Error - Unable to create download queue folder: " + str(e))

def init():
    FtpConnection = FileSyncer(os.environ["FtpSyncServer"], os.environ["FtpSyncUser"], os.environ["FtpSyncPassword"], os.environ["FtpSyncPort"], os.environ["FtpSyncRemoteDirectory"], os.environ["FtpSyncLocalDirectory"])
    listOfLocalFolders = FtpConnection.checkLocalFiles()
    listOfRemoteFolders = FtpConnection.checkRemoteFiles()
    missingFiles = FtpConnection.findMissingFiles(listOfLocalFolders, listOfRemoteFolders)
    FtpConnection.appendDownloadQueue(missingFiles)

    # FtpConnection.downloadMissingFiles(localMissingFiles)
    # cleanupDownloadsFolder(os.environ["FtpSyncLocalDirectory"])

init()