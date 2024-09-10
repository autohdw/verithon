import re
import inspect

import inspect
import types


def modify_and_execute(func, *args, **kwargs):
    # 获取函数的源码
    source_code = inspect.getsource(func)

    # 修改源码，例如在函数前后添加一些打印语句
    modified_source_code = f"""
def func_new(*args, **kwargs):
    print("Before function execution")
    result = 1
    print("After function execution")
    return result
"""

    # 使用exec执行修改后的源码，定义新的函数func_new
    local_vars = {}
    G = globals()
    exec(modified_source_code, globals(), local_vars)
    func_new = local_vars['func_new']
    # 将func的参数代入func_new进行执行



# 示例函数
def example_func(a, b):
    return a + b


# 调用modify_and_execute函数
result = modify_and_execute(example_func, 1, 2)
print("Result:", result)

new_code = f'line = [] \nline.append(1)\n'
local_vars = {}
exec(new_code, globals(), local_vars)
print(local_vars['line'])
G = globals()
print(G)
