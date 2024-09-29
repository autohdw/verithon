from functools import wraps
import inspect
import re
from functools import wraps
from inspect import getcallargs
import warnings
import json
import hashlib
from pytv.ModuleLoader import *

# Warning COLOR Setings
RED = "\033[31m"
RESET = "\033[0m"

def extract_function_calls(line):
    """
    检查输入的一行代码中是否有函数调用，并返回所有函数名。

    :param line: 输入的代码行
    :return: 一个包含函数名的列表，如果没有返回空列表
    """
    # 使用正则表达式匹配函数调用
    # 这里匹配格式：函数名(参数)
    pattern = r'\b(\w+)\s*\('
    matches = re.findall(pattern, line)

    return matches  # 返回所有匹配的函数名
def isVerilogLine(line):
    line = line.strip()
    pattern = '^#/'
    return bool(re.match(pattern, line))
def isModuleFunc(line):
    is_mf = False
    # for mf_name in ModuleLoader_Singleton.module_func_list:
    #     if mf_name in line:
    #         if not "def" in line:
    #             is_mf = True
    #             return is_mf
    line = line.strip()
    func_names = []
    func_name = str()
    if "def" in line:
        return is_mf
    func_names = extract_function_calls(line)
    if len(func_names) > 0:
        func_name = func_names[0]
        if func_name.startswith("Module"):
            is_mf = True
            return is_mf
    return is_mf

def findPythonVarinVerilogLine(line):
    is_found = False
    pattern = r'(?<=\`).+?(?=\`)'
    var_names = []
    var_names = re.findall(pattern, line)
    if len(var_names) > 0:
        is_found = True
    return var_names, is_found

# def subPythonVarinVerilog(line, local_var_dict):
#     [python_var_names, has_python_var] = findPythonVarinVerilogLine(line)
#     for python_var_name in python_var_names

def processVerilogLine(line):
    [python_var_names, has_python_var] = findPythonVarinVerilogLine(line)

    # Converting the python variable to numbers with python function str()
    # This is done when the decorator fucntion is executed, here only the python code is generated
    if(has_python_var):
        for python_var_name in python_var_names:
            name_str_extended = '`'+ python_var_name + '`'
            # This seems robust because there are usually no numbers at the start or end of a verilog line
            replace_str = "'+" + "str(" + python_var_name + ")" + "+'"
            line = line.replace(name_str_extended, replace_str)
    idx = line.index('#/')
    line_cut = line[idx+2:]
    line_cut_extend = "'" + line_cut + "'"
    line_code_renew = "print(" + line_cut_extend + ")"
    return line_code_renew

# directly replace the
def processPythonVarinVerilogInst(line, python_var_dict):
    [python_var_names, has_python_var] = findPythonVarinVerilogLine(line)
    if has_python_var:
        for python_var_name in python_var_names:
            name_str_extended = '`' + python_var_name + '`'
            replace_str = str(python_var_dict.get(python_var_name))
            line = line.replace(name_str_extended, replace_str)
    return line

def processVerilogLine_str(line):
    [python_var_names, has_python_var] = findPythonVarinVerilogLine(line)
    # fix for bugs in lines such as a = 12'b`llr`
    line = replace_single_quotes(line, "\\'")
    # Converting the python variable to numbers with python function str()
    # This is done when the decorator fucntion is executed, here only the python code is generated
    if(has_python_var):
        for python_var_name in python_var_names:
            name_str_extended = '`'+ python_var_name + '`'
            # This seems robust because there are usually no numbers at the start or end of a verilog line
            replace_str = "'+" + "str(" + python_var_name + ")" + "+'"
            line = line.replace(name_str_extended, replace_str)
    idx = line.index('#/')
    line_cut = line[idx+2:]
    #line_cut_extend = "'" + line_cut +  + "'"
    line_cut_extend = f"'{line_cut}\\n'"
    line_code_renew = 'v_declaration'+'='+'v_declaration'+'+'+line_cut_extend
    return line_code_renew

# This function processes the verilog instance block and returns a line of python code
def parseVerilog_inst_block(kwargs, module_file_name_in, inst_idx_str):
    has_module_name = False
    has_inst_name = False
    has_vparams = False
    #inst_keys = kwargs.keys()
    PORT_DICT = {}
    VPARAM_DICT = {}
    PARAM_DICT = []
    INST_NAME = str()
    MODULE_NAME = str()
    isTOP = True
    if 'PORTS' in kwargs:
        PORT_DICT = kwargs['PORTS']
        isTOP = False
    elif not moduleloader.disable_warning:
        warnings.warn(f"{RED}Call of module function with unassigned ports is detected. Make sure this is the top module{RESET}",stacklevel=4)
    if 'VPARAMS' in kwargs:
        has_vparams = True
        VPARAM_DICT = kwargs['VPARAMS']

    if 'MODULE_NAME' in kwargs:
        has_module_name = True
        MODULE_NAME = kwargs['MODULE_NAME']
        #if len(kwargs['MODULE_NAME'] > 0):
            
    if 'INST_NAME' in kwargs:
        has_inst_name = True
        INST_NAME = kwargs['INST_NAME']
        # if len(kwargs['INST_NAME'] > 0):
        
    # Assigning default module name if not defined in the verilog instance block
    module_file_name_in = module_file_name_in.strip()
    module_file_name_in = module_file_name_in.replace(".v","")
    module_file_name_in = module_file_name_in.strip()
    if not has_module_name:
        if not moduleloader.disable_warning:
           warnings.warn(f"{RED}Module name is not specified in the verilog instance block. Default module name applied.{RESET}",stacklevel=4)
        MODULE_NAME = module_file_name_in
    # Assigning default inst name if not defined in the verilog instance block
    if not has_inst_name:
        if not moduleloader.disable_warning:
           warnings.warn(f"{RED}Inst name is not specified in the verilog instance block. Default Inst name applied.{RESET}",stacklevel=4)
        INST_NAME = 'u_' + inst_idx_str + '_'
        INST_NAME = INST_NAME + MODULE_NAME
    # func_name = 'Module'+ MODULE_NAME
    return PORT_DICT, PARAM_DICT, VPARAM_DICT, INST_NAME, MODULE_NAME, isTOP

# process the python function for instantiating a verilog module by adding the return value
def processVerlog_inst_line(inst_line):
    # print(inst_line)
    inst_line_strip = inst_line.strip()
    n_blanks = len(inst_line) - len(inst_line_strip)
    # print(n_blanks)
    inst_line_renew0 = " " * (n_blanks-1) + inst_line_strip + "\n"
    inst_line_renew1 = " " * (n_blanks-1) + 'v_inst_code_in, v_declaration_in, module_dict_tree_in, module_file_name_in = '+ 'ModuleLoader_Singleton.extract_module_inst_info()' + "\n"
    inst_line_renew2 = " " * (n_blanks-1) + f"v_module_dict_list.append(module_dict_tree_in) \n"
    inst_line_renew3 = " " * (n_blanks-1) + f"v_declaration = v_declaration + v_inst_code_in \n"
    inst_line_renew = inst_line_renew0 + inst_line_renew1 + inst_line_renew2 + inst_line_renew3
    return inst_line_renew


def processVerilog_inst_block(inst_code):
    inst_code_str = str(inst_code)
    line_renew = f"inst_v_code_tmp, module_name_tmp = instantiate_full(v_declaration_in,{inst_code_str}, locals(), kwargs, module_file_name_in) \n"
    return line_renew

def judge_state(line):
    if isVerilogLine(line):
        STATE = 'IN_VERILOG_INLINE'
    else:
        if isModuleFunc(line):
            STATE = 'IN_VERILOG_INST'
        else:
            STATE = 'IN_PYTHON'
    return STATE

def state_transition(STATE_prev, line):
    match STATE_prev:
        case 'IN_PYTHON':
            if isVerilogLine(line):
                line_without_note = line.replace('#/', '')
                line_strip = line_without_note.strip()
                if line_strip.startswith('INST:'):
                    STATE = 'BEGIN_VERILOG_INST'
                else:
                    STATE = 'IN_VERILOG_INLINE'
            else:
                STATE = 'IN_PYTHON'
        
        case 'IN_VERILOG_INLINE':
            if isVerilogLine(line):
                line_without_note = line.replace('#/', '')
                line_strip = line_without_note.strip()
                if line_strip.startswith('INST:'):
                    STATE = 'BEGIN_VERILOG_INST'
                else:
                    STATE = 'IN_VERILOG_INLINE'
            else:
                STATE = 'IN_PYTHON'

        case 'BEGIN_VERILOG_INST':
            # TEST
            # print("INST BEGINS! \n")
            if isVerilogLine(line):
                line_without_note = line.replace('#/', '')
                line_strip = line_without_note.strip()
                if line_strip.startswith('INST:'):
                    STATE = 'BEGIN_VERILOG_INST'
                    raise Exception("Error: Nested verilog instance block is not supported in the current PyTv version.")
                elif line_strip.startswith('ENDINST'):
                    STATE = 'END_VERILOG_INST'
                else:
                    STATE = 'IN_VERILOG_INST'
            else:
                STATE = 'IN_VERILOG_INST'
                #raise Exception("Error: No python code inside the verilog instance block.")
     

        case 'IN_VERILOG_INST':
            if isVerilogLine(line):
                line_without_note = line.replace('#/', '')
                line_strip = line_without_note.strip()
                if line_strip.startswith('INST:'):
                    STATE = 'BEGIN_VERILOG_INST'
                    raise Exception("Error: Nested verilog instance block is not supported in the current PyTv version.")
                elif line_strip.startswith('ENDINST'):
                    STATE = 'END_VERILOG_INST'
                else:
                    STATE = 'IN_VERILOG_INST'
            else:
                STATE = 'IN_VERILOG_INST'
                #raise Exception("Error: No python code inside the verilog instance block.")

            
        case 'END_VERILOG_INST':
            if isVerilogLine(line):
                line_without_note = line.replace('#/', '')
                line_strip = line_without_note.strip()
                if line_strip.startswith('INST:'):
                    STATE = 'BEGIN_VERILOG_INST'
                else:
                    STATE = 'IN_VERILOG_INLINE'
            else:
                STATE = 'IN_PYTHON'
    return STATE

def extract_vparam_ports(v_declaration):
    pattern = r'(?<=\().+?(?=\))'
    v_declaration = v_declaration.replace('\n',' ')
    port_names = str()
    vparam_names = []
    vparam_and_port_names = re.findall(pattern, v_declaration)
    port_names = vparam_and_port_names[0].replace(',',' ')
    #port_names = vparam_and_port_names[1].replace(',',' ')
    #vparam_names = vparam_names.split()
    port_names = port_names.split()
    return vparam_names, port_names


def instantiate_full(v_declaration, kwargs, module_file_name_in,inst_idx_str):
    PORT_DICT_real = dict()
    VPARAM_DICT_real = dict()
    # Find the required ports by looking up the verilog code
    [vparams_names, ports_names] = extract_vparam_ports(v_declaration)
    # Get the ports and vparams passed by kwargs
    [PORT_DICT, PARAM_DICT, VPARAM_DICT, INST_NAME, MODULE_NAME, isTOP] = parseVerilog_inst_block(kwargs, module_file_name_in, inst_idx_str)
    v_code = str()
    # Exit function if it represents the top module
    if (isTOP):
        return v_code, MODULE_NAME
    if (len(vparams_names) != len(VPARAM_DICT)) or (len(ports_names) != len(PORT_DICT)):
        raise Exception("Module Instantiation: Dimension of input ports/vparams do not match the required dimension")
        pass
    if isinstance(PORT_DICT, dict):
        PORT_DICT_real = PORT_DICT
    elif isinstance(PORT_DICT, list):
        cnt = 0
        for port_name in ports_names:
            PORT_DICT_real[port_name] = PORT_DICT[cnt]
            cnt = cnt + 1
    if isinstance(VPARAM_DICT, dict):
        VPARAM_DICT_real = VPARAM_DICT
    elif isinstance(PORT_DICT, list):
        cnt = 0
        for vparam_name in vparams_names:
            VPARAM_DICT_real[vparam_name] = PORT_DICT[cnt]
            cnt = cnt + 1
    v_code = instantiate(PORT_DICT_real, VPARAM_DICT_real, INST_NAME, MODULE_NAME)
    # print(v_code)
    # print(MODULE_NAME)
    return v_code, MODULE_NAME

def instantiate(ports_dict, vparams_dict, module_name, inst_name):
        params_str = str()
        ports_str = str()
        verilog_code = str()
        # parameters
        if len(vparams_dict) != 0:
            params_str = ", ".join([f".{key}({value})" for key, value in vparams_dict.items()])
        # ports
        ports_str = ", ".join([f".{key}({value})" for key, value in ports_dict.items()])
        # generate verilog code for instantiation
        if len(vparams_dict) != 0:
            verilog_code = f"{inst_name} #({params_str}) {module_name} ({ports_str});\n"
        else:
            verilog_code = f"{inst_name}  {module_name}({ports_str});\n"
        # print verilog code for instantiation

        return verilog_code

def replace_single_quotes(input_string, replacement):
    result = ''
    in_backticks = False
    i = 0

    while i < len(input_string):
        if input_string[i] == '`':
            in_backticks = not in_backticks

        if input_string[i] == "'" and not in_backticks:
            result += replacement
        else:
            result += input_string[i]

        i += 1

    return result


# This function extracts the verilog parameters and ports from the verilog module definition
# def extract_vparams_ports(src_lines):
#     return 0

# @convert
# def test_function(DWT1, DWT2):
#     print("Start to Generate RTL Code \n")
#     for i in range(3):
#         #! module M(rst,A_in,B_in,C_out)
#         #! input [{DWT1}:0] A_in
#         #! input [{DWT2}:0] B_in
#         #! output [{i}:0] C_out
#         #! endmodule
#         continue
#     print("Generating Done \n")
#
# test_function(DWT1 = 10, DWT2=5)