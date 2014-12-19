import os
import imp
import zipfile
import re
import tarfile

from Base import Base
from TarExtractor import TarArchive
from RarExtractor import RarArchive
from ZipExtractor import ZipArchive
rar_file = imp.load_source('rarfile', 'rarfile/rarfile.py')


class Extractor(Base):
    source_path = ""
    destination_path = ""

    rar_regex = re.compile("\.(rar)")

    def __init__(self, destination_path, source_path):
        Base.__init__(self)
        self.destination_path = destination_path
        self.source_path = source_path

    def extract(self):
        try:
            os.chdir(self.source_path)
            for f in os.listdir(self.source_path):
                if self.is_rar_archive(f):
                    RarArchive(self.source_path, self.destination_path, sorted(os.listdir(self.source_path))[0])
                elif self.is_zip_archive(f):
                    ZipArchive(self.source_path, self.destination_path, sorted(os.listdir(self.source_path))[0])
                elif self.is_tar_archive(f):
                    TarArchive(self.source_path, self.destination_path, sorted(os.listdir(self.source_path))[0])
        except Exception as e:
            print("Error - unable to determine archive type: " + str(e))

    def is_rar_archive(self, target_file_name):
        if not self.rar_regex.search(target_file_name):
            return False
        else:
            return True

    def is_tar_archive(self, target_file_name):
        if not tarfile.is_tarfile(target_file_name):
            return False
        else:
            return True