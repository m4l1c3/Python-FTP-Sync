import os
import re
import shutil

from Base import Base


class Cleaner(Base):
    pathToClean = ""
    typeOfRemoval = ""
    removalRegEx = ""
    file_list = []

    def __init__(self, path_to_clean, type_of_removal, file_list=[], removal_regex=""):
        Base.__init__(self)
        self.pathToClean = path_to_clean
        self.typeOfRemoval = type_of_removal
        self.fileList = file_list

        if removal_regex:
            self.removalRegEx = re.compile(removal_regex)

    def remove(self):
        if self.is_regex():
            for f in os.listdir(self.pathToClean):
                if self.removalRegEx.search(f):
                    self.remove_single_file(self.pathToClean + self.directory_separator + f)
        elif self.is_tree:
            shutil.rmtree(self.pathToClean)
        elif self.is_a_file:
            for f in self.file_list:
                self.remove_single_file(self.pathToClean + self.directory_separator + f)
        else:
            return False

    def remove_single_file(self, file_to_remove):
        try:
            os.remove(file_to_remove)
        except OSError as e:
            print("Error - Problem removing: " + file_to_remove + ", " + str(e))

    def is_regex(self):
        if type(self.removalRegEx) is "<class '_sre.SRE_Pattern'>":
            return True
        else:
            return False

    @property
    def is_a_file(self):
        if len(self.file_list) > 1:
            return True
        else:
            return False

    def is_tree(self):
        if self.typeOfRemoval == "tree":
            return True
        else:
            return False