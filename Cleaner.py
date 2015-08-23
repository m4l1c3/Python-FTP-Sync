import os
import re
import shutil

from Base import Base
from Logger import Logger


class Cleaner(Base):
    path_to_clean = ""
    type_of_removal = ""
    acceptable_parent_directory = re.compile("(Sample)")

    def __init__(self, path_to_clean, acceptable_file_types = ''):
        Base.__init__(self)
        if not acceptable_file_types == '':
            self.acceptable_file_types = acceptable_file_types

        self.path_to_clean = path_to_clean

        if not self.path_to_clean == '':
            try:
                for folder in os.listdir(self.path_to_clean):
                    self.check_file(folder)
            except Exception as e:
                Logger("Error cleaning up - " + str(e))
        else:
            Logger("Error - no path to clean defined.")

    def check_file(self, file_or_folder_to_check):
        try:
            if not (self.disallowed_file_types.search(file_or_folder_to_check)):
                for f in os.listdir(self.path_to_clean + self.directory_separator + file_or_folder_to_check):
                    if not self.is_directory(self.path_to_clean + self.directory_separator + file_or_folder_to_check + self.directory_separator + f):
                        if not self.is_acceptable_file_type(self.path_to_clean + self.directory_separator + file_or_folder_to_check + self.directory_separator + f):
                            try:
                                self.remove(self.path_to_clean + self.directory_separator + file_or_folder_to_check + self.directory_separator + f)
                            except Exception as e:
                                Logger("Error - Unable to remove file: " + self.path_to_clean + self.directory_separator + file_or_folder_to_check + self.directory_separator + f)
                        else:
                            continue
                    else:
                        self.check_file(file_or_folder_to_check + self.directory_separator + f)
                        if not self.folder_contains_valid_file(self.path_to_clean + self.directory_separator + file_or_folder_to_check + self.directory_separator + f):
                            try:
                                self.remove(file_or_folder_to_check + self.directory_separator + f)
                            except Exception as e:
                                Logger("Error - Unable to remove file: " + str(e))
        except Exception as e:
            Logger("Error - cleaning: " +str(e))

    @staticmethod
    def is_directory(file_or_folder_to_check):
        if not os.path.isdir(file_or_folder_to_check):
            return False
        else:
            return True

    def folder_contains_valid_file(self, folder_to_check):
        contains_valid_file = False
        for file_or_folder_to_check in os.listdir(folder_to_check):
            if self.is_acceptable_file_type(self.path_to_clean + self.directory_separator + folder_to_check +
                    self.directory_separator + file_or_folder_to_check):
                contains_valid_file = True
                break
        return contains_valid_file

    def remove(self, file_or_folder_to_remove):
        successfully_removed = False

        if not os.path.isdir(file_or_folder_to_remove):
            successfully_removed = self.remove_single_file(file_or_folder_to_remove)
        else:
            successfully_removed = self.remove_folder(file_or_folder_to_remove)

        return successfully_removed

    @staticmethod
    def remove_single_file(file_to_remove):
        try:
            os.remove(file_to_remove)
            return True
        except OSError as e:
            Logger("Error - Removing single file: " + file_to_remove  + ", Exception: " + str(e))
            return False;

    @staticmethod
    def remove_folder(folder_to_remove):
        try:
            os.rmdir(folder_to_remove)
            return True
        except OSError as e:
            Logger("Error - Removing directory: " + folder_to_remove + ", Exception: " + str(e))
            return False;

    def is_acceptable_file_type(self, file_to_check):
        is_acceptable = True;

        if str(type(self.acceptable_file_types)) == "<type '_sre.SRE_Pattern'>":
            if not self.acceptable_file_types.search(file_to_check) or \
                    self.acceptable_parent_directory.search(file_to_check):
                is_acceptable = False
        else:
            for extension in str(file_to_check).split(','):
                if not str(file_to_check).endswith(extension):
                    is_acceptable = False

        return is_acceptable