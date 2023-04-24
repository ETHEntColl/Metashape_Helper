class SettingTypeError(Exception):
    def __init__(self, message: str):
        self.message = message
    
class SettingNotFoundError(Exception):
    def __init__(self, message: str):
        self.message = message

class SettingValueError(Exception):
    def __init__(self, message: str):
        self.message = message

class MetashapeVersionMismatchError(Exception):
    def __init__(self, installed_version: str, needed_version: str):
        self.installed_version = installed_version
        self.needed_version = needed_version

        self.message = f"Script requires Metashape version {needed_version}, but the installed version is {installed_version}"
        super().__init__(self.message)
        