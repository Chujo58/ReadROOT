import os, subprocess, tkinter, json
from tkinter import filedialog

class FileExplorer():
    def __init__(self):
        tkinter.Tk().withdraw()

    def FindFolder(self, start_directory=None):
        return filedialog.askdirectory(initialdir=start_directory)

    def FindFiles(self, start_directory=None):
        return filedialog.askopenfilenames(initialdir=start_directory)

class Configuration():
    requiredHeaders = 3
    def __init__(self, name, configs_file):
        self.name = name
        self.configurations_file = configs_file
        self.required_path = []
        self.pybind11_header = None

    def get_name(self):
        return self.name
    
    def set_name(self, name):
        self.name = name

    def find_required_headers(self, start_directory=None, autosave=False):
        files = FileExplorer.FindFiles(start_directory)
        self.required_path.extend(files)
        while len(self.required_path) < self.requiredHeaders:
            files = FileExplorer.FindFiles(start_directory)
            self.required_path.extend(files)

        for file in self.required_path:
            if "pybind11.h" in file:
                self.pybind11_header = file
        
        self.save() if autosave else None

    def save(self):
        with open(self.configurations_file, "r") as f:
            configs = json.load(f)
        
        current_config = configs.get(self.name)
        if current_config is None:
            configs.update({self.name:{"Required Headers":self.required_path,"pybind11":self.pybind11_header}})
        else:
            configs.pop(self.name)
            configs.update({self.name:{"Required Headers":self.required_path,"pybind11":self.pybind11_header}})
        
        with open(self.configurations_file, "w") as f:
            json.dump(configs, f, indent=4)

    def load(self):
        with open(self.configurations_file, "r") as f:
            configs = json.load(f)

        self.required_path = configs.get(self.name).get("Required Headers")
        self.pybind11_header = configs.get(self.name).get("pybind11")

    def set_required_headers(self, number_of_headers):
        Configuration.requiredHeaders = number_of_headers

    def config_done(self):
        with open(self.configurations_file, "r") as f:
            configs = json.load(f)

        configs["LoadConfig"] = False
        
        with open(self.configurations_file, "w") as f:
            json.dump(configs, f, indent=4)

    def config_to_do(self):
        with open(self.configurations_file, "r") as f:
            configs = json.load(f)

        configs["LoadConfig"] = True
        
        with open(self.configurations_file, "w") as f:
            json.dump(configs, f, indent=4)        

class SetUpCpp():
    def __init__(self, file_path):
        self.file_path = file_path

    def load_configuration(self, config: Configuration):
        config.load() #Load config if it wasn't done.
        with open(self.file_path, "r") as f:
            lines = f.readlines()

        start = 0
        stop = 0
        for line in lines:     
            if "Start of config" in line:
                start = lines.index(line)
            if "End of config" in line:
                stop = lines.index(line)
        
        code_before_start = lines[0:start]

        first = lines[start]
        last = lines[stop]

        rest_of_code = lines[stop+1::]
        # print(rest_of_code)
        new_code = []
        new_code.extend(code_before_start)
        new_code.append(first)
        
        for header in config.required_path:
            new_code.append(f'#include "{header}"\n')

        new_code.append(last)
        new_code.extend(rest_of_code)
        
        with open(self.file_path, "w") as f:
            f.writelines(new_code)

    def load_pybind11(self, config: Configuration):
        config.load() #Load config if it wasn't done.
        with open(self.file_path, "r") as f:
            lines = f.readlines()

        start = 0
        stop = 0
        for line in lines:     
            if "Start of config" in line:
                start = lines.index(line)
            if "End of config" in line:
                stop = lines.index(line)
        
        code_before_start = lines[0:start]

        first = lines[start]
        last = lines[stop]

        rest_of_code = lines[stop+1::]
        # print(rest_of_code)
        new_code = []
        new_code.extend(code_before_start)
        new_code.append(first)
        
        new_code.append(f'#include "{config.pybind11_header}"\n')

        new_code.append(last)
        new_code.extend(rest_of_code)
        
        with open(self.file_path, "w") as f:
            f.writelines(new_code)
    


if __name__ == "__main__": 
    test = Configuration("XPS13","config.json")
    test.find_required_headers(autosave=True)
    test.load()

    setup = SetUpCpp("funcs.hpp")
    setup.load_configuration(test)
    setup = SetUpCpp("wrap.cpp")
    setup.load_pybind11(test)
