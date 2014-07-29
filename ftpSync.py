import os
import subprocess
import re
import shutil
import logging
import datetime

from ftplib import FTP



def logger(message):
    if(os.path.isdir("Logs") == False):
        os.mkdir("Logs")

    LOG_FILENAME = "Logs/" + datetime.datetime.now().strftime("%Y-%m-%d") + ".log"
    logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)
    logging.debug(message)

class DirEntry: # found at: http://www.java2s.com/Tutorial/Python/0420__Network/nlstwithfiledirectorydetectionexample.htm
    def __init__(self, filename, ftpobj, startingdir = None):
        self.filename = filename
        if startingdir == None:
            startingdir = ftpobj.pwd()
        try:
            ftpobj.cwd(filename)
            self.filetype = 'd'
            ftpobj.cwd(startingdir)
        except ftplib.error_perm:
            self.filetype = '-'
        
    def gettype(self):
        return self.filetype

    def getfilename(self):
        return self.filename

class FileSyncer:
    ftpConnection = None
    ftpUser = ""
    ftpPassword = ""
    ftpServer = ""
    ftpPort = 21
    remoteDirectoryToSync = ""
    localDirectoryToSync = ""
    subScans = 0

    def __init__(self, server, user, password, port, remoteDirectory, localDirectory):
        self.ftpServer = server
        self.ftpUser = user
        self.ftpPassword = password
        self.ftpPort = port
        self.remoteDirectoryToSync = remoteDirectory
        self.localDirectoryToSync = localDirectory
        # self.ftpConnection = self.createFtpConnection()

    def createFtpConnection(self):
        logger("Opening FTP Connection at: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        ftp = FTP()
        ftp.connect(self.ftpServer, int(self.ftpPort))
        ftp.login(self.ftpUser, self.ftpPassword)
        return ftp

    def closeFtpConnection(self, ftpConnection):
        logger("Closing FTP Connection")
        ftpConnection.close()

    def findMissingFiles(self, localList, remoteList):
        return [i for i in remoteList if i not in localList]

    def checkLocalFiles(self):
        return [d for d in os.listdir(self.localDirectoryToSync) if os.path.isdir(os.path.join(self.localDirectoryToSync, d))]

    def moveFile(self, fileName, destination):
        try:
            logger("Moving downloaded file: " + fileName + " to: " + destination + "/" + fileName + "\n")
            shutil.move(fileName, self.localDirectoryToSync + "/" + destination + "/" + fileName)

        except Exception as e:
            logger("Exception: " + str(e) + "\n")

    def createLocalDirectory(self, folderToCreate):
        try:
            if(os.path.isdir(self.localDirectoryToSync + "/" + folderToCreate) == False):
                os.mkdir(self.localDirectoryToSync + "/" + folderToCreate)
            else:
                logger("Unable to create directory: " + self.localDirectoryToSync + "/" + folderToCreate + " already exists.\n")
        except Exception as e:
            logger("Error creating local directory: " + e)

    def checkRemoteFiles(self):
        listOfFiles = []

        try:
            ftp = self.createFtpConnection()
            ftp.cwd(self.remoteDirectoryToSync)
            
            logger("Create Remote File List:\n")
            listOfFiles = ftp.retrlines('NLST', fileNames.append)
            self.closeFtpConnection(ftp)
        
        except ftplib.error_perm as resp: #TODO: add more cases here
            if str(resp) == "550 No files found":
                logger("No files in this directory -- 550 No files found" + "\n")
            else:
                raise
        
        return listOfFiles

    def checkForDirectories(self, objFtp, fileToScan):
        hasSubDirectories = False
        for singleFile in fileToScan:
            
            if(self.isDirectory(objFtp, singleFile) == True): #We have a sub directory
                # self.createLocalDirectory(singleFile)
                hasSubDirectories = True
            else: #We do not have a sub directory
                self.createLocalDirectory(destinationFolder)
                self.downloadFile(objFtp, f, singleFile)

        return hasSubDirectories

    def downloadFolder(self, objFtp, folderToScan):
        fileNames = []
        
        try:
            self.createLocalDirectory(folderToScan)
            objFtp.cwd(self.remoteDirectoryToSync + "/" + folderToScan)
            objFtp.retrlines('NLST', fileNames.append)
            
            for f in fileNames:

                if(self.isDirectory(objFtp, f)):
                    self.subScans += 1
                    if(self.checkForDirectories(objFtp, f) == True):
                        print("i am here too downloading a # of scans: " + str(self.subScans))
                        self.downloadFolder(objFtp, f)
                    else:
                        print("i am here again doing something else")
                else:
                    print("i am here downloading a single file")
                    self.downloadFile(objFtp, folderToScan, f)
        
        except Exception as e:
            logger("Folder scan exception: " + str(e))

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
        

    def isDirectory(self, objFtp, fileToCheck):
        try:
            objFtp.cwd(self.remoteDirectoryToSync + "/" + fileToCheck)
            isASubDirectory = True

        except Exception as e:
            isASubDirectory = False

        return isASubDirectory

    def downloadMissingFiles(self, missingFiles):
        logger("Beginning Downloads at: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + "\n")
        try:
            ftp = self.createFtpConnection()
            ftp.cwd(self.remoteDirectoryToSync)

            for f in missingFiles:
                fileNames = []
                ftp.cwd(self.remoteDirectoryToSync + "/" + f)
                ftp.retrlines('NLST', fileNames.append)
                self.downloadFolder(ftp, f)
        except Exception as e:
            logger("Exception: " + str(e))

        self.closeFtpConnection(ftp)

def init():
    FtpConnection = FileSyncer(os.environ["FtpSyncServer"], os.environ["FtpSyncUser"], os.environ["FtpSyncPassword"], os.environ["FtpSyncPort"], os.environ["FtpSyncRemoteDirectory"], os.environ["FtpSyncLocalDirectory"])
    listOfLocalFolders = FtpConnection.checkLocalFiles()
    listOfRemoteFolders = FtpConnection.checkRemoteFiles()
    localMissingFiles = FtpConnection.findMissingFiles(listOfLocalFolders, listOfRemoteFolders)
    
    FtpConnection.downloadMissingFiles(localMissingFiles)
    # cleanupDownloadsFolder(os.environ["FtpSyncLocalDirectory"])

init()