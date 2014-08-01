import time
import FtpSync

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
	ThreadManager = ThreadManager(10)

	def __init__(self, localDownloadQueue):
		self.DownloadQueue = localDownloadQueue
		self.DownloadFolderAndFiles()

	def CreateThread(self):
		self.ThreadManager.CreateThread(thread)

	def DownloadFolderAndFiles(self):
		return

	def ProcessDownloadFile(self, fileToProcess):
		return

