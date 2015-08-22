import os
import imp
import zipfile
import re
import tarfile

from Base import Base
from TarExtractor import TarArchive
from RarExtractor import RarExtractor
from ZipExtractor import ZipArchive
from Logger import Logger
rar_file = imp.load_source('rarfile', 'rarfile/rarfile.py')


class Extractor(Base):
    extraction_path = ""

    rar_regex = re.compile("\.(rar)")

    def __init__(self, extraction_path):
        Base.__init__(self)
        self.extraction_path = extraction_path
        self.extract()

    def extract(self):
        try:
            os.chdir(self.extraction_path)
            for folder in os.listdir(self.extraction_path):
                Logger("Looping - folder: " + folder)

                try:
                    for file_to_check in os.listdir(self.extraction_path +
                            self.directory_separator + folder):
                        if self.is_rar_archive(self.extraction_path +
                                self.directory_separator + folder +
                                self.directory_separator + file_to_check):
                            Logger("Status - UnRar Archive: " +
                                   self.extraction_path +
                                   self.directory_separator +
                                   folder)
                            RarExtractor(self.extraction_path +
                                         self.directory_separator +
                                         folder,
                                         file_to_check)
                        elif self.is_zip_archive(self.extraction_path +
                                self.directory_separator +
                                folder +
                                self.directory_separator +
                                file_to_check):
                            Logger("Status - Attempting to extract ZIP Archive in: " + self.extraction_path)
                            ZipArchive(self.extraction_path + self.directory_separator + folder,
                                    sorted(os.listdir(self.extraction_path + self.directory_separator +
                                                      file_to_check))[0])
                        elif self.is_tar_archive(self.extraction_path + self.directory_separator + folder + 
                                self.directory_separator + file_to_check):
                            Logger("Status - Attempting to extract TAR Archive in: " + self.extraction_path)
                            TarArchive(self.extraction_path + self.directory_separator + folder,
                                    sorted(os.listdir(self.extraction_path + self.directory_separator +
                                                      file_to_check))[0])
                        else:
                            continue
                except Exception as exception:
                    Logger("Error - checking archive: " + str(exception))
                    continue
        except Exception as exception:
            Logger("Error - unable to determine archive type: " + str(exception))
    
    @staticmethod
    def is_zip_archive(target_file_name):
        if not zipfile.is_zipfile(target_file_name):
            return False
        else:
            return True

    def is_rar_archive(self, target_file_name):
        if not self.rar_regex.search(target_file_name):
            return False
        else:
            return True
    
    @staticmethod
    def is_tar_archive(target_file_name):
        if not tarfile.is_tarfile(target_file_name):
            return False
        else:
            return True
