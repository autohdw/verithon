from functools import wraps
import inspect
import re
from functools import wraps
from inspect import getcallargs

IN_PYTHON = 1
IN_VERILOG_INLINE = 2
BEGIN_VERILOG_INST = 3
IN_VERILOG_INST = 4
END_VERILOG_INST = 5

def isVerilogLine(line):
    pattern = '^#!'
    return bool(re.match(pattern, line))

def findPythonVarinVerilogLine(line):
    is_found = False
    pattern = r'(?<=\{).+?(?=\})'
    var_names = []
    var_names = re.findall(pattern, line)
    if len(var_names) > 0:
        is_found = True
    return var_names, is_found

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
    idx = line.index('#!')
    line_cut = line[idx+2:]
    line_cut_extend = "'" + line_cut + "'"
    line_code_renew = "print(" + line_cut_extend + ")"
    return line_code_renew

# This function processes the verilog instance block and returns a line of python code
def processVerilog_inst_block(inst_code):
    IN_PARAM = 1
    IN_VPARAM = 2
    IN_PORT = 3
    IN_INST_NAME = 4
    IN_MODULE_NAME = 5
    IDLE = 0
    STATE = 'IDLE'

    PARAM_DICT = {}
    VPARAM_DICT = {}
    PORT_DICT = {}

    for line in inst_code:
        line_without_note = line.replace('#!', '')
        line_strip = line_without_note.strip()
        line_cnt = 0
        if line_strip.startswith('PARAM:'): 
            STATE = 'IN_PARAM'
            line_cnt = 0
        elif line_strip.startswith('VPARAM:'):
            STATE = 'IN_VPARAM'
            line_cnt = 0
        elif line_strip.startswith('PORT:'):
            STATE = 'IN_PORT'
            line_cnt = 0
        elif line_strip.startswith('INST_NAME:'):
            STATE = 'IN_INST_NAME'
            line_cnt = 0
        elif line_strip.startswith('MODULE_NAME:'):
            STATE = 'IN_MODULE_NAME'
            line_cnt = 0

        key, value = line_strip.split(':')
        key = key.strip()
        value = value.strip()

        match STATE:
            case 'IDLE':
                continue

            case 'IN_PARAM':
                if line_cnt > 1:
                     PARAM_DICT[key] = value
                     line_cnt = line_cnt + 1

            case 'IN_VPARAM':
                if line_cnt > 1:
                     VPARAM_DICT[key] = value
                     line_cnt = line_cnt + 1
            
            case 'IN_PORT':
                if line_cnt > 1:
                     PORT_DICT[key] = value
                     line_cnt = line_cnt + 1

            case 'IN_INST_NAME':
                INST_NAME = value
            
            case 'IN_MODULE_NAME':
                MODULE_NAME = value

    return PARAM_DICT, VPARAM_DICT, PORT_DICT, INST_NAME, MODULE_NAME
    
               
def state_transition(STATE_prev, line):
    match STATE_prev:
        case 'IN_PYTHON':
            if isVerilogLine(line):
                line_without_note = line.replace('#!', '')
                line_strip = line_without_note.strip()
                if line_strip.startswith('INST:'):
                    STATE = 'BEGIN_VERILOG_INST'
                else:
                    STATE = 'IN_VERILOG_INLINE'
            else:
                STATE = 'IN_PYTHON'
        
        case 'IN_VERILOG_INLINE':
            if isVerilogLine(line):
                line_without_note = line.replace('#!', '')
                line_strip = line_without_note.strip()
                if line_strip.startswith('INST:'):
                    STATE = 'BEGIN_VERILOG_INST'
                else:
                    STATE = 'IN_VERILOG_INLINE'
            else:
                STATE = 'IN_PYTHON'

        case 'BEGIN_VERILOG_INST':
            if isVerilogLine(line):
                line_without_note = line.replace('#!', '')
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
                line_without_note = line.replace('#!', '')
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
                line_without_note = line.replace('#!', '')
                line_strip = line_without_note.strip()
                if line_strip.startswith('INST:'):
                    STATE = 'BEGIN_VERILOG_INST'
                else:
                    STATE = 'IN_VERILOG_INLINE'
            else:
                STATE = 'IN_PYTHON'
    return STATE
            

def convert(func):
    # Initalize the state machine
    STATE = IN_PYTHON
    src_lines, starting_line = inspect.getsourcelines(func)
    new_func_code = []
    for line in src_lines:
        stripped_line = line.strip()
        # check whether the line is verilog
        if isVerilogLine(stripped_line):
            # line_renew is print(stripped verilog line)
            line_renew = processVerilogLine(stripped_line)
            new_func_code.append(
                ' ' * (len(line) - len(stripped_line) - 1) + line_renew + '\n')
        # if it's not verilog line, directly add to the new code
        else:
            new_func_code.append(line + '\n')

    # Reassemble the code lines to form a new function
    new_func_body = ''.join(new_func_code[1:])  # 从第三行开始，因为前两行是函数定义
    # Execute newly assembled function
    local_vars = {}
    # exec(new_func_body, func.__globals__, local_vars)  # 执行新函数代码
    return local_vars[func.__name__]  # 将重定义后的函数返回


def convert_new(func):
    # Initalize the state machine
    STATE = IN_PYTHON
    src_lines, starting_line = inspect.getsourcelines(func)
    new_func_code = []
    inst_code = []
    for line in src_lines:
        stripped_line = line.strip()
        STATE = state_transition(STATE, stripped_line)
        if STATE == IN_PYTHON:
            new_func_code.append(line + '\n')
        elif STATE == IN_VERILOG_INLINE:
            line_renew = processVerilogLine(stripped_line)
            new_func_code.append(
                ' ' * (len(line) - len(stripped_line) - 1) + line_renew + '\n')
        elif STATE == BEGIN_VERILOG_INST:
            inst_code.append(line + '\n')
        elif STATE == IN_VERILOG_INST:
            inst_code.append(line + '\n')
        elif STATE == END_VERILOG_INST:
            inst_code_renew = processVerilog_inst_block(inst_code)
            new_func_code.append(
                ' ' * (len(line) - len(stripped_line) - 1) + inst_code_renew + '\n')

    # Reassemble the code lines to form a new function
    new_func_body = ''.join(new_func_code[1:])  # 从第三行开始，因为前两行是函数定义
    # Execute newly assembled function
    local_vars = {}
    exec(new_func_body, func.__globals__, local_vars)  # 执行新函数代码
    return local_vars[func.__name__]  # 将重定义后的函数返回

@convert
def test_function(DWT1, DWT2):
    print("Start to Generate RTL Code \n")  
    for i in range(3):
        #! module M(rst,A_in,B_in,C_out)
        #! input [{DWT1}:0] A_in
        #! input [{DWT2}:0] B_in
        #! output [{i}:0] C_out
        #! endmodule
        continue
    print("Generating Done \n")
    
test_function(DWT1 = 10, DWT2=5)