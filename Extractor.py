import os
import imp
rar_file = imp.load_source('rarfile', '/rarfile/rarfile.py')

class Extractor:
    source_path = ""
    destination_path = ""

    def __init__(self, destination_path, source_path):
        self.destination_path = destination_path
        self.source_path = source_path

    def Extract(self):
        return