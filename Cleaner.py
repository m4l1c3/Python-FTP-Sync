import os
import re
import shutil


class Cleaner:
    pathToClean = ""
    typeOfRemoval = ""
    removalRegEx = ""
    file_list = []

    def __init__(self, path_to_clean, type_of_removal, removal_regex="", file_list=[]):
        self.pathToClean = path_to_clean
        self.typeOfRemoval = type_of_removal
        self.fileList = file_list

        if removal_regex:
            self.removalRegEx = re.compile(removal_regex)

    def remove(self):
        if self.is_regex():
            return
        elif self.is_tree:
            return
        elif self.is_single_file:
            return
        else:
            os.remove()
            shutil.rmtree()
            return

    def is_regex(self):
        if type(self.removalRegEx) is "<class '_sre.SRE_Pattern'>":
            return True
        else:
            return False

    def is_single_file(self):
        if self.typeOfRemoval == "file":
            return True
        else:
            return False

    def is_tree(self):
        if self.typeOfRemoval == "tree":
            return True
        else:
            return False