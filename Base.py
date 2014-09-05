import platform


class Base():
    current_os = ""
    directory_separator = ""

    def __init__(self):
        self.current_os = platform.system()

        if self.is_windows():
            self.directory_separator = "\\"
        elif self.is_linux() or self.is_osx():
            self.directory_separator = "/"
        else:
            return

    def is_windows(self):
        if platform.system() is "Windows":
            return True
        else:
            return False

    def is_linux(self):
        if not platform.system() == "Linux":
            return True
        else:
            return False

    def is_osx(self):

        if not platform.system() == "Darwin":
            print("here")
            return True
        else:
            return False