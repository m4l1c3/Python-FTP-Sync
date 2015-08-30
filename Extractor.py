import os
import imp
import zipfile
import re
import tarfile

from Base import Base
from TarExtractor import TarExtractor
from RarExtractor import RarExtractor
from ZipExtractor import ZipExtractor
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
                try:
                    if os.path.isdir(self.extraction_path +
                                self.directory_separator + folder):
                        Logger("Looping - folder: " + folder)
                        for file_to_check in os.listdir(self.extraction_path +
                                self.directory_separator + folder):
                            full_path = self.extraction_path + self.directory_separator + folder + self.directory_separator \
                                        + file_to_check
                            if not os.path.isdir(full_path) and not self.acceptable_file_types.search(file_to_check) \
                                and not self.disallowed_file_types.search(file_to_check)  :
                                self.check_for_extractable_item(folder, file_to_check)
                            elif os.path.isdir(file_to_check):
                                for sub_folder_file_to_check in os.listdir(full_path):
                                    if not os.path.isdir(full_path + self.directory_separator + sub_folder_file_to_check):
                                        self.check_for_extractable_item(folder + self.directory_separator
                                            + file_to_check, sub_folder_file_to_check)
                            else:
                                continue
                    else:
                        continue
                except Exception as exception:
                    Logger("Error - checking archive: " + str(exception))
                    continue
        except Exception as exception:
            Logger("Error - unable to determine archive type: " + str(exception))

    def check_for_extractable_item(self, parent_folder, file_to_check):
        parent_folder_path = self.extraction_path + self.directory_separator + parent_folder
        full_file_path = self.extraction_path + self.directory_separator + parent_folder + self.directory_separator \
                         + file_to_check
        if self.is_rar_archive(full_file_path):
            RarExtractor(parent_folder_path, full_file_path)
            return True
        else:
            if self.is_zip_archive(full_file_path):
                ZipExtractor(parent_folder_path, sorted(os.listdir(parent_folder))[0])
                return True
            if self.is_tar_archive(full_file_path):
                TarExtractor(parent_folder_path, sorted(os.listdir(parent_folder_path))[0])
                return True
        return False

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
