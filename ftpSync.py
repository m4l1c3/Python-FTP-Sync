import os
import subprocess
import re
import shutil
from ftplib import FTP
from termcolor import colored

ftpUser = "jw4102"
ftpPassword = "jw4102"
ftpServer = "frd107.seedstuff.ca"
ftpPort = 32001

remoteDirectoryToSync = "/rtorrent/downloads"
localDirectoryToSync = "/Users/jwisdom/Movies"

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
        cprint("Opening FTP Connection", "green")
        self.ftpConnection = FTP()
        self.ftpConnection.connect(self.ftpServer, self.ftpPort)
        self.ftpConnection.login(self.ftpUser, self.ftpPassword)

    def closeFtpConnection():
        print colored("Closing FTP Connection", "green")
        self.ftpConnection.close()



def ftpConnect(server, user, password, port):
    print colored("Opening FTP Connection", "green")
    ftp = FTP()
    ftp.connect(server, port)
    ftp.login(user, password)
    return ftp

def checkRemoteFiles(server, user, password, port, remoteFolder):
    listOfFiles = []
    ftp = ftpConnect(server, user, password, port)
    ftp.cwd(remoteFolder)
    
    print colored("Create Remote File List:", "green")
    
    try:
        files = ftp.nlst()
    except ftplib.error_perm, resp:
        if str(resp) == "550 No files found":
            print "No files in this directory"
        else:
            raise

    for f in files:
        print "Adding remote file: " + f
        listOfFiles.append(f)
    
    print colored("Closing FTP Connection", "green")
    ftp.close()
    return listOfFiles


def fileDownload(ftpConnection, fileName, destination):
    print colored("Downloading file: " + fileName, "green")
    file = open(fileName, 'wb')
    ftpConnection.retrbinary('RETR '+ fileName, file.write)
    file.close()

    print colored("Moving downloaded file: " + fileName + " to: " + destination + "/" + fileName, "blue")
    shutil.move(fileName, destination + "/" + fileName)
    

def downloadMissingFiles(server, user, password, port, missingFiles, sourceFolder, destinationFolder):
    print "Beginning Downloads"
    ftp = ftpConnect(server, user, password, port)
    ftp.cwd(sourceFolder)
    
    for f in missingFiles:
        ftp.cwd(sourceFolder + "/" + f)
        filenames = []
        ftp.retrlines('NLST', filenames.append)

        if(os.path.isdir(destinationFolder + "/" + f) == False):
            os.mkdir(destinationFolder + "/" + f)
        else:
            print colored("Unable to create directory: " + destinationFolder + "/" + f + " already exists.", "red")

        for filename in filenames:
            allowedRegEx = re.compile("\.(rar|r[0-9]{2}|s[0-9]{2})$")
            disallowedRegEx = re.compile("\.(nfo|mp4|avi|mkv)$")

            if(allowedRegEx.search(filename) != None): # the file we're on is not a directory, let's continue and download the file
                local_filename = os.path.join(destinationFolder + "/" + f, filename)
                print colored("Attempting To Download: " + local_filename, "yellow")
                
                if(os.path.exists(local_filename) == False):
                    fileDownload(ftp, filename, destinationFolder + "/" + f)

                else:
                    print colored("Unable to download file: " + local_filename + " already exists.", "red")
            elif(disallowedRegEx.search(filename)): 
                continue
            else: #we need to create another directory
                subfiles = []
                if(os.path.isdir(destinationFolder + "/" + f + "/" + filename) == False):
                    os.mkdir(destinationFolder + "/" + f + "/" + filename)
                    print "Attempting to create: " + colored(sourceFolder + "/" + f + "/" + filename, "yellow")
                    ftp.cwd(sourceFolder + "/" + f + "/" + filename)
                    ftp.retrlines('NLST', subfiles.append)
                    for subfile in subfiles:
                        if(allowedRegEx.search(subfile)):
                            sub_local_filename = os.path.join(destinationFolder + "/" + f + "/" + filename, subfile)
                            print colored("Attempting To Download: " + sub_local_filename, "yellow")
                            
                            if(os.path.exists(sub_local_filename) == False):
                                fileDownload(ftp, sub_local_filename, destinationFolder + "/" + f)

                            else:
                                print colored("Unable to download file: " + sub_local_filename + " already exists.", "red")
                else:
                    print colored("Unable to create director: " + destinationFolder + "/" + f + "/" + filename + " directory already exists.")


    print colored("Closing FTP Connection", "green")
    ftp.close()

def iterateThroughDirectory(directory):
    directories = set(folder for folder, subfolders, files in os.walk(directory) for file_ in files if os.path.splitext(file_)[1] == '.rar')
    
    for dir in directories:
        os.chdir(os.path.realpath(dir))
        bashExtractCommand = "unrar x " + os.getcwd().replace(" ", "\ ") + "/*.rar"
        bashRemoveCommand = "rm -rf " + os.getcwd().replace(" ", "\ ") + "/*.r*"
        print colored("Running: " + bashExtractCommand, "green")
        process = subprocess.Popen(bashExtractCommand, shell=True, stdout=subprocess.PIPE)
        output = process.communicate()[0]
        print colored(output, "blue")
    
    for dir in directories:    
        print colored("Removing: rar archives from: " + os.getcwd().replace(" ", "\ "), "green")
        process = subprocess.Popen(bashRemoveCommand, shell=True, stdout=subprocess.PIPE)
        output = process.communicate()[0]
        print colored(output, "blue")



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

listOfLocalFiles = checkLocalFiles(localDirectoryToSync)
listOfRemoteFiles = checkRemoteFiles(ftpServer, ftpUser, ftpPassword, ftpPort, remoteDirectoryToSync)
localMissingFiles = findMissingFiles(listOfLocalFiles, listOfRemoteFiles)

downloadMissingFiles(ftpServer, ftpUser, ftpPassword, ftpPort, localMissingFiles, remoteDirectoryToSync, localDirectoryToSync)
cleanupDownloadsFolder(localDirectoryToSync)