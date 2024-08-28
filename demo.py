import inspect
import re

def special_comment_interpreter(func):
    # 获取函数的源码和开始行号
    src_lines, starting_line = inspect.getsourcelines(func)
    new_func_code = []
    special_command_mapping = {
        '#/ Hello': "print('hello')",
        '#/ Nice': "print('nice')"
    }
    
    # 提前定义处理每一个源代码行
    for line in src_lines:
        # 检查是否是特殊注释行
        stripped_line = line.strip()
        if stripped_line in special_command_mapping:
            # 若是特殊注释，添加映射命令到新代码中，保持源代码的缩进
            new_func_code.append(' ' * (len(line) - len(stripped_line) - 1) + special_command_mapping[stripped_line] + '\n')
        # 添加当前行到新函数代码中，确保结构未被破坏
        new_func_code.append(line + '\n')

    # 将代码列表组合成字符串
    new_func_body = ''.join(new_func_code[1:])  # 从第三行开始，因为前两行是函数定义

    # 在当前局部作用域定义一个新的函数执行环境
    local_vars = {}
    exec(new_func_body, func.__globals__, local_vars)  # 执行新函数代码
    return local_vars[func.__name__]  # 将重定义后的函数返回




@special_comment_interpreter
def test_function():
    print("Start of the function.")    # Normal function code start
    print("Middle of the function.")   # More normal code
    for i in range(3):
        a =3
        #/ Hello
        #/ Nice
        #// inst namse: a
        continue
    print("More middle of the function.")
    #/ Nice
    print("End of the function.")      # Normal function code end



test_function()
