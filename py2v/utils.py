from functools import wraps
import inspect
import re
from functools import wraps
from inspect import getcallargs

def isVerilogLine(line):
    line = line.strip()
    pattern = '^#/'
    return bool(re.match(pattern, line))

def findPythonVarinVerilogLine(line):
    is_found = False
    pattern = r'(?<=\{).+?(?=\})'
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
            name_str_extended = '{'+ python_var_name + '}'
            # This seems robust because there are usually no numbers at the start or end of a verilog line
            replace_str = "'+" + "str(" + python_var_name + ")" + "+'"
            line = line.replace(name_str_extended, replace_str)
    idx = line.index('#/')
    line_cut = line[idx+2:]
    line_cut_extend = "'" + line_cut + "'"
    line_code_renew = "print(" + line_cut_extend + ")"
    return line_code_renew

def processVerilogLine_str(line):
    [python_var_names, has_python_var] = findPythonVarinVerilogLine(line)

    # Converting the python variable to numbers with python function str()
    # This is done when the decorator fucntion is executed, here only the python code is generated
    if(has_python_var):
        for python_var_name in python_var_names:
            name_str_extended = '{'+ python_var_name + '}'
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
def parseVerilog_inst_block(inst_code, local_var_dict):
    STATE = 'IDLE'
    PARAM_DICT = {}
    VPARAM_DICT = {}
    PORT_DICT = {}
    MODULE_NAME = str()
    INST_NAME = str()
    line_cnt = 0
    for line in inst_code:
        line_without_note = line.replace('#/', '')
        line_strip = line_without_note.strip()
        if line_strip.startswith('PARAMS:'):
            STATE = 'IN_PARAM'
            line_cnt = 0
        elif line_strip.startswith('VPARAMS:'):
            STATE = 'IN_VPARAM'
            line_cnt = 0
        elif line_strip.startswith('PORTS:'):
            STATE = 'IN_PORT'
            line_cnt = 0
        elif line_strip.startswith('INST_NAME:'):
            STATE = 'IN_INST_NAME'
            line_cnt = 0
        elif line_strip.startswith('MODULE_NAME:'):
            STATE = 'IN_MODULE_NAME'
            line_cnt = 0
        elif line_strip.startswith('ENDINST'):
            STATE = 'ENDINST'
            line_cnt = 0
        [python_var_names, has_python_var] = findPythonVarinVerilogLine(line_strip)
        match STATE:
            case 'IDLE':
                continue

            case 'IN_PARAM':
                if line_cnt > 0 :
                    key, value = line_strip.split(':')
                    key = key.strip()
                    if has_python_var:
                        value = local_var_dict.get(python_var_names[0])
                        PARAM_DICT[key] = value
                    else:
                        raise Exception("Python PARAMs can only be asssigned with pre-defined python variables")
                line_cnt = line_cnt + 1
            
            case 'IN_VPARAM':
                if line_cnt > 0 :
                    line_split = line_strip.split(':')
                    if len(line_split) == 1:
                        if has_python_var:
                            VPARAM_DICT = local_var_dict.get(python_var_names[0])
                        else:
                            raise Exception("Missing ':' in instantiation")
                    else:
                        key, value = line_strip.split(':')
                        key = key.strip()
                        value = value.strip()
                        VPARAM_DICT[key] = value
                line_cnt = line_cnt + 1
            
            case 'IN_PORT':
                if line_cnt > 0 :
                    line_split = line_strip.split(':')
                    if len(line_split) == 1:
                        if has_python_var:
                            PORT_DICT = local_var_dict.get(python_var_names[0])
                        else:
                            raise Exception("Missing ':' in instantiation")
                    else:
                        key, value = line_strip.split(':')
                        key = key.strip()
                        value = value.strip()
                        PORT_DICT[key] = value
                line_cnt = line_cnt + 1

            case 'IN_INST_NAME':
                key, value = line_strip.split(':')
                key = key.strip()
                value = value.strip()
                INST_NAME = value
            
            case 'IN_MODULE_NAME':
                key, value = line_strip.split(':')
                #value = 1
                key = key.strip()
                value = value.strip()
                MODULE_NAME = value

    func_name = 'Module'+ MODULE_NAME
    module_object_name = 'Module'+'Object'+ MODULE_NAME
    lines_renew = []
    line_renew_obj = module_object_name + '=' + 'vModule.vModule'+ '(' + func_name + ')'+'\n'
    line_renew_inst = module_object_name + '.' + 'instantiate_full' + '(' + str(PORT_DICT) + ',' + str(PARAM_DICT) + ',' + str(VPARAM_DICT) + ',' + str(MODULE_NAME) + ',' + str(INST_NAME) + ')'+'\n'
    lines_renew.append(line_renew_obj)
    lines_renew.append(line_renew_inst)
    #print(PARAM_DICT)
    return PORT_DICT, PARAM_DICT, VPARAM_DICT, INST_NAME, MODULE_NAME

# process the python function for instantiating a verilog module by adding the return value
def processVerlog_inst_line(inst_line):
    #print(inst_line)
    print("\n")
    inst_line_strip = inst_line.strip()
    n_blanks = len(inst_line) - len(inst_line_strip)
    inst_line_renew = " " * (n_blanks-1) + 'v_declaration_in = '+ inst_line_strip + "\n"
    return inst_line_renew


def processVerilog_inst_block(inst_code):
    inst_code_str = str(inst_code)
    line_renew = f"instantiate_full(v_declaration_in,{inst_code_str}, locals()) \n"
    return line_renew


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
    vparam_and_port_names = re.findall(pattern, v_declaration)
    vparam_names = vparam_and_port_names[0].replace(',',' ')
    port_names = vparam_and_port_names[1].replace(',',' ')
    vparam_names = vparam_names.split()
    port_names = port_names.split()
    return vparam_names, port_names


def instantiate_full(v_declaration, inst_code, local_var_dict):
    local_var_dict = local_var_dict
    PORT_DICT_real = dict()
    VPARAM_DICT_real = dict()
    [vparams_names, ports_names] = extract_vparam_ports(v_declaration)
    [PORT_DICT, PARAM_DICT, VPARAM_DICT, INST_NAME, MODULE_NAME] = parseVerilog_inst_block(inst_code, local_var_dict)
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
    return v_code

def instantiate(ports_dict, vparams_dict, module_name, inst_name):
        # parameters
        params_str = ", ".join([f".{key}({value})" for key, value in vparams_dict.items()])
        # ports
        ports_str = ", ".join([f".{key}({value})" for key, value in ports_dict.items()])
        # generate verilog code for instantiation
        verilog_code = f"{inst_name} #({params_str}) {module_name} ({ports_str});\n"
        # print verilog code for instantiation
        return verilog_code



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