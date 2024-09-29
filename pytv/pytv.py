from pytv.utils import *
from pytv.ModuleLoader import *
# the decorator replaces func with a newly defined function decorated(*args, **kwargs)
def pytv(func):
    #A = getcallargs(func)
    # @wraps(func)
    def decorated(*args, **kwargs):
        STATE = 'IN_PYTHON'
        func_name = func.__name__
        abstract_module_name = func_name[6:]
        concrete_module_name = abstract_module_name
        # Add decorated func to the list in moduleloader
        ModuleLoader_Singleton.add_module_func(func_name)
        for key,value in kwargs.items():
            concrete_module_name += f"_{key}_{value}"
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
                new_func_code.append(f"    abstract_module_name = '{abstract_module_name}'\n")
                new_func_code.append(' ' * 4 + 'v_declaration = str()\n')
                new_func_code.append(' ' * 4 + 'v_module_name_tree = dict()\n')
                new_func_code.append(' ' * 4 + 'v_module_dict_list = []\n')
            stripped_line = line.strip()
            # STATE = state_transition(STATE, stripped_line)
            # neglect the original return value
            if stripped_line.startswith("return"):
                tokens = stripped_line.split()
                if tokens[0] == "return":
                    continue
            STATE = judge_state(stripped_line)
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
                    #Here the following 2 lines are added
                    #v_declaration_in, module_dict_tree_in, module_file_name_in = ModuleBasic(p1=10, p2=10)
                    #v_module_dict_list.append(module_dict_tree_in)
                    new_func_code.append(inst_line_renew)
                else:
                    inst_code.append(line + '\n')
                inst_code = []
            elif STATE == 'END_VERILOG_INST':
                inst_code = []

        # 将代码列表组合成字符串
        new_func_code.pop(0)
        new_func_code.pop(0)
        new_func_code.insert(0, line_func_def)

        # new_func_code.append("    print(v_module_dict_list)\n")
        new_func_code.append("    return v_declaration, v_module_dict_list")
        new_func_body = ''.join(new_func_code[0:])
        # print(new_func_body)
        # print(new_func_body)
        # 从第三行开始，因为前两行是函数定义
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
        verilog_code, module_dict_list = func_new(*args, **kwargs)
        module_dict_tree = dict()
        # print(verilog_code)
        # FOR TEST:
        # if func_name == "ModuleTOP":
        #     print("in module top")
        # FOR TEST
        module_generated, module_file_name, inst_idx_str = ModuleLoader_Singleton.generate_module(abstract_module_name, python_vars_dict, verilog_code)
        inst_verilog_code, module_name_tmp = instantiate_full(verilog_code, kwargs, module_file_name, inst_idx_str)
        # FOR TEST
        # print(inst_verilog_code)
        # print(f"xxxxxxxxxxxxxxxxxxxx{inst_verilog_code}xxxxxxxxxxxxxxxxxxx")
        # FOR TEST
        module_dict_tree[module_file_name] = module_dict_list
        ModuleLoader_Singleton.generate_file_tree(module_dict_tree)
        # pass the instantiation information to the singleton module
        ModuleLoader_Singleton.add_module_inst_info(inst_verilog_code, verilog_code, module_dict_tree, concrete_module_name, func_name)
        # return inst_verilog_code, verilog_code, module_dict_tree, concrete_module_name
        # return value of the original function
        # kwargs.pop("PORTS",None)
        # return func(*args, **kwargs)
    return decorated
# @py2v
# def testfunc1(A,B):
#     pass
#
#
#
# @py2v
# def simpletestfunc(M,N):
#     C = testfunc1(1,2)
#     #/ verilog BBB
#     print("C: \n")
#     print(C)
#
#
# simpletestfunc(1,1)


