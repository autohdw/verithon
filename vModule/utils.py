from functools import wraps
import inspect
import re
from functools import wraps
from inspect import getcallargs

# IN_PYTHON = 1
# IN_VERILOG_INLINE = 2
# BEGIN_VERILOG_INST = 3
# IN_VERILOG_INST = 4
# END_VERILOG_INST = 5
def isVerilogLine(line):
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
    line_cut_extend = "'" + line_cut + "'"
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

def processVerilog_inst_block(inst_code):
    MODULE_NAME = str()
    for line in inst_code:
        line_without_note = line.replace('#/', '')
        line_strip = line_without_note.strip()
        if line_strip.startswith('MODULE_NAME:'):
            line_module_name = line_strip.replace('MODULE_NAME:','')
            MODULE_NAME = line_module_name.strip()
            break
    func_name = 'Module'+ MODULE_NAME
    module_object_name = 'Module'+'Object'+ MODULE_NAME
    lines_renew = []
    line_renew_obj = module_object_name + '=' + 'vModule.vModule'+ '(' + func_name + ')'+'\n'
    line_renew_inst = module_object_name + '.' + 'instantiate_full_str' + '('+ str(inst_code) + ',' + 'locals()' + ')'+'\n'
    return line_renew_obj, line_renew_inst


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
                STATE = 'IN_PYTHON'
                raise Exception("Error: No python code inside the verilog instance block.")
     

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
                STATE = 'IN_PYTHON'
                raise Exception("Error: No python code inside the verilog instance block.")

            
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
    vparam_and_port_names = re.findall(pattern, v_declaration)
    vparam_names = vparam_and_port_names[0].replace(',',' ')
    port_names = vparam_and_port_names[1].replace(',',' ')
    vparam_names = vparam_names.split()
    port_names = port_names.split()
    return vparam_names, port_names


def convert(func):
    # Initalize the state machine
    STATE = 'IDLE'
    src_lines, starting_line = inspect.getsourcelines(func)
    new_func_code = []
    i = 0
    for line in src_lines:
        i = i + 1
        if i == 2:
            new_func_code.append(' '*3 + 'v_declaration = str()\n')
        stripped_line = line.strip()
        # check whether the line is verilog
        if isVerilogLine(stripped_line):
            # line_renew is print(stripped verilog line)
            line_renew = processVerilogLine(stripped_line)
            new_func_code.append(
                ' ' * (len(line) - len(stripped_line) - 1) + line_renew + '\n')
            line_renew_str = processVerilogLine_str(stripped_line)
            new_func_code.append(
                ' ' * (len(line) - len(stripped_line) - 1) + line_renew_str + '\n')
        # if it's not verilog line, directly add to the new code
        else:
            new_func_code.append(line + '\n')
    new_func_code.append(' '*3 + 'return v_declaration')

    # Reassemble the code lines to form a new function
    new_func_body = ''.join(new_func_code[0:])  # 从第三行开始，因为前两行是函数定义
    #print("output_func of vModule object \n")
    #print(new_func_body)
    # Execute newly assembled function
    local_vars = {}
    #exec(new_func_body, func.__globals__, local_vars)  # 执行新函数代码
    exec(new_func_body, globals())
    return globals()[func.__name__]  # 将重定义后的函数返回


def convert_new(func):
    # Initalize the state machine
    STATE = 'IN_PYTHON'
    src_lines, starting_line = inspect.getsourcelines(func)
    new_func_code = []
    inst_code = []
    for line in src_lines:
        stripped_line = line.strip()
        STATE = state_transition(STATE, stripped_line)
        if STATE == 'IN_PYTHON':
            new_func_code.append(line + '\n')
        elif STATE == 'IN_VERILOG_INLINE':
            line_renew = processVerilogLine(stripped_line)
            new_func_code.append(
                ' ' * (len(line) - len(stripped_line) - 1) + line_renew + '\n')
        elif STATE == 'BEGIN_VERILOG_INST':
            inst_code.append(line + '\n')
        elif STATE == 'IN_VERILOG_INST':
            inst_code.append(line + '\n')
        elif STATE == 'END_VERILOG_INST':
            obj_code, inst_code = processVerilog_inst_block(inst_code)
            new_func_code.append(
                ' ' * (len(line) - len(stripped_line) - 1) + obj_code )
            new_func_code.append(
                ' ' * (len(line) - len(stripped_line) - 1) + inst_code)


    # Reassemble the code lines to form a new function
    new_func_body = ''.join(new_func_code[1:])  # 从第三行开始，因为前两行是函数定义
    #print(new_func_body)
    # Execute newly assembled function
    local_vars = {}
    exec(new_func_body, func.__globals__, local_vars)  # 执行新函数代码
    return local_vars[func.__name__]  # 将重定义后的函数返回

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