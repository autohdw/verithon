from functools import wraps
import inspect
import re
from functools import wraps
from inspect import getcallargs


def tokenize(text):

    tokens = re.findall(r"\S+", text)

    cleaned_text = re.sub(r"[\W_]+", " ", text)

    return cleaned_text.split()


def super_print(input_str, local):

    # tokenize the input string
    tokens = tokenize(input_str)

    for key, value in local.items():
        if key in tokens:
            input_str = re.sub(r"\b" + key + r"\b", str(value), input_str)

    print(input_str)


def isVerilogLine(line):
    pattern = "^#/"
    return bool(re.match(pattern, line))


def processVerilogLine(line):
    # remove the first 3 characters '#/'
    line = line[3:]

    # remove the leading and trailing whitespaces
    line = line.strip()

    return "super_print(' " + line + "', locals())"


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
                " " * (len(line) - len(stripped_line) - 1) + line_renew + "\n"
            )
        # if it's not verilog line, directly add to the new code
        else:
            new_func_code.append(line)

    # Reassemble the code lines to form a new function
    new_func_body = "".join(new_func_code[1:])  # 从第三行开始，因为前两行是函数定义
    # Execute newly assembled function
    local_vars = {}
    exec(new_func_body, func.__globals__, local_vars)  # 执行新函数代码
    return local_vars[func.__name__]  # 将重定义后的函数返回


@convert
def test_function(DWT1, DWT2):
    print("Start to Generate RTL Code \n")
    for i in range(3):
        #/ module M(rst,A_in,B_in,C_out)
        #/ input[DWT1 : 0] A_in
        #/ input [ DWT2 : 0] B_in
        #/ output [i : 0 ] C_out
        #/ endmodule
        continue
    print("Generating Done \n")

test_function(DWT1 = 10, DWT2=5)