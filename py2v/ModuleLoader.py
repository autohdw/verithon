import os

class ModuleLoader:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.abstract_module_list = []
        self.module_file_name_list = []
    
    # load the module based on the abstract module name and the parameter value
    # returns a boolean value to indicate whether the module is already generated or not, and the module file name
    def load_module(self,abstract_module_name,module_param_dict):
        moduleExists = False
        if abstract_module_name in self.abstract_module_list:
            pass
        else:
            self.abstract_module_list.append(abstract_module_name)
        module_file_name = abstract_module_name
        for key,value in module_param_dict.items():
            # generate the module file name based on the abstract module name and the parameter value
            module_file_name += "_" + key + "_" + str(value)
        
        if module_file_name in self.module_file_name_list:
            pass
        else:
            self.module_file_name_list.append(module_file_name)
        return moduleExists, module_file_name
    
    # writes the module verilog code to the file 
    # returns a boolean value to indicate whether the module is generated or not
    def generate_module(self,abstract_module_name,module_param_dict,module_verilog_code):
        moduleGenerated = False
        moduleExists, module_file_name = self.load_module(abstract_module_name,module_param_dict)
        if not moduleExists:
            with open(self.root_dir + "\\" + module_file_name + ".v","w") as f:
                f.write(module_verilog_code)
            moduleGenerated = True
            print(f"Writing into module file {module_file_name}.v \n")
        return moduleGenerated
        
current_file_dir = os.path.dirname(os.path.abspath(__file__))
# create a singleton instance of the ModuleLoader class
ModuleLoader_Singleton = ModuleLoader(f"{current_file_dir}\\RTL")