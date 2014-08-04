#!/Library/Frameworks/Python.framework/Versions/3.4/bin python3

import time, json, shutil, os

from FtpSync import FileSyncer

class ThreadManager():
	threads = []
	
	def __init__(self, threadLimit):
		self.threadLimit = threadLimit

	def CreateThread(self, thread):
		if(len(self.threads) < self.threadLimit):
			self.threads.append(thread)


class DownloadProcessor():
	timeOut = 60 * 60
	DownloadQueue = ""
	ftpSync = None

	def __init__(self, localDownloadQueue):
		self.DownloadQueue = localDownloadQueue
		self.DownloadFolderAndFiles()
		self.ftpSync = FtpSync()

	def CreateThread(self):
		self.ThreadManager.CreateThread(thread)

	def MoveFilesIntoProcessing(self):
		if not os.path.isdir("ProcessingFiles"):
			os.mkdir("ProcessingFiles")

		if os.listdir("PendingDownloadQueue"):
			shutil.move(os.listdir("PendingDownloadQueue")[0], "ProcessingFiles")

	def DownloadFolderAndFiles(self):
		for f in os.listdir("PendingDownloadQueue"):
			self.MoveFilesIntoProcessing()

	def ProcessDownloadFile(self, fileToProcess):
		try:
			with open("PendingDownloadQueue/" + fileToProcess + ".txt", "r") as downloadFile:
				downloadData = json.loads(downloadFile.read())
				print(downloadData)

        #     objFtp.sendcmd("TYPE i")
        #     logger("Status - Downloading file: " + fileToDownload + " " + str(objFtp.size(fileToDownload) / 1024 / 1024) + "MB\n")
        #     file = open(fileToDownload, 'wb')
        #     objFtp.retrbinary('RETR '+ fileToDownload, file.write)
        #     file.close()
        #     logger("Status - Download successful: " + fileToDownload)
        #     self.moveFile(fileToDownload, destinationFolder)

		except Exception as e:
			logger("Error - Failed file download file: " + fileToDownload)

