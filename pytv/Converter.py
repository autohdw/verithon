# from pytv.utils import *
from functools import wraps
import inspect
import time
import ast
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
from pytv.utils import get_default_expressions
from pytv.utils import find_irrelevant_line_in_for_loop
from pytv.utils import modify_func_call
import traceback
import sys
# the decorator replaces func with a newly defined function decorated(*args, **kwargs)
YELLOW = "\033[1;33m"
RESET = "\033[0m"


def accumulate_complete_call(src_lines, start_idx):
    """
    Accumulate lines starting from start_idx until we have balanced parentheses/braces/brackets.
    Returns: (complete_line, num_lines_consumed)
    """
    accumulated = src_lines[start_idx]
    paren_count = accumulated.count('(') - accumulated.count(')')
    brace_count = accumulated.count('{') - accumulated.count('}')
    bracket_count = accumulated.count('[') - accumulated.count(']')
    
    lines_consumed = 1
    idx = start_idx + 1
    
    # Continue accumulating while we have unbalanced brackets
    while (paren_count > 0 or brace_count > 0 or bracket_count > 0) and idx < len(src_lines):
        line = src_lines[idx]
        accumulated += '\n' + line
        paren_count += line.count('(') - line.count(')')
        brace_count += line.count('{') - line.count('}')
        bracket_count += line.count('[') - line.count(']')
        lines_consumed += 1
        idx += 1
    
    return accumulated, lines_consumed


def convert(func):
    #moduleloader.set_look_ahead_speedup(look_ahead_speedup)
    flag_inst = True
    func_name = func.__name__
    defaults = func.__defaults__ if func.__defaults__ else ()
    argnames = func.__code__.co_varnames[:func.__code__.co_argcount]
    default_exprs = get_default_expressions(func)
    defaults_dict = dict(zip(argnames[-len(defaults):], defaults)) if defaults else {}
    abstract_module_name = func_name[6:]
    concrete_module_name = abstract_module_name
    # Add decorated func to the list in moduleloader
    moduleloader.add_module_func(func_name)
    flag_end_inst = 0
    new_func_code = []
    inst_code = []
    # the generated verilog code.
    # python_vars_dict = kwargs
    src_lines, starting_line = inspect.getsourcelines(func)
    # n of indents in the line of function definition
    leading_line_indent = len(src_lines[1]) - len(src_lines[1].lstrip())
    src_lines = [l.rstrip() for l in src_lines]
    src_lines = [l[leading_line_indent:] for l in src_lines]
    i = 0

    # For debug
    current_gen_line = 0
    line_mapping = {}

    # lines to be optimized stored in moduleloader
    irrelevant_line_list = []

    if moduleloader.look_ahead_speedup:
        irrelevant_line_list = find_irrelevant_line_in_for_loop(func)
    # print(f"IRR: {irrelevant_line_list}")
        moduleloader.add_irrelevant_lineno(irrelevant_line_list, func_name)

    # definition of the newly generated function for producing v_declaration code
    line_func_def = f"def func_new(*args, **kwargs): \n"
    skip_until_idx = -1
    for idx, line in enumerate(src_lines):
        i = i + 1
        
        # Skip lines that were already processed as part of multi-line call
        if idx < skip_until_idx:
            continue

        # For debug: line number in the original code
        original_line_number = starting_line+i-1

        if i == 3:
            for name in argnames:
                current_gen_line += 1
                if name in defaults_dict:
                    new_func_code.append(f"    {name} = kwargs.get('{name}', {default_exprs[name]})\n")
                else:
                    new_func_code.append(f"    {name} = kwargs['{name}']\n")
            # PORTS as kwargs
            new_func_code.append(f"    PORTS=[]\n")
            new_func_code.append(f"    PORTS=kwargs['PORTS'] if 'PORTS' in kwargs.keys() else None\n")
            # new_func_code.append(f"    PORTS=kwargs['OUTMODE']\n")
            new_func_code.append(f"    abstract_module_name = '{abstract_module_name}'\n")
            new_func_code.append(' ' * 4 + 'v_declaration = []\n')
            new_func_code.append(' ' * 4 + 'v_module_name_tree = dict()\n')
            new_func_code.append(' ' * 4 + 'v_module_dict_list = []\n')
            current_gen_line += 6

        stripped_line = line.strip()
        if stripped_line.startswith("return"):
            tokens = stripped_line.split()
            if tokens[0] == "return":
                continue
        STATE = judge_state(stripped_line)
        if STATE == 'IN_PYTHON':
            # ------------------------- Comments with line number -------------------------
            new_func_code.append(f"# LINE {original_line_number}\n")
            current_gen_line += 1
            line_mapping[current_gen_line] = original_line_number
            # -----------------------------------------------------------------
            new_func_code.append(line + '\n')
        elif STATE == 'IN_VERILOG_INLINE':
            line_renew = processVerilogLine(stripped_line)
            line_renew_str = processVerilogLine_str(stripped_line)
            # ------------------------- Comments with line number -------------------------
            new_func_code.append(f"# LINE {original_line_number}\n")
            current_gen_line += 1
            # -----------------------------------------------------------------
            new_func_code.append(
                ' ' * (len(line) - len(stripped_line)) + line_renew_str + '\n')
            current_gen_line += 1
            line_mapping[current_gen_line] = original_line_number
        elif STATE == 'BEGIN_VERILOG_INST':
            flag_end_inst = 1
            inst_code.append(line + '\n')
        elif STATE == 'IN_VERILOG_INST':
            if not isVerilogLine(line):
                # Check if this is a multi-line call by checking for balanced parentheses
                stripped = line.strip()
                paren_balance = stripped.count('(') - stripped.count(')')
                brace_balance = stripped.count('{') - stripped.count('}')
                bracket_balance = stripped.count('[') - stripped.count(']')
                
                # If unbalanced, accumulate lines until balanced
                if paren_balance > 0 or brace_balance > 0 or bracket_balance > 0:
                    complete_line, lines_consumed = accumulate_complete_call(src_lines, idx)
                    skip_until_idx = idx + lines_consumed
                    line = complete_line
                
                if moduleloader.look_ahead_speedup:
                    if i in moduleloader.irrelevant_lineno_dict[func_name]:
                        line = modify_func_call(line, top_module_name=func_name, line_no=i)

                # b = isVerilogLine(line)
                inst_line_renew = processVerlog_inst_line(line)
                new_func_code.append(f"# LINE {original_line_number}\n")
                current_gen_line += 1
                # Here the following 2 lines are added
                # v_declaration_in, module_dict_tree_in, module_file_name_in = ModuleBasic(p1=10, p2=10)
                # v_module_dict_list.append(module_dict_tree_in)
                new_func_code.append(inst_line_renew)
                current_gen_line += len(inst_line_renew)

            else:
                inst_code.append(line + '\n')
            inst_code = []
        elif STATE == 'END_VERILOG_INST':
            inst_code = []
    # new_func_code.pop(0)
    # new_func_code.pop(0)
    new_func_code.insert(0, line_func_def)
    new_func_code.append("    return ''.join(v_declaration), v_module_dict_list")
    new_func_body = ''.join(new_func_code[0:])
    local_vars = {}
    # print(f"{func_name}")
    # print(new_func_body)

    # ------------------------- Compile time error control -------------------------
    if moduleloader.debug_mode:
        try:
            code_obj = compile(
                new_func_body,
                filename=f"<Generated from {func.__name__}>",
                mode="exec"
            )
            exec(code_obj, func.__globals__, local_vars)
            func_new = local_vars['func_new']
            moduleloader.module_function_definition_dict[func_name] = func_new
        except Exception as e:
            traceback.print_exc()
            error_line = getattr(e, 'lineno', None)
            # print(f"error line={error_line}")
            generated_lines = new_func_body.split('\n')
            original_line = None
            for i in range(error_line - 1, -1, -1):
                if generated_lines[i].startswith("# LINE"):
                    original_line = int(generated_lines[i].split()[2])
                    break
            # print(original_line)
            if original_line:
                original_src = inspect.getsource(func)
                original_lines = original_src.split('\n')
                adjusted_line = original_line - starting_line
                if 0 <= adjusted_line < len(original_lines):
                    error_code = original_lines[adjusted_line].strip()
                    print(f"{YELLOW}\nERROR in {func_name} (line {original_line}):{RESET}")
                    print(f"{YELLOW} Source line: {error_code}{RESET}")
                    print(f"{YELLOW}Error Type: {type(e).__name__}, Details: {str(e)}{RESET}")
                else:
                    print(f"{YELLOW}Error occurred near line {original_line} of {func_name}{RESET}")
            else:
                print(f"{YELLOW}Error in generated code of {func_name}: {str(e)}{RESET}")
            raise
    # -----------------------------------------------------------------

    else:
        exec(new_func_body, func.__globals__, local_vars)
        func_new = local_vars['func_new']
        moduleloader.module_function_definition_dict[func_name] = func_new

    # def get_modified_func(*args, **kwargs):

    def decorated(*args, **kwargs):

        flag_inst = True
        flag_optimized = False
        module_exists = False
        module_file_name_aux = str()
        top_func_name = str()
        lineno_in_top_func = 0

        time0 = time.perf_counter()
        if "OUTMODE" in kwargs.keys():
            if kwargs["OUTMODE"] == "PRINT":
                flag_inst = False
        if "LANGUAGE_MODE" in kwargs.keys():
            moduleloader.set_language_mode(kwargs["LANGUAGE_MODE"])
        if "top_module_name" in kwargs.keys():
            if kwargs['top_module_name'] and moduleloader.look_ahead_speedup:
                flag_optimized = True
                top_func_name = kwargs['top_module_name']
                lineno_in_top_func = kwargs['line_no']


        func_name = func.__name__
        func_new = moduleloader.module_function_definition_dict[func_name]

        inst_verilog_code = str()
        verilog_code = str()
        module_dict_tree = dict()
        abstract_module_name = func_name[6:]
        kwargs.pop('top_module_name',None)
        kwargs.pop('line_no', None)
        python_vars_dict = kwargs.copy()
        concrete_module_name = abstract_module_name

        if flag_optimized:
            module_exists, module_file_name_aux = moduleloader.judge_module_exists_optimized(top_func_name=top_func_name,
                                                                                             lineno=lineno_in_top_func)

        if (not flag_optimized) or (flag_optimized and not module_exists):
            module_exists, module_file_name_aux = moduleloader.judge_module_exists(abstract_module_name=abstract_module_name,
                                                         module_param_dict_in=python_vars_dict)
            if flag_optimized:
                moduleloader.add_irrelevant_aux_name_dict(top_func_name=top_func_name, lineno=lineno_in_top_func,
                                                          aux_module_file_name=module_file_name_aux)

        time1 = time.perf_counter()
        python_vars_dict = kwargs.copy()

        #print(f"{func_name}:{module_exists}")

        if not module_exists:
            # ------------------------- Run time error control -------------------------
            if moduleloader.debug_mode:
                try:
                    moduleloader.empty_irrelevant_aux_name_dict(top_func_name=func_name)
                    verilog_code, module_dict_list = func_new(*args, **kwargs)
                except Exception as e:
                    tb = sys.exc_info()[2]
                    cnt_layers = 0
                    # while tb.tb_next:
                    #     tb = tb.tb_next
                    while cnt_layers < 1:
                        tb = tb.tb_next
                        cnt_layers = cnt_layers + 1

                    error_line = tb.tb_lineno
                    # print(f"error_line={error_line}")
                    generated_lines = new_func_body.split('\n')
                    original_line = None
                    for i in range(error_line - 1, -1, -1):
                        if generated_lines[i].startswith("# LINE"):
                            original_line = int(generated_lines[i].split()[2])
                            break

                    if original_line:
                        original_src = inspect.getsource(func)
                        original_lines = original_src.split('\n')
                        adjusted_line = original_line - starting_line
                        if 0 <= adjusted_line < len(original_lines):
                            error_code = original_lines[adjusted_line].strip()
                            print(f"{YELLOW}\nERROR in {func_name} (line {original_line}):{RESET}")
                            print(f"{YELLOW} Source line: {error_code}{RESET}")
                            print(f"{YELLOW} Error Type: {type(e).__name__}, Details: {str(e)}{RESET}")
                        else:
                            print(f"{YELLOW}Error occurred near line {original_line} of {func_name}{RESET}")
                    else:
                        print(f"{YELLOW}Error in generated code of {func_name}: {str(e)}{RESET}")
                    raise
                # ------------------------- Run time error control -------------------------
            else:
                moduleloader.empty_irrelevant_aux_name_dict(top_func_name=func_name)
                verilog_code, module_dict_list = func_new(*args, **kwargs)
                moduleloader.n_func_new_enter += 1
        else:
            module_dict_list = []
            verilog_code = moduleloader.module_verilog_code[module_file_name_aux]

        if flag_inst:

            timeA = time.perf_counter()
            module_generated, module_file_name, inst_idx_str = moduleloader.generate_module(abstract_module_name,
                                                                                            python_vars_dict,
                                                                                            verilog_code,module_exists,module_file_name_aux)
            timeB = time.perf_counter()
            inst_verilog_code, module_name_tmp = instantiate_full(verilog_code, kwargs, module_file_name,
                                                                  inst_idx_str,module_exists, module_file_name_aux)
            timeC = time.perf_counter()
            module_dict_tree[module_file_name] = module_dict_list
            # moduleloader.generate_file_tree(module_dict_tree)
            # pass the instantiation information to the singleton module
            moduleloader.add_module_inst_info(inst_verilog_code, verilog_code, module_dict_tree,
                                              concrete_module_name,
                                              func_name)
            timeD = time.perf_counter()

            moduleloader.module_generation_time += (timeB-timeA)
            moduleloader.module_instantiate_time += (timeC-timeB)
            moduleloader.judge_module_exist_time += (time1-time0)
            moduleloader.add_module_inst_info_time += (timeD-timeC)

            if func_name == 'ModuleM2V':
                print(f"module generation time is {moduleloader.module_generation_time: .6f}s")
                print(f"module instantiation time is {moduleloader.module_instantiate_time: .6f}s")
                print(f"module add info time is {moduleloader.add_module_inst_info_time:.6f}s")
                print(f"judge_module_exists_time is {moduleloader.judge_module_exist_time: .6f}s")
                print(f"func_new enter time is {moduleloader.n_func_new_enter}")

        else:
            moduleloader.add_module_inst_info(inst_verilog_code, verilog_code, module_dict_tree, concrete_module_name,
                                              func_name)

    return decorated

