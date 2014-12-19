import os
import re
import shutil

from Base import Base


class Cleaner(Base):
    path_to_clean = ""
    type_of_removal = ""
    removal_reg_ex = ""
    file_list = []

    def __init__(self, path_to_clean, file_list=[], removal_regex=""):
        Base.__init__(self)
        self.path_to_clean = path_to_clean
        self.fileList = file_list

        if removal_regex:
            self.removal_reg_ex = re.compile(removal_regex)

    def remove(self):
        if self.is_regex():
            for f in os.listdir(self.path_to_clean):
                if self.removal_reg_ex.search(f):
                    self.remove_single_file(self.path_to_clean + self.directory_separator + f)
        elif self.is_tree:
            shutil.rmtree(self.path_to_clean)
        elif self.is_a_file:
            for f in self.file_list:
                self.remove_single_file(self.path_to_clean + self.directory_separator + f)
        else:
            return False

    def remove_single_file(self, file_to_remove):
        try:
            os.remove(file_to_remove)
        except OSError as e:
            print("Error - Problem removing: " + file_to_remove + ", " + str(e))

    def is_regex(self):
        if type(self.removal_reg_ex) is "<class '_sre.SRE_Pattern'>":
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
        if self.type_of_removal == "tree":
            return True
        else:
            return False