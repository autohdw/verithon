from functools import wraps
import inspect
import re
from functools import wraps
from inspect import getcallargs

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

def convert(func):
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