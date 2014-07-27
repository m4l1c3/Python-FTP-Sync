import os
import subprocess
import re
import shutil
import logging
import datetime

from ftplib import FTP
#from termcolor import colored

def init():
    listOfLocalFiles = checkLocalFiles(os.environ["FtpSyncLocalDirectory"])
    listOfRemoteFiles = checkRemoteFiles(os.environ["FtpSyncServer"], os.environ["FtpSyncUser"], os.environ["FtpSyncPassword"], os.environ["FtpSyncPort"], os.environ["FtpSyncRemoteDirectory"])
    localMissingFiles = findMissingFiles(listOfLocalFiles, listOfRemoteFiles)

    downloadMissingFiles(os.environ["FtpSyncServer"], os.environ["FtpSyncUser"], os.environ["FtpSyncPassword"], os.environ["FtpSyncPort"], localMissingFiles, os.environ["FtpSyncRemoteDirectory"], os.environ["FtpSyncLocalDirectory"])
    cleanupDownloadsFolder(os.environ["FtpSyncLocalDirectory"])

# def setupEnvironmentVariables():
#     bashCommands = []

#     ftpUser = raw_input("What is your FTP user name? ")
#     bashCommands.append("export FtpSyncUser=" + ftpUser)

#     ftpServer = raw_input("What is your FTP server? ")
#     bashCommands.append("export FtpSyncServer=" + ftpServer)

#     ftpPassword = raw_input("What is your FTP password? ")
#     bashCommands.append("export FtpSyncPassword=" + ftpPassword)

#     ftpPort = raw_input("What is the FTP port? ")
#     bashCommands.append("export FtpSyncPort=" + ftpPort)

#     remoteDirectoryToSync = raw_input("What remote directory would you like to sync? ")
#     bashCommands.append("export FtpSyncRemoteDirectory=" + remoteDirectoryToSync)

#     localDirectoryToSync = raw_input("What local direcory would you like to sync? ")
#     bashCommands.append("export FtpSyncLocalDirectory=" + localDirectoryToSync)
 
#     for command in bashCommands:
#         process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
#         output = process.communicate()[0]

#     print colored("Environment variables created", "red")


class FileSyncer:
    ftpConnection = None
    ftpUser = ""
    ftpPassword = ""
    ftpServer = ""
    ftpPort = 21
    remoteDirectoryToSync = ""
    localDirectoryToSync = ""

    def __init__(self, server, user, password, port, remoteDirectory, localDirectory):
        self.ftpServer = server
        self.ftpUser = user
        self.ftpPassword = password
        self.ftpPort = port
        self.remoteDirectoryToSync = remoteDirectory
        self.localDirectoryToSync = localDirectory
        self.ftpConnection = self.createFtpConnection()
        createFtpConnection()

    def createFtpConnection():
        logger("Opening FTP Connection at: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.ftpConnection = FTP()
        self.ftpConnection.connect(self.ftpServer, self.ftpPort)
        self.ftpConnection.login(self.ftpUser, self.ftpPassword)

    def closeFtpConnection():
        print colored("Closing FTP Connection", "green")
        self.ftpConnection.close()

    def checkLocalFiles():
        directories = [d for d in os.listdir(self.localDirectoryToSync) if os.path.isdir(os.path.join(self.localDirectoryToSync, d))]
        dirs = []
        for d in directories:
            dirs.append(d)

        return dirs

    def iterateThroughDirectory():
        directories = set(folder for folder, subfolders, files in os.walk(self.localDirectoryToSync) for file_ in files if os.path.splitext(file_)[1] == '.rar')
        
        for dir in directories:
            os.chdir(os.path.realpath(dir))
            bashExtractCommand = "unrar x " + os.getcwd().replace(" ", "\ ") + "/*.rar"
            bashRemoveCommand = "rm -rf " + os.getcwd().replace(" ", "\ ") + "/*.r*"
            logger("Running: " + bashExtractCommand)
            process = subprocess.Popen(bashExtractCommand, shell=True, stdout=subprocess.PIPE)
            output = process.communicate()[0]
        
        for dir in directories:    
            logger("Removing: rar archives from: " + os.getcwd().replace(" ", "\ "))
            process = subprocess.Popen(bashRemoveCommand, shell=True, stdout=subprocess.PIPE)
            output = process.communicate()[0]

    def cleanupDownloadsFolder(downloadsFolder):
        iterateThroughDirectory(downloadsFolder)

    def checkRemoteFiles():
        listOfFiles = []
        
        self.ftpConnection = self.createFtpConnection()
        self.ftpConnection.cwd(self.remoteDirectoryToSync)
        
        logger("Creating Remote File List:")
        
        try:
            files = self.ftpConnection.nlst()
        except ftplib.error_perm, resp:
            if str(resp) == "550 No files found":
                logger("No files in this directory -- 550 No files found")
            else:
                raise

        for f in files:
            logger("Adding remote file: " + f)
            listOfFiles.append(f)
        
        logger("Closing FTP Connection")
        self.closeFtpConnection()

        return listOfFiles

    def fileDownload(fileName, destination):
        logger("Downloading file: " + fileName + "\n")
        file = open(fileName, 'wb')
        
        self.ftpConnection.retrbinary('RETR '+ fileName, file.write)
        file.close()

        logger("Moving downloaded file: " + fileName + " to: " + destination + "/" + fileName + "\n")
        shutil.move(fileName, destination + "/" + fileName)

    def findMissingFiles(localList, remoteList):
        return [i for i in remoteList if i not in localList]

    def logger(message):
        if(os.path.isdir("Logs") == False):
            os.mkdir("Logs")

        LOG_FILENAME = "Logs/" + datetime.datetime.now().strftime("%Y-%m-%d") + ".log"
        logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)
        logging.debug(message)



def ftpConnect(server, user, password, port):
    logger("Opening FTP Connection at: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    ftp = FTP()
    ftp.connect(server, port)
    ftp.login(user, password)
    return ftp

def checkRemoteFiles(server, user, password, port, remoteFolder):
    listOfFiles = []
    ftp = ftpConnect(server, user, password, port)
    ftp.cwd(remoteFolder)
    
    logger("Create Remote File List:")
    
    try:
        files = ftp.nlst()
    except ftplib.error_perm, resp:
        if str(resp) == "550 No files found":
            logger("No files in this directory -- 550 No files found")
        else:
            raise

    for f in files:
        logger("Adding remote file: " + f)
        listOfFiles.append(f)
    
    logger("Closing FTP Connection")
    ftp.close()
    return listOfFiles


def fileDownload(ftpConnection, fileName, destination):
    try:
        logger("Downloading file: " + fileName)
        file = open(fileName, 'wb')
        
        ftpConnection.retrbinary('RETR '+ fileName, file.write)
        file.close()

        logger("Moving downloaded file: " + fileName + " to: " + destination + "/" + fileName)
        shutil.move(fileName, destination + "/" + fileName)
    except Exception as e:
        logger(e)

def downloadMissingFiles(server, user, password, port, missingFiles, sourceFolder, destinationFolder):
    logger("Beginning Downloads at: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + "\n")
    ftp = ftpConnect(server, user, password, port)
    ftp.cwd(sourceFolder)
    
    for f in missingFiles:
        ftp.cwd(sourceFolder + "/" + f)
        filenames = []
        ftp.retrlines('NLST', filenames.append)

        if(os.path.isdir(destinationFolder + "/" + f) == False):
            os.mkdir(destinationFolder + "/" + f)
        else:
            logger("Unable to create directory: " + destinationFolder + "/" + f + " already exists.")

        for filename in filenames:
            allowedRegEx = re.compile("\.(rar|iso|zip|z[0-9]{2}|r[0-9]{2}|s[0-9]{2})$")
            disallowedRegEx = re.compile("\.(nfo|sfv|mp4|avi|mkv)$")

            if(allowedRegEx.search(filename) != None): # the file we're on is not a directory, let's download the file
                local_filename = os.path.join(destinationFolder + "/" + f, filename)
                logger("Attempting To Download: " + local_filename)
                
                if(os.path.exists(local_filename) == False):
                    fileDownload(ftp, filename, destinationFolder + "/" + f)
                else:
                    #TODO: add logic to compare remote/local files and delete or move on, log which happens
                    logger("Unable to download file: " + local_filename + " already exists.")
            elif(disallowedRegEx.search(filename)): #not an allowed download, skip this round
                continue
            else: #we need to create another directory
                subfiles = []
                if(os.path.isdir(destinationFolder + "/" + f + "/" + filename)):
                    logger("Unable to create directory: " + destinationFolder + "/" + f + "/" + filename + " directory already exists.")
                else:
                    os.mkdir(destinationFolder + "/" + f + "/" + filename)
                    logger("Attempting to create: " + destinationFolder + "/" + f + "/" + filename)
                    ftp.cwd(sourceFolder + "/" + f + "/" + filename)
                    ftp.retrlines('NLST', subfiles.append)
                    for subfile in subfiles:
                        if(allowedRegEx.search(subfile)):
                            sub_local_filename = os.path.join(destinationFolder + "/" + f + "/" + filename, subfile)
                            logger("Attempting To Download: " + sub_local_filename)
                            
                            if(os.path.exists(sub_local_filename) == False):
                                fileDownload(ftp, sub_local_filename, destinationFolder + "/" + f)

                            else:
                                logger("Unable to download file: " + sub_local_filename + " already exists.")


    logger("Closing FTP Connection at: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    ftp.close()

def iterateThroughDirectory(directory):
    directories = set(folder for folder, subfolders, files in os.walk(directory) for file_ in files if os.path.splitext(file_)[1] == '.rar')
    
    for dir in directories:
        os.chdir(os.path.realpath(dir))
        bashExtractCommand = "unrar x " + os.getcwd().replace(" ", "\ ") + "/*.rar"
        bashRemoveCommand = "rm -rf " + os.getcwd().replace(" ", "\ ") + "/*.r*"
        logger("Running: " + bashExtractCommand)
        process = subprocess.Popen(bashExtractCommand, shell=True, stdout=subprocess.PIPE)
        output = process.communicate()[0]
    
    for dir in directories:    
        logger("Removing: rar archives from: " + os.getcwd().replace(" ", "\ "))
        process = subprocess.Popen(bashRemoveCommand, shell=True, stdout=subprocess.PIPE)
        output = process.communicate()[0]



def cleanupDownloadsFolder(downloadsFolder):
    iterateThroughDirectory(downloadsFolder)

def checkLocalFiles(localPath):
    directories = [d for d in os.listdir(localPath) if os.path.isdir(os.path.join(localPath, d))]
    dirs = []
    for d in directories:
        dirs.append(d)

    return dirs

def findMissingFiles(localList, remoteList):
    return [i for i in remoteList if i not in localList]

def logger(message):
    if(os.path.isdir("Logs") == False):
        os.mkdir("Logs")

    LOG_FILENAME = "Logs/" + datetime.datetime.now().strftime("%Y-%m-%d") + ".log"
    logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)
    logging.debug(message)

init()