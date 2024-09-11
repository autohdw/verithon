
from voldelog.utils import *
from voldelog.ModuleLoader import *
def voodoo(func):
    #A = getcallargs(func)
    #@wraps(func)
    def decorated(*args, **kwargs):
        STATE = 'IN_PYTHON'
        func_name = func.__name__
        abstract_module_name = func_name[6:]

        #print(abstract_module_name)
        #print(func_name)
        flag_end_inst = 0
        new_func_code = []
        inst_code = []
        # the generated verilog code.
        python_vars_dict = kwargs
        #dict_new = getcallargs(func, *args, **kwargs)
        #python_vars_dict_extend = locals()
        src_lines, starting_line = inspect.getsourcelines(func)
        i = 0
        # definition of the newly generated function for producing v_declaration code
        line_func_def = f"def func_new(*args, **kwargs): \n"
        for line in src_lines:
            i = i + 1
            if i == 3:
                #key = 'param_top1'
                #new_func_code.append(' ' * 4 + "param_top1 = kwargs['param_top1']\n")
                # pass the keyword variables
                for key in kwargs.keys():
                    new_func_code.append(f"    {key}=kwargs['{key}']\n")
                new_func_code.append(' ' * 4 + 'v_declaration = str()\n')
            stripped_line = line.strip()
            STATE = state_transition(STATE, stripped_line)
            if STATE == 'IN_PYTHON':
                new_func_code.append(line + '\n')
            elif STATE == 'IN_VERILOG_INLINE':
                line_renew = processVerilogLine(stripped_line)
                # new_func_code.append(
                #     ' ' * (len(line) - len(stripped_line) - 1) + line_renew + '\n')
                line_renew_str = processVerilogLine_str(stripped_line)
                new_func_code.append(
                    ' ' * (len(line) - len(stripped_line) - 1) + line_renew_str + '\n')
            elif STATE == 'BEGIN_VERILOG_INST':
                flag_end_inst = 1
                inst_code.append(line + '\n')
            elif STATE == 'IN_VERILOG_INST':
                if not isVerilogLine(line):
                    b = isVerilogLine(line)
                    inst_line_renew = processVerlog_inst_line(line)
                    new_func_code.append(inst_line_renew)
                else:
                    inst_code.append(line + '\n')
            elif STATE == 'END_VERILOG_INST':
                stripped_line = line.strip()
                n_blanks = len(line) - len(stripped_line)
                line_inst_renew = processVerilog_inst_block(inst_code)
                new_func_code.append(' ' * (n_blanks - 1) + line_inst_renew)
                new_func_code.append(' ' * (n_blanks - 1) + f"v_declaration = v_declaration + {line_inst_renew}\n")
        # 将代码列表组合成字符串
        new_func_code.pop(0)
        new_func_code.pop(0)
        new_func_code.insert(0, line_func_def)
        new_func_code.append("    return v_declaration")
        new_func_body = ''.join(new_func_code[0:])  # 从第三行开始，因为前两行是函数定义
        # 在当前局部作用域定义一个新的函数执行环境

        local_vars = {}
        #G = func. __globals__
        #L = local_vars
        #("Newly Assembled Function: \n")
        #print(new_func_body)
        #G = func.__globals__
        exec(new_func_body, func.__globals__, local_vars)  # 执行新函数代码
        func_new = local_vars['func_new']
        # kwargs['param_top1'] = 2
        # kwargs['param_top2'] = 4
        # print(**kwargs)
        verilog_code = func_new(*args, **kwargs)
        # print(verilog_code)
        ModuleLoader_Singleton.generate_module(abstract_module_name, python_vars_dict, verilog_code)
        return verilog_code
    return decorated
# @voodoo
# def testfunc1(A,B):
#     pass
#
#
#
# @voodoo
# def simpletestfunc(M,N):
#     C = testfunc1(1,2)
#     #/ verilog BBB
#     print("C: \n")
#     print(C)
#
#
# simpletestfunc(1,1)


