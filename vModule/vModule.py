import re
import inspect
import utils
from utils import parseVerilog_inst_block
from utils import extract_vparam_ports
# Workflow:
# A verilog module is defined in the following way:
# the outer coat is a python function that takes in parameters of the python layer
# the inner coat is a verilog module that takes in parameters of the verilog layer
# the inner coat is written with a mixture of python code and magic comments followed by verilog code
# output_func is a transformed version of the python function with converted magic comments

class vModule:
    def __init__(self, ifunc):
        self.output_func = utils.convert(ifunc)
        self.params = self.output_func.__defaults__   # params
        self.signature = inspect.signature(self.output_func)
        self.params_names = list(self.signature.parameters.keys())
        self.vparams_names = []
        self.ports_names = []
        # print("start of func \n")
        # K = funcA(M,N)
        # print(K)
        # print("end of func \n")
    
    # generate module files before instantiation
    def pre_instantiate(self, params_dict, local_var_table):
        print("------------Executing Pre-Instantiation. Generating Module------------: \n")
        # pass the values in params_dict to ofunc
        bound_args = self.signature.bind_partial(**params_dict)
        bound_args.apply_defaults()
        v_declaration = self.output_func(**bound_args.arguments)
        [self.vparams_names, self.ports_names] = extract_vparam_ports(v_declaration)
        print("------------Pre-Instantiation: Done. Module Generated------------: \n")

    def instantiate(self, ports_dict, vparams_dict, module_name, inst_name):
        # parameters
        params_str = ", ".join([f".{key}({value})" for key, value in vparams_dict.items()])
        # ports
        ports_str = ", ".join([f".{key}({value})" for key, value in ports_dict.items()])
        # generate verilog code for instantiation
        verilog_code = f"{module_name} #({params_str}) {inst_name} ({ports_str});"
        # print verilog code for instantiation
        print(verilog_code)

    def instantiate_full(self, ports_dict, params_dict, vparams_dict, module_name, inst_name):
        self.pre_instantiate(self,params_dict)
        self.instantiate(self,ports_dict,vparams_dict,module_name,inst_name)

    def instantiate_full_str(self, inst_code, local_var):
        local_var_dict = local_var
        PORT_DICT_real = dict()
        VPARAM_DICT_real = dict()
        VPARAM_DICT = 0
        [PORT_DICT, PARAM_DICT, VPARAM_DICT, INST_NAME, MODULE_NAME] = parseVerilog_inst_block(inst_code, local_var_dict)
        self.pre_instantiate(PARAM_DICT, local_var)

        if (len(self.vparams_names) != len(VPARAM_DICT)) or (len(self.ports_names) != len(PORT_DICT)):
            raise Exception("Module Instantiation: Dimension of input ports/vparams do not match the required dimension")

        if isinstance(PORT_DICT, dict):
            PORT_DICT_real = PORT_DICT
        elif isinstance(PORT_DICT, list):
            cnt = 0
            for port_name in self.ports_names:
                PORT_DICT_real[port_name] = PORT_DICT[cnt]
                cnt =cnt + 1

        if isinstance(VPARAM_DICT, dict):
            VPARAM_DICT_real = VPARAM_DICT
        elif isinstance(PORT_DICT, list):
            cnt = 0
            for vparam_name in self.vparams_names:
                VPARAM_DICT_real[vparam_name] = PORT_DICT[cnt]
                cnt = cnt + 1

        self.instantiate(PORT_DICT_real, VPARAM_DICT_real, INST_NAME, MODULE_NAME)

    # def get_vparams_and_ports_names(self, params_dict):



    

    # convert the input module function for module output
 






