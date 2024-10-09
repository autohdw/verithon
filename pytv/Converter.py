# from pytv.utils import *
from functools import wraps
import inspect
import re
from functools import wraps
from inspect import getcallargs
import warnings
import json
import hashlib
from pytv.utils import extract_function_calls
from pytv.utils import isVerilogLine
from pytv.utils import isModuleFunc
from pytv.utils import findPythonVarinVerilogLine
from pytv.utils import processVerilogLine
from pytv.utils import processPythonVarinVerilogInst
from pytv.utils import processVerilogLine_str
from pytv.utils import parseVerilog_inst_block
from pytv.utils import processVerlog_inst_line
from pytv.utils import processVerilog_inst_block
from pytv.utils import judge_state
from pytv.utils import state_transition
from pytv.utils import extract_vparam_ports
from pytv.utils import instantiate_full
from pytv.utils import instantiate
from pytv.utils import replace_single_quotes
import pytv.ModuleLoader
from pytv.ModuleLoader import ModuleLoader
from pytv.ModuleLoader import ModuleLoader_Singleton
from pytv.ModuleLoader import moduleloader
# the decorator replaces func with a newly defined function decorated(*args, **kwargs)


def convert(func):
    def decorated(*args, **kwargs):
        flag_inst = True
        if "OUTMODE" in kwargs.keys():
            if kwargs["OUTMODE"] == "PRINT":
                flag_inst = False
        STATE = 'IN_PYTHON'
        func_name = func.__name__
        defaults = func.__defaults__
        if defaults:
            argnames = func.__code__.co_varnames[:func.__code__.co_argcount]
            defaults_dict = dict(zip(argnames[-len(defaults):], defaults))
            key_kwargs = kwargs.keys()
            key_default = defaults_dict.keys()
            for key_de in key_default:
                if key_de not in key_kwargs:
                    kwargs[key_de] = defaults_dict[key_de]
        abstract_module_name = func_name[6:]
        concrete_module_name = abstract_module_name
        # Add decorated func to the list in moduleloader
        moduleloader.add_module_func(func_name)
        flag_end_inst = 0
        new_func_code = []
        inst_code = []
        # the generated verilog code.
        python_vars_dict = kwargs
        src_lines, starting_line = inspect.getsourcelines(func)
        src_lines = [l.rstrip() for l in src_lines]
        i = 0
        # definition of the newly generated function for producing v_declaration code
        line_func_def = f"def func_new(*args, **kwargs): \n"
        for line in src_lines:
            # TEST:
            # if "ModuleMUL" in line:
            #     print("xxxxxxxxxxxx\n")
            # TEST
            i = i + 1
            if i == 3:
                # pass the keyword variables
                for key in kwargs.keys():
                    new_func_code.append(f"    {key}=kwargs['{key}']\n")
                new_func_code.append(f"    abstract_module_name = '{abstract_module_name}'\n")
                new_func_code.append(' ' * 4 + 'v_declaration = str()\n')
                new_func_code.append(' ' * 4 + 'v_module_name_tree = dict()\n')
                new_func_code.append(' ' * 4 + 'v_module_dict_list = []\n')
            stripped_line = line.strip()
            if stripped_line.startswith("return"):
                tokens = stripped_line.split()
                if tokens[0] == "return":
                    continue
            STATE = judge_state(stripped_line)
            if STATE == 'IN_PYTHON':
                new_func_code.append(line + '\n')
            elif STATE == 'IN_VERILOG_INLINE':
                line_renew = processVerilogLine(stripped_line)
                line_renew_str = processVerilogLine_str(stripped_line)
                new_func_code.append(
                    ' ' * (len(line) - len(stripped_line)) + line_renew_str + '\n')
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
        new_func_code.pop(0)
        new_func_code.pop(0)
        new_func_code.insert(0, line_func_def)
        new_func_code.append("    return v_declaration, v_module_dict_list")
        new_func_body = ''.join(new_func_code[0:])
        local_vars = {}
        # print(new_func_body)
        exec(new_func_body, func.__globals__, local_vars)
        func_new = local_vars['func_new']
        verilog_code, module_dict_list = func_new(*args, **kwargs)
        inst_verilog_code = str()
        module_dict_tree = dict()
        if flag_inst:
            module_generated, module_file_name, inst_idx_str = moduleloader.generate_module(abstract_module_name,
                                                                                            python_vars_dict,
                                                                                            verilog_code)
            inst_verilog_code, module_name_tmp = instantiate_full(verilog_code, kwargs, module_file_name, inst_idx_str)
            module_dict_tree[module_file_name] = module_dict_list
            moduleloader.generate_file_tree(module_dict_tree)
            # pass the instantiation information to the singleton module
            moduleloader.add_module_inst_info(inst_verilog_code, verilog_code, module_dict_tree, concrete_module_name,
                                              func_name)
        else:
            moduleloader.add_module_inst_info(inst_verilog_code, verilog_code, module_dict_tree, concrete_module_name,
                                              func_name)

    return decorated

