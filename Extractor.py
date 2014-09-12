import os
import imp
import zipfile
import re
import tarfile

from Base import Base
rar_file = imp.load_source('rarfile', 'rarfile/rarfile.py')


class Extractor(Base):
    source_path = ""
    destination_path = ""
    zip_regex = re.compile("\.(zip)")
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
                    self.process_rar_archive(sorted(os.listdir(self.source_path))[0])
                    break
                elif self.is_zip_archive(f):
                    self.process_zip_archive(sorted(os.listdir(self.source_path))[0])
                elif self.is_tar_archive(f):
                    self.process_tar_archive(sorted(os.listdir(self.source_path))[0])
        except Exception as e:
            print("Error - unable to determine archive type: " + str(e))

    def process_tar_archive(self, archive_file):
        try:
            obj_tar_file = tarfile.open(self.source_path + self.directory_separator + archive_file)
            print("Extracting: " + str(obj_tar_file))
            obj_tar_file.extractall(self.destination_path)
            obj_tar_file.close()
        except Exception as e:
            print("Error - Unable to extract tar: " + str(e))

    def process_rar_archive(self, archive_file):
        try:
            with rar_file.RarFile(self.source_path + self.directory_separator + archive_file) as obj_rar_file:
                print("Extracting - " + str(obj_rar_file))
                obj_rar_file.extractall(self.destination_path)
        except Exception as e:
            print("Error - Unable to extract rar: " + str(e))

    def process_zip_archive(self, archive_file):
        try:
            with zipfile.ZipFile(self.source_path + self.directory_separator + archive_file, "r") as zip_file:
                print("Extracting - " + zip_file.filename)
                zip_file.extractall(self.destination_path + self.directory_separator + archive_file[:str(archive_file).find(".z")])
        except Exception as e:
            print("Error - Unable to extract zip: " + str(e))

    def is_rar_archive(self, target_file_name):
        if not self.rar_regex.search(target_file_name):
            return False
        else:
            return True

    def is_zip_archive(self, target_file_name):
        if not zipfile.is_zipfile(target_file_name):
            return False
        else:
            return True

    def is_tar_archive(self, target_file_name):
        if not tarfile.is_tarfile(target_file_name):
            return False
        else:
            return True