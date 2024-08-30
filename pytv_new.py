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

def processVerilogLine(line, python_vars_dict):
    [python_var_names, has_python_var] = findPythonVarinVerilogLine(line)
    if(has_python_var):
        for python_var_name in python_var_names:
            name_str_extended = '{'+ python_var_name + '}'
            python_var_value = str(python_vars_dict.get(python_var_name))
            line = line.replace(name_str_extended, python_var_value)
    idx = line.index('#!')
    line_cut = line[idx+2:]
    line_renew = 'f.write('+"'"+line_cut+ "'" +')'
    return line_renew

def convert(func):
    new_func_code = [];
    @wraps(func)
    def decorated(*args, **kwargs):
        python_vars_dict = kwargs
        #dict_new = getcallargs(func, *args, **kwargs)
        #python_vars_dict_extend = locals()
        src_lines, starting_line = inspect.getsourcelines(func)
        for line in src_lines:
            stripped_line = line.strip()
            if isVerilogLine(stripped_line):
               line_renew = processVerilogLine(stripped_line, python_vars_dict)
               #print(line_renew)
               new_func_code.append(' ' * (len(line) - len(stripped_line) - 1) +"with open('C:\信道编码\AutoGeneration\PyTV_new\\test.txt','w') as f:"+'\n')
               new_func_code.append(
                ' ' * (len(line) - len(stripped_line) + 1) + line_renew + '\n')
            else:
                new_func_code.append(line + '\n')
        # 将代码列表组合成字符串
        new_func_body = ''.join(new_func_code[1:])  # 从第三行开始，因为前两行是函数定义
        # 在当前局部作用域定义一个新的函数执行环境
        local_vars = {}
        #G = func. __globals__
        #L = local_vars
        exec(new_func_body, func.__globals__, local_vars)  # 执行新函数代码
        return func(*args, **kwargs)
    return decorated

@convert
def test_function(DWT1, DWT2):
    print("Start to Generate RTL Code \n")  # Normal function code start
    for i in range(3):

        #! module M(rst,A_in,B_in,C_out)
        #! input [{DWT1}:0] A_in
        #! input [{DWT2}:0] B_in
        #! output [10:0] C_out
        #! endmodule
        continue
    print("Generating Done \n")
test_function(DWT1 = 10, DWT2=5)