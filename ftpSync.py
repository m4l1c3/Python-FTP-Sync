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

    def createFtpConnection(self):
        logger("Opening FTP Connection at: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        ftp = FTP()
        ftp.connect(self.ftpServer, int(self.ftpPort))
        ftp.login(self.ftpUser, self.ftpPassword)
        return ftp

    def checkLocalFiles(self):
        listOfFiles = []
        
        try:
            listOfFiles = [d for d in os.listdir(os.environ["FtpSyncLocalDirectory"]) if os.path.isdir(os.environ["FtpSyncLocalDirectory"])]

        except Exception as e:
            logger("Error finding local files at " + os.environ["FtpSyncLocalDirectory"] + ": " + e)

        return listOfFiles
    
    def changeWorkingDirectory(self, objFtp, directoryToChangeTo):
        self.currentWorkingDirectory = directoryToChangeTo
        objFtp.cwd(directoryToChangeTo)

    def checkRemoteFiles(self):
        listOfFiles = []

        try:
            ftp = self.createFtpConnection()
            self.changeWorkingDirectory(ftp, self.remoteDirectoryToSync)
            logger("Create Remote File List:\n")
            ftp.retrlines('NLST', listOfFiles.append)
            ftp.close()

        except Exception as resp: #TODO: add more cases here
            if str(resp) == "550 No files found":
                logger("Error: No files in this directory -- 550 No files found, " + self.remoteDirectoryToSync)
            else:
                raise
        
        return listOfFiles

    def isDirectory(self, objFtp, fileToCheck):
        try:
            objFtp.cwd(self.remoteDirectoryToSync + "/" + fileToCheck)
            isASubDirectory = True

        except Exception as e:
            isASubDirectory = False

        return isASubDirectory

    def checkForDirectories(self, objFtp, fileToScan):
        hasSubDirectories = False
        for singleFile in fileToScan:
            if(self.isDirectory(objFtp, singleFile) == True): #We have a sub directory
                hasSubDirectories = True

        return hasSubDirectories

    def findMissingFiles(self, localList, remoteList):
        return [i for i in remoteList if i not in localList]

    def downloadFile(self, objFtp, destinationFolder, fileToDownload):
        try:
            objFtp.sendcmd("TYPE i")
            logger("Downloading file: " + fileToDownload + " " + str(objFtp.size(fileToDownload) / 1024 / 1024) + "MB\n")
            file = open(fileToDownload, 'wb')
            objFtp.retrbinary('RETR '+ fileToDownload, file.write)
            file.close()
            self.moveFile(fileToDownload, destinationFolder)

        except Exception as e:
            logger("Failed file download:" + fileToDownload)

    def createLocalDirectory(self, folderToCreate):
        try:
            if(os.path.isdir(self.localDirectoryToSync + "/" + folderToCreate) == False):
                os.mkdir(self.localDirectoryToSync + "/" + folderToCreate)
            else:
                logger("Unable to create directory: " + self.localDirectoryToSync + "/" + folderToCreate + " already exists.\n")

        except Exception as e:
            logger("Error creating local directory: " + e)

    def appendDownloadQueue(self, listOfRemoteFiles):
        try:
            if(os.path.isdir("PendingDownloadQueue") == False):
                os.mkdir("PendingDownloadQueue")

            try:
                for singleFile in listOfRemoteFiles:
                    f = open("PendingDownloadQueue/" + singleFile + ".txt", "w")
                    f.write(json.dumps(singleFile))
                    f.close
            except Exception as e:
                logger("Error - Unable to write datafile: " + str(e))

        except Exception as e:
            logger("Error - Unable to create download queue folder: " + str(e))

        self.appendSingleDownloadFile("True.Blood.S07E02.HDTV.x264-KILLERS.txt", {"Directory": "Blah","File": "blah.txt","File": "blah2.txt"})

    def appendSingleDownloadFile(self, itemToAppend, listOfSubItems):
        try:

            if(os.path.isfile("PendingDownloadQueue/" + itemToAppend)):
                with open("PendingDownloadQueue/" + itemToAppend, "r+") as f:
                    previousContents = json.loads(f.read())
                    additionalContent = ""
                    f.seek(0)
                    
                    for key in listOfSubItems:
                        additionalContent += key + ":" + listOfSubItems[key] + ","
                    # logger(json.dumps(previousContent + "{" + additionalContent + "}", separators=',', ':'))
                    # ['foo', {'bar': ('baz', None, 1.0, 2)}]
                    testContent = {"Parent": itemToAppend, "Files": listOfSubItems}
                    test = json.dumps(testContent, separators=(',', ':'), indent=4)
                    print test
                    test2 = json.loads(test)
                    print test2
                    # f.write(json.dumps(previousContents + additionalContent))
            else:
                logger("Error - Local file: " + itemToAppend + " does not exist, therefore we cannot append it's contents.")
        except Exception as e:
            logger("Error - Appending single file and re-encoding: " + str(e))


def init():
    FtpConnection = FileSyncer(os.environ["FtpSyncServer"], os.environ["FtpSyncUser"], os.environ["FtpSyncPassword"], os.environ["FtpSyncPort"], os.environ["FtpSyncRemoteDirectory"], os.environ["FtpSyncLocalDirectory"])
    listOfLocalFolders = FtpConnection.checkLocalFiles()
    listOfRemoteFolders = FtpConnection.checkRemoteFiles()
    missingFiles = FtpConnection.findMissingFiles(listOfLocalFolders, listOfRemoteFolders)
    FtpConnection.appendDownloadQueue(missingFiles)
    
    # FtpConnection.downloadMissingFiles(localMissingFiles)
    # cleanupDownloadsFolder(os.environ["FtpSyncLocalDirectory"])

init()